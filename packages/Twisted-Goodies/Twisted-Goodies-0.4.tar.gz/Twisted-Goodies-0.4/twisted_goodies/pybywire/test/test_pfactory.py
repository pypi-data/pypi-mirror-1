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
Unit tests for twisted_goodies.pybywire.pfactory
"""

from zope.interface import Interface, implements
from twisted.trial.unittest import TestCase
from twisted.spread import pb

import pfactory


class IMockAlpha(Interface):
    pass

class IMockBravo(Interface):
    pass

class MockAlphaPerspective(object):
    implements(IMockAlpha)
    
class MockBravoPerspective(object):
    implements(IMockBravo)


class TestPerspectiveFactory(TestCase):
    def setUp(self):
        interfaceMap = {
            'alpha':   (IMockAlpha,),
            'bravo':   (IMockBravo,),
            'charlie': (IMockAlpha, IMockBravo)
            }
        perspectiveList = [MockAlphaPerspective, MockBravoPerspective]
        self.pf = pfactory.PerspectiveFactory(interfaceMap, perspectiveList)

    def test_implementor(self):
        result = self.pf.implementor(IMockAlpha)
        self.failUnlessEqual(result, MockAlphaPerspective)
        result = self.pf.implementor(IMockBravo)
        self.failUnlessEqual(result, MockBravoPerspective)

    def test_perspective_one(self):
        p = self.pf.perspective(['alpha'])
        self.failUnless(isinstance(p, pb.Avatar))
        self.failUnless(isinstance(p, MockAlphaPerspective))
        self.failIf(isinstance(p, MockBravoPerspective))
        p = self.pf.perspective(['bravo'])
        self.failUnless(isinstance(p, pb.Avatar))
        self.failIf(isinstance(p, MockAlphaPerspective))
        self.failUnless(isinstance(p, MockBravoPerspective))
                                          
    def test_perspective_two(self):
        p = self.pf.perspective(['alpha', 'bravo'])
        self.failUnless(isinstance(p, pb.Avatar))
        self.failUnless(isinstance(p, MockAlphaPerspective))
        self.failUnless(isinstance(p, MockBravoPerspective))

    def test_perspective_both(self):
        p = self.pf.perspective(['charlie'])
        self.failUnless(isinstance(p, pb.Avatar))
        self.failUnless(isinstance(p, MockAlphaPerspective))
        self.failUnless(isinstance(p, MockBravoPerspective))
