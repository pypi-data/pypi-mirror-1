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
Miscellaneous goodies
"""

import struct, socket, new, sys
from twisted.internet import interfaces, defer


class DeferredTracker(object):
    """
    I allow you to track and wait for deferreds without actually having
    received a reference to them.
    """
    def __init__(self):
        self.list = []
    
    def put(self, d):
        """
        Put another deferred in the tracker.
        """
        if not isinstance(d, defer.Deferred):
            raise TypeError("Object '%s' is not a deferred" % d)
        self.list.append(d)

    def deferToAll(self):
        """
        Return a deferred that tracks all active deferreds that aren't yet
        being tracked. When the tracked deferreds fire, the returned deferred
        fires, too.
        """
        if self.list:
            d = defer.DeferredList(self.list)
            self.list = []
        elif hasattr(self, 'd_WFA') and not self.d_WFA.called():
            d = defer.Deferred()
            self.d_WFA.chainDeferred(d)
        else:
            d = defer.succeed(None)
        return d

    def deferToLast(self):
        """
        Return a deferred that tracks the deferred that was most recently put
        in the tracker. When the tracked deferred fires, the returned deferred
        fires, too.
        """
        if self.list:
            d = defer.Deferred()
            self.list.pop().chainDeferred(d)
        elif hasattr(self, 'd_WFL') and not self.d_WFL.called():
            d = defer.Deferred()
            self.d_WFL.chainDeferred(d)
        else:
            d = defer.succeed(None)
        return d


class AddressRestrictorMixin:
    """
    Mix me in with your normal L{twisted.internet.interfaces.IProtocolFactory}
    implementer to restrict the client addresses that are permitted to connect
    to your server.
    """
    def addSubnet(self, subnet):
        """
        Adds a subnet for permitted client connection addresses, e.g.,
        '192.168.1.1/24'.
        """
        subnetSequence = subnet.split("/")
        base = self._quadToInt(subnetSequence[0])
        if len(subnetSequence) == 1:
            bits = 32
        else:
            bits = subnetSequence[1]
        subnets = getattr(self, '_subnets', [])
        subnets.append((base, int(bits)))
        self._subnets = subnets
    
    def _quadToInt(self, quad):
        """
        Converts the dotted-quad address string supplied as I{quad} into an
        integer.
        """
        return struct.unpack(">L", socket.inet_aton(quad))[0]

    def testAddress(self, quad):
        """
        Tests the supplied IP address for a match with the subnet(s) defined
        for acceptance.

        @param quad: A string representing an IPv4 address in dotted-quad
            format.
        
        """
        addrInt = self._quadToInt(quad)
        for base, bits in self._subnets:
            maskString = '1'*bits + '0'*(32-bits)
            mask = int(maskString, 2)
            if (addrInt & mask) == (base & mask):
                return True
        return False

    def buildProtocol(self, addr):
        """
        A protocol is only returned if the address matches my IP subnet.
        Otherwise, the connection immediately closes.
        """
        if self.testAddress(addr.host):
            for BaseClass in self.__class__.__bases__:
                if interfaces.IProtocolFactory.implementedBy(BaseClass):
                    return BaseClass.buildProtocol(self, addr)


class TracerMixin(object):
    """
    Mix me in to trace problems
    """
    isTracing = False
    traceFrame = None
    traceStack = [
        # Bottom frame on up, just like a stack. The following items just
        # represent an example that was used in Trac/WSGI debugging.
        ('cache.py', 'get_changes'),
        ('changeset.py', 'get_changes'),
        ('changeset.py', '_render_html')
        ]
    traceLevels = 5
    
    def settrace(self):
        """
        Call this method to start tracing. If you're using threads, you must
        call it within the same thread whose execution you want to trace.
        """
        sys.settrace(self.trace)
        self.isTracing = True

    def trace(self, frame, event, arg):
        """
        This is the actual trace function.
        """
        def msg(level):
            values = ["." * level]
            values.extend([
                getattr(frame.f_code, "co_%s" % x)
                for x in ('filename', 'firstlineno', 'name')])
            if values != getattr(self, '_prevMsgValues', None):
                self._prevMsgValues = values
                print "%s %s (%04d): %s" % tuple(values)

        def isTraceEntry(k, thisFrame):
            if thisFrame.f_code.co_name == self.traceStack[k][1]:
                tail = "/%s" % self.traceStack[k][0]
                if thisFrame.f_code.co_filename.endswith(tail):
                    return True

        def frameGenerator(N):
            nextFrame = frame
            for k in xrange(N):
                yield k, nextFrame
                nextFrame = nextFrame.f_back

        if not self.isTracing:
            return
        if event == 'call':
            level = 1
            if self.traceFrame is None:
                N = len(self.traceStack)
                for k, thisFrame in frameGenerator(N):
                    if not isTraceEntry(k, thisFrame):
                        return
                else:
                    print "-" * 40
                    self.traceFrame = frame
            else:
                for k, thisFrame in frameGenerator(self.traceLevels):
                    level += 1
                    if thisFrame in (None, self.traceFrame):
                        break
                else:
                    return
            msg(level)
            return self.trace
        elif event == 'return' and frame == self.traceFrame:
            self.traceFrame = None
            print "->", arg
