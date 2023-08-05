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
Unit tests for master.control
"""

from twisted.internet import defer
from twisted.python import failure
from twisted.trial.unittest import TestCase

import mock
import control


class TestSessionManager(TestCase):
    def setUp(self):
        control.SessionManager.usersActive = {}
        self.sm = self._getTestableSM()

    def _getTestableSM(self):
        def testableInit(self):
            self.ctl = mock.Control()
            self.sessionMap = {}
            self.t = mock.UserDataTransactor()
        
        TestableSessionManager = control.SessionManager
        TestableSessionManager.__init__ = testableInit
        return TestableSessionManager()

    def _setupViewBegin(self, timeRemaining=0.4):
        nodeID, userID, password  = 123, 'alpha', 'bravo'
        self.node = mock.Perspective(nodeID, userID)
        self.sm.t.setUp(userID, password, timeRemaining)

    def testViewBeginOK(self):
        self._setupViewBegin()
        d = self.sm.view_begin(self.node, 'alpha', 'bravo')
        d.addCallback(self.failUnlessEqual, True)
        return d

    def testViewBeginBadUser(self):
        self._setupViewBegin()
        d = self.sm.view_begin(self.node, 'X', 'bravo')
        d.addCallback(self.failUnlessEqual, False)
        return d

    def testViewBeginBadPassword(self):
        self._setupViewBegin()
        d = self.sm.view_begin(self.node, 'alpha', 'X')
        d.addCallback(self.failUnlessEqual, False)
        return d

    def testViewBeginNoTime(self):
        self._setupViewBegin(0.0)
        d = self.sm.view_begin(self.node, 'alpha', 'bravo')
        d.addCallback(self.failUnlessEqual, False)
        return d

    def testViewBeginAlreadyActive(self):
        def tryDupe(null):
            nodeID = 125,
            node2 = mock.Perspective(nodeID, 'alpha')
            d = defer.maybeDeferred(
                self.sm.view_begin, node2, 'alpha', 'bravo')
            d.addCallback(self.failUnlessEqual, False)
            return d
            
        self._setupViewBegin()
        d = defer.maybeDeferred(
            self.sm.view_begin, self.node, 'alpha', 'bravo')
        d.addCallback(self.failUnlessEqual, True)
        d.addCallback(tryDupe)
        return d


class TestController(TestCase):
    def setUp(self):
        def testableInit(self):
            self.nodes = {}
            self.jobber = mock.JobManager()
        
        TestableController = control.Controller
        TestableController.__init__ = testableInit
        self.ctl = TestableController()

    def testAttachNode(self):
        expectedID = 1
        node = mock.Perspective(123, 'user')
        root = mock.Root(None)
        
        def checkAttached(null):
            self.failUnless(expectedID in self.ctl.nodes)
            self.failUnlessEqual(
                self.ctl.jobber.attached.get(expectedID, None), root)
            
        d = self.ctl.attachNode(node, root)
        d.addCallback(self.failUnlessEqual, expectedID)
        d.addCallback(checkAttached)
        return d

    def testNodeRemote(self):
        node = mock.Perspective(123, 'user')
        root = mock.Root(None)

        def gotID(nodeID):
            self._nodeID = nodeID
            return nodeID

        def checkCalled(result, president):
            self.failUnlessEqual(result, None)
            callInfo = root.calls.pop()
            self.failUnlessEqual(callInfo['called'], 'message')
            self.failUnlessEqual(callInfo['args'], (president,))
        
        d = self.ctl.attachNode(node, root)
        d.addCallback(gotID)
        president = "Abe Lincoln"
        d.addCallback(self.ctl.nodeRemote, 'message', president)
        d.addCallback(checkCalled, president)
        president = "Al Hamilton"
        d.addCallback(
            lambda _: self.ctl.nodeRemote(self._nodeID, 'message', president))
        d.addCallback(
            lambda _: self.ctl.nodeRemote(666, 'message', president))
        d.addBoth(
            lambda result: self.failUnless(
            isinstance(result, failure.Failure)))
        return d

    def testUserRemote(self):
        node = mock.Perspective(123, 'joeblow123')
        root = mock.Root(None)

        def checkCalled(result, president):
            self.failUnlessEqual(result, None)
            callInfo = root.calls.pop()
            self.failUnlessEqual(callInfo['called'], 'message')
            self.failUnlessEqual(callInfo['args'], (president,))

        d = self.ctl.attachNode(node, root)
        president = "Abe Lincoln"
        d.addCallback(
            lambda _: self.ctl.userRemote('joeblow123', 'message', president))
        d.addCallback(checkCalled, president)
        president = "Al Hamilton"
        d.addCallback(
            lambda _: self.ctl.userRemote('bogus', 'message', president))
        d.addBoth(
            lambda result: self.failUnless(
            isinstance(result, failure.Failure)))
        return d

    def testNodeRemoteAfterDetaching(self):
        node = mock.Perspective(123, 'user')
        root = mock.Root(None)

        def gotID(nodeID):
            self._nodeID = nodeID
            return nodeID

        def checkCalled(result, president):
            self.failUnlessEqual(result, None)
            callInfo = root.calls.pop()
            self.failUnlessEqual(callInfo['called'], 'message')
            self.failUnlessEqual(callInfo['args'], (president,))
        
        d = self.ctl.attachNode(node, root)
        d.addCallback(gotID)
        president = "Abe Lincoln"
        d.addCallback(self.ctl.nodeRemote, 'message', president)
        d.addCallback(checkCalled, president)
        self.ctl.detachNode(self._nodeID)
        d.addCallback(
            lambda _: self.ctl.nodeRemote(self._nodeID, 'message', president))
        d.addBoth(
            lambda result: self.failUnless(
            isinstance(result, failure.Failure)))
        return d
    
        
