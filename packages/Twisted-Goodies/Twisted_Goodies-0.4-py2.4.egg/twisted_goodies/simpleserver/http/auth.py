# twisted_goodies.simpleserver.http:
# A virtual hosting twisted.web2 HTTP server that uses subdirectories for
# virtual host content. Subdirectories can be python packages providing dynamic
# content with a root resource object, or sources of static content.
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
Provides an authenticated wrapper for C{twisted.web2.iweb.IResource}
implementations.
"""

from zope.interface import Interface, implements
from twisted.cred import portal, checkers
from twisted.web2.auth import digest, basic, wrapper


class IHTTPUser(Interface):
    """From twisted/doc/web2/examples/auth/credsetup.py"""
    pass


class HTTPUser(object):
    """From twisted/doc/web2/examples/auth/credsetup.py"""
    implements(IHTTPUser)


class HTTPAuthRealm(object):
    """From twisted/doc/web2/examples/auth/credsetup.py"""
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IHTTPUser in interfaces:
            return IHTTPUser, HTTPUser()
        raise NotImplementedError("Only IHTTPUser interface is supported")


class AuthResource(wrapper.HTTPAuthResource):
    """
    Instantiate me with a reference to a C{twisted.web2.iweb.IResource}
    provider and the path of a user:password file and I'll provide secure
    access to the resource.
    """
    addSlash = False
    authSpecs = {}
    
    def __init__(self, protectedResource, passwd, realmName='default'):
        self.cacheKey = (passwd, realmName)
        if self.cacheKey not in self.authSpecs:
            credFactories = (
                basic.BasicCredentialFactory(realmName),
                digest.DigestCredentialFactory('md5', realmName))
            thisPortal = portal.Portal(HTTPAuthRealm())
            thisPortal.registerChecker(checkers.FilePasswordDB(passwd))
            specs = (credFactories, thisPortal)
            self.authSpecs[self.cacheKey] = specs
        specs = (protectedResource,) + \
                self.authSpecs[self.cacheKey] + (IHTTPUser,)
        print "AUTH", specs, passwd
        wrapper.HTTPAuthResource.__init__(self, *specs)

        

