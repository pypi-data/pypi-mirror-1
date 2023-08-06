# Twisted Goodies:
# Miscellaneous add-ons and improvements to the separately maintained and
# licensed Twisted (TM) asynchronous framework. Permission to use the name was
# graciously granted by Twisted Matrix Laboratories, http://twistedmatrix.com.
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
Unit tests for twisted_goodies.simpleserver.http.resources.projects
"""

import os, os.path, shutil, tempfile
from twisted.trial.unittest import TestCase

import projects


class BaseTC(TestCase):
    def _get_vhostPath(self):
        if not hasattr(self, '_vhostPath'):
            self._vhostPath = "test.com"
            self.dirs = []
            self.mkdir()
        return self._vhostPath
    vhostPath = property(_get_vhostPath)
    
    def mkdir(self, *pathParts):
        dirPath = os.path.join(self.vhostPath, *pathParts)
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            self.dirs.append(dirPath)
        return dirPath

    def tearDown(self):
        dirs = getattr(self, 'dirs', [])
        while dirs:
            dirPath = dirs.pop()
            if os.path.exists(dirPath):
                shutil.rmtree(dirPath)
            

class Test_APIDocResource(BaseTC):
    def setUp(self):
        self.projectURLProto = "/trac/%s/wiki"
        self.projectRepoProto = "svn://tellectual.com/foss/projects/%s/trunk"
        self.rsrc = projects.APIDocResource(
            self.vhostPath, self.projectURLProto, self.projectRepoProto)

    def test_svnRev(self):
        def gotRev(rev):
            self.failUnless(rev.isdigit())
            self.failUnless(int(rev) >= 63)
        
        return self.rsrc.svnRev("Twisted-Goodies").addCallback(gotRev)

    def test_svnExport(self):
        def done(errCode):
            self.failUnlessEqual(errCode, 0)
            self.failUnless('twisted_goodies' in os.listdir(tmpDir))
        
        tmpDir = self.mkdir("tmp")
        return self.rsrc.svnExport(tmpDir, "Twisted-Goodies").addCallback(done)

    def test_pydoctor(self):
        def done(errCode):
            # pydoctor complains a lot
            # self.failUnlessEqual(errCode, 0)
            apiSubDir = os.path.join(apiDir, "Twisted-Goodies")
            self.failUnless('twisted_goodies.html' in os.listdir(apiSubDir))
        
        apiDir = self.mkdir("api")
        tmpDir = self.mkdir("tmp")
        d = self.rsrc.svnExport(tmpDir, "Twisted-Goodies")
        d.addCallback(lambda _: self.rsrc.pydoctor(tmpDir, "Twisted-Goodies"))
        d.addCallback(done)
        return d
        
