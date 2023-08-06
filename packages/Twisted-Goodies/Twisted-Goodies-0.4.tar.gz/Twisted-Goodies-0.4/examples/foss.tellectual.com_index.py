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
This file is what defines the root resource for U{foss.eepatents.com}, my free
& open source projects site. A L{resources.WSGIResource} is used to provide
access to Trac via an WSGI gateway.
"""

import os.path
from textwrap import TextWrapper
from twisted.web2 import static
from twisted.python.log import msg as log

from twisted_goodies.simpleserver.http.resources import \
     T, StanResource, DownloadResource, APIDocResource, TracResource


TRAC_DIR = '/var/trac/foss'
PROJECTS = (
    ("AsynCluster",
     """
     Asynchronous operation of a computing cluster with a Node Display
     Manager (NDM) that allows regular workstation usage of cluster
     nodes with computing jobs running behind the scenes. Includes
     evolutionary computing tools that make use of the asynchronous
     node processing.
     """),

    ("AsynQueue",
     """
     Asynchronous task queueing based on the Twisted framework, with task
     prioritization and a powerful worker/manager interface.
     """),

    ("sAsync",
     """
     SQLAlchemy done asynchronously, with enhancements like persistent
     dictionaries, arrays, and graphs, all based on an access broker
     that conveniently manages database access, table setup, and
     deferred transactions.
     """),

    ("Twisted-Goodies",
     """
     Miscellaneous add-ons and improvements to the separately
     maintained and licensed Twisted framework, including asynchronous
     task queueing, HTTP fetching, and simple HTTP and POP3 servers.
     """
     ),

    ("WinDictator",
     """
     Gives desktop users of the GNU/Linux operating system a
     convenient way to make use of speech recognition software that
     runs only under the Microsoft Windows operating system. Your
     dictation software runs on a separate computer (virtual or real)
     that is networked to your Linux- based desktop. Keystrokes of
     dictated text are transmitted via a TCP connection and entered
     via faked X events.
     """),
    )


class DisabledResource(StanResource):
    addSlash = False

    def __init__(self, whatDisabled):
        self.whatDisabled = whatDisabled
        self.title = "%s Temporarily Disabled" % whatDisabled

    def render(self, request):
        return [
            T.h2[self.title],
            T.p["Hopefully this should be fixed soon."]]


class Resource(StanResource):
    """
    A home page for all of the trac project names and paths supplied in the
    I{projects} dict
    """
    addSlash = True
    wrapper = TextWrapper(break_long_words=False)
    projectURLProto = "/trac/%s/wiki"
    projectRepoProto = "/foss/projects/%s/trunk"
    
    def __init__(self, vhostPath):
        self.vhostPath = vhostPath
        self.apiDocResource = APIDocResource(
            vhostPath, self.projectURLProto,
            "file:///var/svn" + self.projectRepoProto)
        self.downloadResource = DownloadResource(
            vhostPath, self.projectURLProto,
            "svn://foss.eepatents.com" + self.projectRepoProto)            
        self.title = "Ed Suominen's Free & Open Source Software Projects"
        self.style = {
            "row":\
            {'padding':'0.3em',
             'margin-bottom':'1em',
             'margin-left':'0.5em',
             'margin-right':'2em',
             'background-color':'#FFFFC0'},

            "project_link":\
            {'font-size':'larger',
             'font-style':'bold',
             'margin-bottom':'2px'},
            
            "project_description":{'margin':'2px'},
            "header":{'margin':'0.5em'},
            "footer":{'font-style':'oblique', 'margin-top':'0.5em'}
            }
        env = {
            'mod_python.subprocess_env':\
            {'PYTHON_EGG_CACHE': os.path.join(TRAC_DIR, 'python-eggs')}}
        self.tr = TracResource(TRAC_DIR, env)

    def _possibleStatic(self, *pathParts):
        """
        """
        staticPath = os.path.join(self.vhostPath, *pathParts)
        if os.path.exists(staticPath):
            return static.File(staticPath)

    def render(self, request):
        """
        Returns the body of my home page HTML.
        """
        body = [T.img(src='/banner.png', alt=self.title), self.header(), T.hr]
        for projectName, doc in PROJECTS:
            projectDescription = " ".join(
                [x.strip() for x in doc.strip().split("\n")])
            href = self.projectURLProto % projectName
            projectDiv = [
                T.a(id="project_link", href=href)[projectName]]
            projectDiv.append(
                T.p(id="project_description")[projectDescription])
            body.append(T.div(id="row")[projectDiv])
        body.extend([T.hr, self.footer()])
        return body

    def header(self):
        contents = [
            "Built on the ",
            T.a(href='http://python.org')["Python"],
            " object-oriented programming language and the ",
            T.a(href='http://twistedmatrix.com')["Twisted"],
            " asynchronous processing framework."
            ]
        return T.p(id="header")[contents]

    def footer(self):
        contents = """
        The software featured here is licensed under the <a
        href="http://www.gnu.org/licenses/gpl.html">
        GNU Public License</a>, which permits you to use it freely but requires
        that you accept the complete lack of <strong>any warranty</strong>, and
        agree to make whatever software you build with it equally free. If you
        want to use this software under different terms, <span
        style="font-style:normal">e.g.</span>, with a commercial license to put
        it under wraps in a proprietary product, feel free to contact me about
        it. Commercial licenses are available, for the most part, and in use.
        """
        return T.p(id="footer")[self.html(contents)]

    def locateChild(self, request, segments):
        """
        Returns either a Trac WSGI resource or a static file in my
        vhost subdirectory.
        """
        root = segments[0]
        if not root:
            return self, ()
        if root == 'trac':
            return self.tracChild(request, segments[1:])
        if root in [x[0] for x in PROJECTS]:
            return self.tracChild(request, segments)
        return static.File(os.path.join(self.vhostPath, *segments)), ()

    def tracChild(self, request, segments):
        """
        Returns a resource within a trac project path. If a file is available
        in a corresponding path from the subdirectory 'trac', a static file
        resource to it is returned instead of a TracResource.
        """
        def rootState(segmentList):
            root = segmentList[0]
            if len(segmentList) == 1:
                return root, True
            if len(segmentList) == 2 and segmentList[1] == '':
                del segmentList[1]
                return root, True
            return root, False

        def listOp(methodName, *args):
            uriList = request.uri.split("/")
            k = len(uriList) - len(segments)
            uriPreList, uriPostList = uriList[:k], uriList[k:]
            for thisList in (request.postpath, subSegments, uriPostList):
                getattr(thisList, methodName)(*args)
            request.uri = "/".join(uriPreList + uriPostList)

        projectName, subSegments = segments[0], list(segments[1:])
        if subSegments and not subSegments[-1]:
            listOp('pop')
        if not subSegments:
            listOp('append', 'wiki')
        root, isAtRoot = rootState(subSegments)
        if False and root == 'changeset':
            # TODO, hopefully won't need to keep trying this for long
            return DisabledResource("Changeset Listings"), ()
        if root == 'wiki' and len(subSegments) > 1:
            subRoot = subSegments[1]
            if subRoot.isalpha() and subRoot.islower():
                listOp('remove', 'wiki')
                root = subRoot
        if root == 'api':
            return self.apiDocResource, [projectName] + subSegments[1:]
        if root == 'download':
            return self.downloadResource, [projectName] + subSegments[1:]
        if isAtRoot:
            if root == 'wiki':
                listOp('append', "Start_%s" % projectName)
            elif root == 'browser':
                listOp('extend', ['projects', projectName, 'trunk'])
        possibleResult = self._possibleStatic('trac', *subSegments)
        if possibleResult:
            return possibleResult, ()
        return self.tr, subSegments
