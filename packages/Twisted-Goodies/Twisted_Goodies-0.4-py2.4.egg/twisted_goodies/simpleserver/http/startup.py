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
Populate a NameVirtualHost resource from web root subdirectories
"""

# Package imports
import os.path as ospath
import os, sre, sys
from stat import *

import zope.interface
from twisted.web2 import vhost, resource, static, iweb

import util


class VHostRoot(resource.Resource):
    """
    I am a twisted.web2 root resource object for a virtual host
    """
    addSlash = False
    _vhostRoots = {}
    
    def __init__(self, dirPath):
        """
        I am instantiated with the path of a subdirectory for my very own
        virtual host.
        """
        self._dirPath = dirPath
        resource.Resource.__init__(self)

    def locateChild(self, request, segments):
        """
        Forces traversal to occur through the B{real} root resource for my
        virtual host, generating that resource if necessary and caching it for
        further use.
        """
        realRoot = self._vhostRoots.setdefault(
            self._dirPath, self._getVhostRoot())
        return realRoot, segments

    def _getVhostRoot(self):
        """
        Returns my real root resource. It is either

            - an instance of a class named 'Resource'found in the module of a
              special package I've managed to import from my vhost's
              subdirectory, where the class implements
              L{twisted.web2.iweb.IResource}
        
            - simply an instance of L{twisted.web2.static.File} serving my
              vhost's subdirectory contents.
              
        """
        indexPath = ospath.join(self._dirPath, "index.py")
        if ospath.exists(indexPath):
            try:
                sys.path.insert(0, self._dirPath)
                namespace = {}
                execfile(indexPath, namespace)
                sys.path.pop(0)
            except:
                return util.showException()
            else:
                # Successfully executed the 'index' python file...
                RClass = namespace.get('Resource', None)
                if iweb.IResource in zope.interface.implementedBy(RClass):
                    # and it has a 'Resource' class that implements IResource,
                    # so assign an instance of that class as the root resource
                    return RClass(self._dirPath)
        # If there hasn't been a successful dynamic resource assignment, do the
        # fallback operation of assigning the subdirectory's static contents
        return static.File(self._dirPath)


class VHostSiteRoot(vhost.NameVirtualHost):
    """
    I am a twisted.web2 root resource object that populates myself with root
    resources of virtual hosts based on the structure of the supplied
    I{wwwPath} directory.

    Each subdirectory with a legal hostname is given a virtual host root
    resource object:
    
        - If the subdirectory contain a file index.py, I attempt to import that
          file as a python module whose name is unimportant. If the import
          succeeds and the imported module's namespace includes an object
          C{resource} that implements L{twisted.web2.iweb.IResource}, that
          object is assigned as the root resource of the virtual host for the
          subdirectory.

        - Otherwise, the contents of the directory are served statically using
          an instance of L{twisted.web2.static.File}.

    A hostname must be provided to my constructor that corresponds to a
    directory meeting these requirements. It is assigned to the host default.
    """
    reAlpha = sre.compile(
        r"localhost|^[a-z][a-z0-9\-]+\.[a-z][a-z0-9\-\.]+$")
    reNum = sre.compile(
        r"^([0-9]{1,3}\.){3}[0-9]{1,3}")

    def __init__(self, wwwPath, defaultHost):
        self.wwwPath = wwwPath
        defaultPath = os.path.join(wwwPath, defaultHost)
        if not os.path.isdir(defaultPath):
            raise ValueError(
                "No subdir present for default host '%s'" % defaultHost)
        defaultResource = VHostRoot(defaultPath)
        vhost.NameVirtualHost.__init__(self, defaultResource)
        for dirName, dirPath in self._hostSubdirGenerator(defaultPath):
            self.addHost(dirName, VHostRoot(dirPath))

    def _hostSubdirGenerator(self, *ignored):
        """
        Yields the name and path of each vhost-qualified subdirectory in my
        root path. To qualify, the subdirectory name must
        
            - begin with a lowercase letter and be either 'localhost' or be
              followed by lowercase letters, hyphens, and/or numbers, a period,
              and more of the same (interspersed periods in the part after the
              first period, i.e., subdomains, are OK), or 

            - be a dotted-quad IP address

        """
        for dirName in os.listdir(self.wwwPath):
            dirPath = ospath.join(self.wwwPath, dirName)
            if dirPath in ignored:
                continue
            if not os.path.isdir(dirPath):
                continue
            if self.reAlpha.search(dirName) or self.reNum.search(dirName):
                yield dirName, dirPath

