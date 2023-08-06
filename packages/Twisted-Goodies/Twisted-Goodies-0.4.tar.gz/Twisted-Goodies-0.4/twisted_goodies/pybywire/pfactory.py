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
Perspective factory
"""

import new
from twisted.internet import interfaces
from twisted.spread import pb


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


