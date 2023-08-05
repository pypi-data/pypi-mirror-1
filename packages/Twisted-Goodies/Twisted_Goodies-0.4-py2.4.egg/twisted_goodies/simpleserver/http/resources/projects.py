# twisted_goodies.simpleserver.http:
# A virtual hosting twisted.web2 HTTP server that uses subdirectories for
# virtual host content. Subdirectories can be python packages providing dynamic
# content with a root resource object, or sources of static content.
#
# Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

"""
Resources for web sites hosting FOSS projects
"""

import tempfile, shutil, os, os.path, re, dircache
from twisted.internet import defer, utils
from twisted.python import procutils
from twisted.web2 import static
from twisted.web2.resource import Resource, RedirectResource

from basic import T, StanResource


class Mixin(object):
    def __init__(self, vhostPath, projectURLProto, projectRepoProto):
        self.vhostPath = os.path.realpath(vhostPath)
        for name in ('projectURLProto', 'projectRepoProto'):
            string = locals()[name]
            if "%s" not in string:
                raise ValueError("Invalid string prototype '%s'" % string)
            setattr(self, name, string)
    

class APIDocResource(Mixin, Resource):
    """
    I provide Web access to generated API documentation for projects hosted
    within a particular I{vhostPath}.
    """
    re_rev = re.compile(r"Revision:\s+(\d+)")

    def _executable(self, name):
        result = procutils.which(name)[0]
        if not result:
            raise ImportError("Can't locate %s executable" % name)
        return result

    def _packageName(self, projectName):
        return projectName.lower().replace("-", "_")

    def _repo(self, projectName):
        repo = self.projectRepoProto % projectName
        return os.path.join(repo, self._packageName(projectName))

    def locateChild(self, request, segments):
        """
        Returns a (deferred) instance of L{RedirectResource} that points to a
        particular HTML file containing generated API documentation. If the
        documentation does not yet exist or is out of date, it will be
        (re)generated before the deferred fires.
        """
        def ready(null):
            urlPath = "/api/%s/%s" % (projectName, apiFile)
            newURL = (request.scheme, request.host, urlPath, '', '', '')
            return RedirectResource(*newURL), ()

        print "APIDocResource", segments
        projectName = segments[0]
        if len(segments) > 1:
            apiFile = segments[1]
        else:
            apiFile = "%s.html" % self._packageName(projectName)
        d = defer.maybeDeferred(
            self.ensureDocsPresent, projectName, apiFile)
        d.addCallback(ready)
        return d

    def ensureDocsPresent(self, projectName, apiFile):
        """
        If the specified I{apiFile} for the project I{projectName} does not
        exist or is out of date, corrects the situation and returns a deferred
        that fires when done.  Otherwise, returns nothing.
        """
        def lastRev(rev=None):
            if rev is None:
                if not os.path.exists(revFile):
                    return
                fh = open(revFile)
                rev = fh.readline().strip()
            else:
                revDir = os.path.dirname(revFile)
                if not os.path.exists(revDir):
                    os.makedirs(revDir)
                fh = open(revFile, 'w')
                fh.write(str(rev))
            fh.close()
            return rev
        
        def compareRevs(currentRev):
            if currentRev != lastRev():
                # Tell the world that the docs are at the new rev...
                lastRev(currentRev)
                # ...then make good on that (just once)
                tmpDir = tempfile.mkdtemp()
                d = self.svnExport(tmpDir, projectName)
                d.addCallback(lambda _: self.pydoctor(tmpDir, projectName))
                d.addCallback(lambda _: shutil.rmtree(tmpDir))
                return d

        revFile = os.path.join(self.vhostPath, 'api', projectName, 'REV')
        return self.svnRev(projectName).addCallback(compareRevs)

    def svnRev(self, projectName):
        """
        Returns a deferred that fires with the current revision of the
        I{projectName} project in the SVN repo, i.e., the revision of the
        newest file found from a recursive info command. The revision number is
        provided as a string.
        """
        def gotInfo(info):
            maxRev = 0
            for line in [x.strip() for x in info.split("\n")]:
                match = self.re_rev.match(line)
                if match:
                    thisRev = int(match.group(1))
                    maxRev = max([maxRev, thisRev])
            return str(maxRev)
        
        args = ["info", "-R", self._repo(projectName)]
        d = utils.getProcessOutput(self._executable('svn'), args=args)
        d.addCallback(gotInfo)
        return d

    def svnExport(self, tmpDir, projectName):
        """
        Exports to the specified I{tmpDir} a copy of the SVN repo for the
        I{projectName} project. Returns a deferred that fires when the export
        is done.
        """
        repo = self._repo(projectName)
        packageDir = os.path.realpath(
            os.path.join(tmpDir, self._packageName(projectName)))
        args = ["export", "-q", "--force", repo, packageDir]
        return utils.getProcessValue(self._executable('svn'), args=args)

    def pydoctor(self, tmpDir, projectName):
        """
        Generates API documentation for the package corresponding to the
        specified I{projectName}, which must be present in a specified
        I{tmpDir}. The resulting HTML documents will appear in a subdirectory
        C{api/<projectName>} of my vhost path after the returned deferred fires.
        """
        url = self.projectURLProto % projectName
        args = [
            "--make-html",
            "--project-name=%s" % projectName,
            "--add-package=%s" % self._packageName(projectName),
            "--html-output=%s/api/%s" % (self.vhostPath, projectName),
            "--project-url=%s" % url]
        return utils.getProcessValue(
            self._executable('pydoctor'), args=args, path=tmpDir)


