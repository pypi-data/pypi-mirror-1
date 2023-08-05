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
Unit tests for twisted_goodies.asyncluster.master.nodes
"""

from twisted.internet import reactor
from twisted.cred import checkers, credentials
from twisted.spread import pb
from twisted.trial.unittest import TestCase

import mock
import nodes


class TestPerspective(TestCase):
    def setUp(self):
        self.ctl = mock.Control()
        self.p = nodes.Perspective(self.ctl)

    def testAttachedOK(self):
        def checkResult(result):
            self.failUnless(isinstance(result, tuple))
            self.failUnlessEqual(getattr(self.p, 'ID', None), mock.NODE_ID)
            self.failUnless(self.ctl.attached)
            result[-1]()
            self.failIf(self.ctl.attached)
        
        mockRoot = mock.Root(mock.SERVER_PASSWORD)
        d = self.p.attached(mockRoot)
        d.addCallback(checkResult)
        return d

    def testAttachedBogus(self):
        def checkResult(result):
            self.failUnless(isinstance(result, tuple))
            self.failIf(hasattr(self.p, 'ID'))
            self.failIf(self.ctl.attached)
        
        mockRoot = mock.Root('bogus')
        d = self.p.attached(mockRoot)
        d.addCallback(checkResult)
        return d

    def testDetached(self):
        self.p.ID = 234
        self.p.detached()
        self.failIf(hasattr(self.p, 'ID'))
        self.failIf(self.ctl.attached)


class TestServerFactory(TestCase):
    def setUp(self):
        self.ctl = mock.Control()
        checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(foo='bar')
        self.f = nodes.ServerFactory(self.ctl, checker=checker)
    
    def testConstructor(self):
        self.failUnlessEqual(self.f._subnets[1], (3222215690, 24))

    def testConnectionFromGoodAddress(self):
        """
        Test whether a TCP server using the factory accepts a connection from a
        good IP address and starts the necessary handshaking.
        """
        def connected(result, listener):
            self.failIf(self.ctl.attached is None)
            self.failUnlessEqual(
                self.client.clientRoot.password, mock.SERVER_PASSWORD)
            self.client.disconnect()
            return listener.stopListening()
        
        self.client = mock.Client()
        listener = reactor.listenTCP(
            mock.TCP_PORT, self.f, interface='127.0.0.1')
        d = self.client.connect()
        d.addCallback(connected, listener)
        return d
    
    def testLogin(self):
        """
        Test whether we can connect and login to a TCP server using the
        factory.
        """
        def login():
            credential = credentials.UsernamePassword('foo', 'bar')
            d = self.client.factory.login(credential, self.client.clientRoot)
            d.addCallback(loggedIn)
            return d

        def loggedIn(perspective):
            d = perspective.callRemote('getSessionManager')
            d.addCallback(gotManager)
            return d

        def gotManager(mgr):
            d = mgr.callRemote('begin', 'alpha', 'bravo')
            d.addCallback(self.failUnlessEqual, 2.0)
            return d

        def done(listener):
            self.client.disconnect()
            return listener.stopListening()
        
        self.client = mock.Client()
        listener = reactor.listenTCP(
            mock.TCP_PORT, self.f, interface='127.0.0.1')
        d = self.client.connect()
        d.addCallback(lambda _: login())
        d.addCallback(lambda _: done(listener))
        return d
