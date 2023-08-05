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
Mock objects for unit tests
"""

import time
from twisted.internet import defer, reactor
from twisted.cred import credentials
from twisted.spread import pb, flavors

NODE_ID = 123
SERVER_PASSWORD = 'foobar'
TCP_PORT = 31415

VERBOSE = False


def deferToDelay(result, delay=0.1):
    d = defer.Deferred()
    reactor.callLater(delay, d.callback, result)
    return d


#--- Server Side --------------------------------------------------------------

class JobManager(object):
    def __init__(self):
        self.counter = 0
        self.attached = {}
        
    def attachNode(self, nodeRoot):
        self.counter += 1
        self.attached[self.counter] = nodeRoot
        return defer.succeed(self.counter)
    
    def detachNode(self, ID):
        del self.attached[ID]


class SessionManager(flavors.Viewable):
    def view_begin(self, node, userID, password):
        if userID == 'alpha' and password == 'bravo':
            self.startTime = time.time()
            timeLeft = 2.0
        else:
            timeLeft = 0.0
        return defer.succeed(timeLeft)

    def view_end(self, node):
        pass
    

class Control(object):
    def __init__(self):
        self.attached = False
        self.config = {
            'server':{'subnets':['127.0.0.1', '192.15.28.10/24'],
                      'passwords file':'passwd.txt'},
            'common':{'server password':SERVER_PASSWORD}
            }
    
    def attachNode(self, nodePerspective, nodeRoot):
        self.attached = nodePerspective, nodeRoot
        return defer.succeed(NODE_ID)

    def detachNode(self, nodeID):
        self.attached = None

    def getSessionManager(self):
        return SessionManager()

    def nodeRemote(self, nodeID, called, *args, **kw):
        return defer.succeed(None)


class Root(object):
    def __init__(self, serverPassword=None):
        self.serverPassword = serverPassword
        self.calls = []
        self.callbacks = []

    def notifyOnDisconnect(self, callback):
        self.callbacks.append(callback)

    def callRemote(self, called, *args, **kw):
        if VERBOSE:
            print "REMOTE CALL", called, args, kw
        info = {'called':called,
                'args':args,
                'kw':kw}
        self.calls.append(info)
        if called == 'runJob':
            return self.callRemote(*args[1:], **kw)
        if called == 'reverseLogin':
            result = (args[0] == self.serverPassword)
        elif called == 'test':
            result = 10*sum(args) + 100*sum(kw.values())
        else:
            result = None
        return deferToDelay(result)


class UserDataTransactor(object):
    def setUp(self, *args):
        self.userID, self.password, self.timeRemaining = args

    def sessionAuthorized(self, userID, userPassword):
        if userID == self.userID and userPassword == self.password:
            result = True
        else:
            result = False
        return defer.succeed(result)
       
    def sessionStart(self, userID):
        if userID == self.userID:
            result = self.timeRemaining
        else:
            result = 0.0
        return defer.succeed(result)

    def restricted(self, userID, isOrNot=None):
        return defer.succeed(True)

    def recordSessionStartTime(self, userID):
        pass


class Perspective(object):
    def __init__(self, ID, userID):
        self.ID, self.userID = ID, userID


#--- Client Side --------------------------------------------------------------

class ClientRoot(pb.Referenceable):
    def remote_reverseLogin(self, password):
        self.password = password
        return password == SERVER_PASSWORD


class Client(object):
    def connect(self):
        self.factory = pb.PBClientFactory()
        reactor.connectTCP('localhost', TCP_PORT, self.factory)
        credential = credentials.UsernamePassword('foo', 'bar')
        self.clientRoot = ClientRoot()
        return self.factory.login(credential, self.clientRoot)

    def disconnect(self):
        self.factory.disconnect()

    

