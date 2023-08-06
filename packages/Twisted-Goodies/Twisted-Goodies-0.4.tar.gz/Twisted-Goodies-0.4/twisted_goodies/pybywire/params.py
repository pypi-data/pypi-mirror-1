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
Provides 'Parameterized' objects that manage caches based on parameters and key
attributes, and that can be passed around via PB with a minimum of fuss on the
user's part.
"""

from twisted.spread import pb, jelly
from twisted.python.reflect import namedObject
import pack


def paregister(*stringReps):
    """
    Call this function with one or more arguments containing standard string
    representations of L{Parameterized} subclasses, and those subclasses will
    be made self-unjellyable and allowed past PB security.

    Use judiciously!
    """
    for stringRep in stringReps:
        # Load the class for the string representation
        cls = namedObject(stringRep)
        # Allow instances of the class, including its type and module
        pb.setUnjellyableForClass(stringRep, cls)
        # Don't think this next line is needed after the one above has run
        #pb.globalSecurity.allowInstancesOf(cls)


class ParaMeta(type):
    """
    I add each imported subclass of L{Parameterized} to my I{registry} of
    string class representations, which can be used in a remote call to
    L{paregister} to make those subclasses self-unjellyable and allowable past
    PB security.
    """
    registry = []

    def __init__(cls, name, bases, dictionary):
        stringRep = "%s.%s" % (cls.__module__, name)
        cls.registry.append(stringRep)
        pb.setUnjellyableForClass(stringRep, cls)
    

class Parameterized(jelly.Jellyable, jelly.Unjellyable, object):
    """
    @cvar registry: A list of standard string representations of all my
      subclasses. Your remote PB peer should expose L{paregister} to you so you
      can call it remotely with those string representations to make the
      subclasses self-unjellyable and allow instances of them.
    
    @cvar keyAttrs: A dict of attributes on which cache keying will be
      partially based. Any entry having a value of C{None} has no default, and
      the attribute and its value must be supplied to the constructor via a
      keyword, or set directly before use.

    @cvar paramNames: A sequence of names for my parameter. Parameter vectors
      must be supplied to L{setParamVector} in that order.

    """
    __metaclass__ = ParaMeta

    name = None
    paramNames, keyAttrs = [], {}

    def __init__(self, **kw):
        """
        Sets up my caching with a dict of parameters.

        When instantiated as an original (not remote) version, keywords can be
        supplied (in some cases, must be supplied) that specify the names and
        values of attributes that are incorporated into the cache keying.
        """
        for name, default in self.keyAttrs.iteritems():
            value = kw.pop(name, default)
            if value is not None:
                object.__setattr__(self, name, value)
        for name, value in kw.iteritems():
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name == 'cache':
            self.cache = {}
            return self.cache
        if name == 'registry':
            return ParaMeta.registry
        raise AttributeError("No attribute '%s'" % name)

    def __str__(self):
        if self.name:
            return self.name
        return self.__class__.__name__.replace("_", " ")

    def __setattr__(self, name, value):
        """
        Sets the attribute I{name} to the supplied I{value}, clearing the cache
        if the attribute is a parameter and its value will be (re)defined.
        """
        if name in self.paramNames or name in self.keyAttrs:
            if not hasattr(self, name):
                isDifferent = True
            else:
                isDifferent = (getattr(self, name) != value)
                # Account for the possibility that one value is a Numpy array
                if hasattr(isDifferent, 'any'):
                    isDifferent = isDifferent.any()
            if isDifferent:
                self.cache.clear()
        object.__setattr__(self, name, value)

    def N_params(self):
        """
        Returns the number of parameters. Override this if you have some other
        parameters figured in somehow.
        """
        return len(self.paramNames)

    def setParams(self, **kw):
        """
        Sets a number of parameters and/or key attributes at once, as keywords.
        """
        for name, value in kw.iteritems():
            if name not in self.paramNames:
                raise LookupError("No such parameter '%s'" % name)
            setattr(self, name, value)

    def paramVector(self):
        """
        Returns my entire current set of parameters as a sequence.
        """
        return [getattr(self, name) for name in self.paramNames]

    def setParamVector(self, paramVector):
        """
        Sets the entire set of parameters from the supplied I{paramVector} of
        values.
        """
        if len(paramVector) != len(self.paramNames):
            raise ValueError("You must supply the exact number of parameters")
        for k, name in enumerate(self.paramNames):
            value = paramVector[k]
            setattr(self, name, value)

    #--- Jelly/Unjelly API ----------------------------------------------------

    def getStateFor(self, jellier):
        """
        Generates my state for jellying, which consists of the value of my key
        attributes and parameters. Also registers my (sub)class and its module
        as being safe for unjellying.
        """
        state = {'name':self.name}
        for sequence in (self.keyAttrs.keys(), self.paramNames):
            for name in sequence:
                if hasattr(self, name):
                    value = getattr(self, name)
                    if pack.needsPacking(value):
                        if '_packedNames' not in state:
                            state['_packedNames'] = []
                            packer = pack.Packer()
                        state['_packedNames'].append(name)
                        packer.append(value)
                    else:
                        state[name] = value
        if 'packer' in locals():
            state['_packedValues'] = packer()
        return state

    def setStateFor(self, unjellier, state):
        """
        Sets my state from the supplied I{state} dict, as usual except for any
        packed values present.
        """
        if '_packedNames' in state:
            packedNames = state.pop('_packedNames')
            unpacker = pack.Unpacker(state.pop('_packedValues'))
            for k, value in enumerate(unpacker):
                object.__setattr__(self, packedNames[k], value)
        self.__dict__.update(state)
