# Node Display Manager (NDM):
# A simple X display manager for cluster nodes that also serve as
# access-restricted workstations. An NDM client runs on each node and
# communicates via Twisted's Perspective Broker to a master NDM server, which
# regulates when and how much each user can use his account on any of the
# workstations. The NDM server also dispatches cluster operations to the nodes
# via the NDM clients, unbeknownst to the workstation users.
#
# Copyright (C) 2006 by Edwin A. Suominen, http://www.eepatents.com
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
Unit tests for twisted_goodies.misc
"""

from zope.interface import Interface, implements
from twisted.trial.unittest import TestCase
from twisted.spread import pb

import misc


class IMockAlpha(Interface):
    pass

class IMockBravo(Interface):
    pass

class MockAlphaPerspective(object):
    implements(IMockAlpha)
    
class MockBravoPerspective(object):
    implements(IMockBravo)



class TestAddressRestrictorMixin(TestCase):
    baseTests = {
        ('127.0.0.1',2130706433):       (('127.0.0.5', (8,16,20,24,25)),
                                         ('127.1.2.3', (8,))),
        
        ('216.27.61.137',3625663881):   (('216.27.61.254', (8,16,20,24,25)),
                                         ('216.27.61.1', (8,16,20,24))),
        
        ('192.15.28.16',3222215696):    (('192.168.1.16', (8,)),
                                         ('192.15.26.0', (8,16,20)))
        }
    
    def setUp(self):
        self.arm = misc.AddressRestrictorMixin()

    def testAddSubnet(self):
        """
        Test whether C{addSubnet} can be used to add one, then multiple
        subnets for acceptance of addresses.
        """
        self.fail()

    def testQuadToInt(self):
        """
        Test whether C{_quadToInt} converts dotted-quad IP addresses to
        integers.
        """
        for quadAddr, intAddr in self.baseTests.iterkeys():
            self.failUnlessEqual(self.arm._quadToInt(quadAddr), intAddr)
    
    def testSingleSubnetTester(self):
        """
        Test whether addresses desirably match or fail to match particular
        subnets.
        """
        for baseTuple, tests in self.baseTests.iteritems():
            base = baseTuple[1]
            for addr, subnetBits in tests:
                for bits in (8,16,20,24,25):
                    self.arm._subnets = [(base, bits)]
                    desiredResult = (bits in subnetBits)
                    msg = "Matching %s against %s/%d must be '%s'" % \
                          (addr, baseTuple[0], bits, desiredResult)
                    self.failUnlessEqual(
                        desiredResult, self.arm.testAddress(addr), msg)

    def testMultipleSubnetTester(self):
        """
        Test whether addresses desirably match or fail to match particular
        combinations of subnets.
        """
        self.fail()


class TestPerspectiveFactory(TestCase):
    def setUp(self):
        interfaceMap = {
            'alpha':   (IMockAlpha,),
            'bravo':   (IMockBravo,),
            'charlie': (IMockAlpha, IMockBravo)
            }
        perspectiveList = [MockAlphaPerspective, MockBravoPerspective]
        self.pf = misc.PerspectiveFactory(interfaceMap, perspectiveList)

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
