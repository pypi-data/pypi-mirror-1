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

import struct, socket, new
from twisted.internet import interfaces, defer
from twisted.spread import pb


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


class PerspectiveFactory(object):
    """
    I generate perspectives for clients with varying access
    privileges. Construct me with an I{interfaceMap} dict and a
    I{perspectiveList} sequence.

    Each entry of the interface map is keyed by the name of an access privilege
    and has as its value a sequence of one or more interfaces that must be
    provided by the perspective object in order to grant the client such
    access.

    The perspective list contains all of the perspective classes that implement
    the interfaces in the interface map. Each perspective that I generate will
    be an instance of a composite of those classes that implement a required
    interfaces.
    """
    def __init__(self, interfaceMap, perspectiveList):
        self.interfaceMap = interfaceMap
        self.perspectiveList = perspectiveList
        self.implementorMap = {}
    
    def implementor(self, interface):
        """
        Returns the first perspective class in my C{perspectiveList} sequence
        that implements the supplied I{interface}, raising an exception if none
        do so.
        """
        result = self.implementorMap.get(interface, None)
        if result is None:
            for candidate in self.perspectiveList:
                if interface.implementedBy(candidate):
                    result = self.implementorMap[interface] = candidate
                    break
            else:
                raise NotImplementedError(
                    "No perspective class implements '%s'" % repr(interface))
        return result
    
    def perspective(self, privileges, **kw):
        """
        Returns to the client a perspective instance that provides interfaces
        in accordance with the supplied list of I{privileges}. Any keywords
        supplied define the names and values of attributes that the instance is
        assigned.

        The interfaces provided by the perspective are mapped out in my
        I{interfaceMap} dict.
        """
        baseClasses = [pb.Avatar]
        for thisPrivilege in privileges:
            requiredInterfaces = self.interfaceMap.get(thisPrivilege, [])
            for thisInterface in requiredInterfaces:
                implementor = self.implementor(thisInterface)
                if implementor is not None and implementor not in baseClasses:
                    baseClasses.append(implementor)
        # Create and instantiate the user's custom perspective class
        Perspective = new.classobj('Perspective', tuple(baseClasses), {})
        thisPerspective = Perspective()
        # Set the perspective's instance attributes
        for name, value in kw.iteritems():
            setattr(thisPerspective, name, value)
        # The perspective is ready to give to the client
        return thisPerspective
