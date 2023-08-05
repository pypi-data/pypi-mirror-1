# AsynCluster: Master
# A cluster management server based on Twisted's Perspective Broker. Dispatches
# cluster jobs and regulates when and how much each user can use his account on
# any of the cluster node workstations.
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
The PB server for node-master TCP connections.
"""

from zope.interface import implements
from twisted.internet import defer, interfaces
from twisted.cred import credentials, checkers, portal, error
from twisted.python.failure import Failure
from twisted.spread import pb

from twisted_goodies.misc import AddressRestrictorMixin


class Perspective(pb.Avatar):
    """
    Each node's PB client receives a reference to its very own instance of me
    as its perspective upon making an authenticated TCP connection to the node
    master server.

    @ivar ID: A unique ID for this node during a mutually authenticated
        client-server connection.

    @ivar userID: The ID of any user having a session underway on the node.
    
    """
    def __init__(self, ctl):
        self.ctl = ctl

    def perspective_getSessionManager(self):
        """
        Remotely-accessible wrapper for
        L{control.Controller.getSessionManager}.
        """
        return self.ctl.getSessionManager()

    def attached(self, clientRoot):
        """
        Called by the node client L{Realm}, after a successful login, with a
        reference to the I{clientRoot} object supplied to it as the
        incomprehensibly named 'mind'.

        Performs a reverse login to the client to satisfy it that I am running
        on a trustworthy server and the arbitrary Python code it receives from
        this server to execute for computing jobs will not do bad things to it.
        """
        def responded(accepted):
            if accepted:
                clientRoot.notifyOnDisconnect(self.detached)
                d = self.ctl.attachNode(self, clientRoot)
                d.addCallback(done)
            else:
                d = defer.succeed(None)
            d.addCallback(lambda _: (pb.IPerspective, self, self.detached))
            return d

        def done(ID):
            print "Attached: %s" % str(ID)
            self.ID = ID
        
        serverPassword = self.ctl.config['common']['server password']
        d = clientRoot.callRemote('reverseLogin', serverPassword)
        d.addCallback(responded)
        return d

    def detached(self, *null):
        """
        Called when the node client disconnects.
        """
        if hasattr(self, 'ID'):
            print "Detached: %s" % str(self.ID)
            self.ctl.detachNode(self.ID)
            del self.ID


class PasswordChecker(object):
    """
    Checks hashed passwords based on the 'client' section of the config file.
    """
    implements(checkers.ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernameHashedPassword,)

    def __init__(self, clientSection):
        self.clientSection = clientSection
    
    def requestAvatarId(self, credentials):
        def possiblyMatched(matched, user):
            if matched:
                return user
            return Failure(error.UnauthorizedLogin())

        user = credentials.username
        if user != self.clientSection['user']:
            d = defer.succeed(False)
        else:
            password = self.clientSection.get('password', None)
            if password is None:
                d = defer.succeed(False)
            else:
                d = defer.maybeDeferred(credentials.checkPassword, password)
        d.addCallback(possiblyMatched, user)
        return d


class Realm(object):
    """
    Construct me with to a reference to the L{control.Controller} object that
    controls everything.
    """
    implements(portal.IRealm)

    def __init__(self, ctl):
        self.ctl = ctl

    def requestAvatar(self, avatarID, mind, *interfaces):
        """
        Returns a deferred of fires with the required
        I{interface, perspective, logout} tuple after the perspective attempts
        a reverse log into the client.
        """
        if pb.IPerspective not in interfaces:
            raise NotImplementedError(self, interfaces)
        perspective = Perspective(self.ctl)
        return perspective.attached(mind)


class ServerFactory(AddressRestrictorMixin, pb.PBServerFactory):
    """
    I am a PB server factory for the NDM node-master TCP server, which only
    accepts connections from one or more IP address subnets, defined in the
    config file as a comma-separated list of base/bits strings, e.g.,
    192.168.1.0/24.

    Construct me with a reference to the L{control.Controller} object that
    controls everything. It must have a public attribute 'config' referencing a
    config object loaded with the NDM configuration file.
    """
    def __init__(self, ctl, checker=None):
        # The checker keyword is for testing with a simple checker
        for subnetString in ctl.config['server']['subnets']:
            self.addSubnet(subnetString.strip())
        rootPortal = portal.Portal(Realm(ctl))
        if checker is None:
            checker = PasswordChecker(ctl.config['client'])
        rootPortal.registerChecker(checker)
        pb.PBServerFactory.__init__(self, rootPortal)

    
    


        