class DownloadResource(Mixin, StanResource):
    """
    I provide a page of HTML that shows the different ways to download projects
    hosted within a particular I{vhostPath}.
    """
    downloadURLProto = "/download/%s"
    downloadExtensions = ('.egg', '.zip', '.exe', '.gz', '.bz2')
    style = {
        "H1":\
        {'margin-bottom':'0px'},

        "H2":\
        {'margin-bottom':'0px'},
        
        "code":\
        {'padding':'0.3em',
         'margin-left':'0.5em',
         'font-size':'larger',
         'font-style':'bold',
         'font-family':'monospace'}
        }

    def _pertinentFiles(self):
        downloadDir = os.path.join(self.vhostPath, 'download')
        listing = []
        for fileName in dircache.listdir(downloadDir):
            if not fileName.startswith(self.projectName):
                continue
            listing.append(fileName)
        return downloadDir, listing

    def _sectionEasyInstall(self):
        if "%s.ez_setup" % self.projectName in self._pertinentFiles()[1]:
            return [
                T.h2["Setup Tools (the easiest way)"],
                T.p(id="code")["easy_install %s" % self.projectName]]
        return []

    def _sectionSVN(self):
        url = self.projectRepoProto % self.projectName
        return [
            T.h2["SVN Checkout"],
            T.p(id="code")["svn co %s %s" % (url, self.projectName)],
            T.p["The current source code (\"trunk\") will appear in the " +\
                "\"%s\" subdirectory. " % self.projectName +\
                "You can go there and install with"],
            T.p(id="code")["sudo python setup.py install"]]
        
    def _sectionInstallFiles(self):
        listing = []
        for fileName in self._pertinentFiles()[1]:
            if os.path.splitext(fileName)[1] in self.downloadExtensions:
                href = self.downloadURLProto % fileName
                item = T.li[T.a(href=href)[fileName]]
                listing.append(item)
        if not listing:
            return []
        return [
            T.h2["Install Files"],
            T.p["You can download one of the following files and use it to " +\
                "install %s, either by " % self.projectName +\
                "executing them (for Windows "+\
                "\".exe\" files) or extracting their archived files and "+\
                "using the setup.py script."],
            T.ul[listing]]

    def render(self, request):
        """
        Returns the body of my HTML.
        """
        msg = "There are a couple of different ways to get up and running "+\
              "with a copy of %s:" % self.projectName
        body  = [T.img(src='/banner.png'), T.hr, T.h1[self.title], T.p[msg]]
        body += self._sectionEasyInstall()
        body += self._sectionSVN()
        body += self._sectionInstallFiles()
        href = self.projectURLProto % self.projectName
        body += [T.hr, T.a(href=href)["Back to Project Page"]]
        return body

    def locateChild(self, request, segments):
        print "DownloadResource", segments
        self.projectName = segments[0]
        self.title = "Downloading %s" % self.projectName
        if len(segments) > 1:
            downloadDir, downloadFiles = self._pertinentFiles()
            if segments[1] in downloadFiles:
                filePath = os.path.join(downloadDir, segments[1])
                return static.File(filePath), ()
        return self, ()
