# Twisted Goodies:
# Miscellaneous add-ons and improvements to the separately maintained and
# licensed Twisted (TM) asynchronous framework. Permission to use the name was
# graciously granted by Twisted Matrix Laboratories, http://twistedmatrix.com.
#
# Copyright (C) 2007 by Edwin A. Suominen, http://www.eepatents.com
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
Unit tests for twisted_goodies.pybywire.params
"""

import scipy as s
from twisted.internet import reactor
from twisted.spread import pb

import mock, params


class Thingy(params.Parameterized):
    keyAttrs = {'a':None, 'b':2.0}
    paramNames = ('c', 'd')
    
    def func(self, x):
        key = 'foo'
        if key not in self.cache:
            self.counter = getattr(self, 'counter', 0) + 1
            self.cache[key] = self.a + self.b**2 + self.c**3 + self.d**4
        return self.cache[key] * x

class SubThingy(Thingy):
    def anotherFunc(self, x):
        return 10*x

class MetaThingy(params.Parameterized):
    keyAttrs = {'myThingy': Thingy(a=10.0, c=1, d=2)}
    paramNames = ('foo',)

    def func(self, x):
        return self.myThingy.func(x)


class Test_Parameterized_Caching(mock.TestCase):
    def setUp(self):
        self.ct = Thingy(a=1.0, b=2.0, c=3.0, d=4.0)

    def test_caches(self):
        y1 = self.ct.func(0.0)
        y2 = self.ct.func(1.0)
        self.failUnlessEqual(self.ct.counter, 1)
        self.failUnlessEqual(len(self.ct.cache), 1)
        
    def test_clearsCacheOnParamChange(self):
        y1 = self.ct.func(1.0)
        self.ct.c = 1.0
        y2 = self.ct.func(1.0)
        self.failIfEqual(y1, y2)
        self.failUnlessEqual(self.ct.counter, 2)
        self.failUnlessEqual(len(self.ct.cache), 1)

    def test_clearsCacheOnAttrChange(self):
        y1 = self.ct.func(1.0)
        self.ct.b = 1.0
        y2 = self.ct.func(1.0)
        self.failIfEqual(y1, y2)
        self.failUnlessEqual(self.ct.counter, 2)
        self.failUnlessEqual(len(self.ct.cache), 1)


class Test_Parameterized_Local(mock.TestCase):
    def setUp(self):
        self.ct = Thingy(a=1.0, b=2.0, c=3.0, d=4.0)

    def test_local_state(self):
        state = self.ct.getStateFor(None)
        # Parameterized objects have a 'name' attribute that is automatically
        # included in the state
        expectedState = {'a':1.0, 'b':2.0, 'c':3.0, 'd':4.0, 'name':None}
        self.failUnlessElementsEqual(state.keys(), expectedState.keys())
        self.failUnlessElementsEqual(state.values(), expectedState.values())


class Test_Parameterized_Remote(mock.TestCase):
    class CopyableReturner(pb.Root):
        def __init__(self, copyable):
            self.copyable = copyable
        def remote_takeMyCopy(self, thingy):
            self.copyable = thingy
        def remote_giveMeCopy(self, null):
            return self.copyable

    def getReferenceToRoot(self, root):
        self.server = reactor.listenTCP(0, pb.PBServerFactory(root))
        clientFactory = pb.PBClientFactory()
        reactor.connectTCP(
            "127.0.0.1", self.server.getHost().port, clientFactory)
        d = clientFactory.getRootObject()
        d.addCallback(lambda x: setattr(self, 'ref', x))
        return d

    def tearDown(self):
        """
        Close any client and server connections.
        """
        if hasattr(self, 'ref'):
            self.ref.broker.transport.loseConnection()
            return self.server.stopListening()

    def _checkCopy(self, result, ct, *attrNames):
        self.failIfEqual(id(result), id(ct))
        self.failUnless(isinstance(result, params.Parameterized))
        for name in attrNames:
            self.failUnlessEqual(getattr(result, name), getattr(ct, name))
        return result

    def _oops(self, failure):
            print "\nOOPS:\n%s" % failure.getTraceback()

    def test_remoteVersion_Baseclass(self):
        ct = Thingy(a=1.0, b=2.0, c=3.0, d=4.0)
        d = self.getReferenceToRoot(self.CopyableReturner(ct))
        d.addCallback(lambda _: self.ref.callRemote("giveMeCopy", ct))
        d.addErrback(self._oops)
        d.addCallback(self._checkCopy, ct, 'a')
        return d

    def test_remoteVersion_Subclass(self):
        ct = SubThingy(a=1.0, b=2.0, c=3.0, d=4.0)
        d = self.getReferenceToRoot(self.CopyableReturner(ct))
        d.addCallback(lambda _: self.ref.callRemote("giveMeCopy", ct))
        d.addErrback(self._oops)
        d.addCallback(self._checkCopy, ct, 'a')
        return d

    def test_remoteVersion_BackAndForth(self):
        ct = Thingy(a=1.0, b=2.0, c=3.0, d=4.0)
        d = self.getReferenceToRoot(self.CopyableReturner(None))
        d.addCallback(lambda _: self.ref.callRemote("takeMyCopy", ct))
        d.addCallback(lambda _: self.ref.callRemote("giveMeCopy", ct))
        d.addErrback(self._oops)
        d.addCallback(self._checkCopy, ct, 'a')
        return d

    def test_remoteVersion_Nesting(self):
        def checkSubThingy(rct):
            self.failUnlessEqual(rct.func(10), ct.func(10))
        
        ct = MetaThingy(foo='bar')
        d = self.getReferenceToRoot(self.CopyableReturner(ct))
        d.addCallback(lambda _: self.ref.callRemote("giveMeCopy", ct))
        d.addErrback(self._oops)
        d.addCallback(self._checkCopy, ct, 'foo')
        d.addCallback(checkSubThingy)
        return d

    def test_remoteVersion_Array(self):
        ct = Thingy(a=1.0, b=2.0, c=3.0)
        ct.d = s.linspace(4,5,10)
        d = self.getReferenceToRoot(self.CopyableReturner(None))
        d.addCallback(lambda _: self.ref.callRemote("takeMyCopy", ct))
        d.addCallback(lambda _: self.ref.callRemote("giveMeCopy", ct))
        d.addErrback(self._oops)
        d.addCallback(self._checkCopy, ct, 'a')
        return d
