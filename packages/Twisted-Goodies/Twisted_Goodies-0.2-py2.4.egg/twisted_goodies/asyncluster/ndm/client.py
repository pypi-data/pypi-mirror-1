# AsynCluster: Node Display Manager (NDM):
# A simple X display manager for cluster nodes that also serve as
# access-restricted workstations. An NDM client runs on each node and
# communicates via Twisted's Perspective Broker to the Aysncluster server,
# which regulates when and how much each user can use his account on any of the
# workstations. The NDM server also dispatches cluster operations to the nodes
# via the NDM clients, unbeknownst to the workstation users.
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
The PB-based network client for the cluster node.
"""

from twisted.internet import defer, reactor
from twisted.cred import credentials
from twisted.spread import pb

import session


WINDOW_LINGER_TIME = 0.5


class ConnectionError(Exception):
    """
    An error occurred while trying to connect to the AsynCluster
    server.
    """


class ClientRoot(pb.Referenceable):
    """
    I am the root resource for one cluster node.
    """
    def __init__(self, main, serverPassword):
        self.main = main
        self.serverPassword = serverPassword
        self.trusted = False
        self.jobs = {}
    
    def remote_reverseLogin(self, password):
        """
        The server calls this method with its own password to authenticate
        itself to the client.

        @return: C{True} if the server was successfully authenticated.
        """
        self.trusted = (password == self.serverPassword)
        return self.trusted

    def remote_setTimeLeft(self, hoursLeft):
        """
        Sets the number of hours left (a float) to the user.
        """
        self.main.sessionUpdate(hoursLeft)

    def remote_message(self, message):
        """
        Displays a pop-up message for the current user.
        """
        pass

    def remote_newJob(self, jobID, jobCode):
        """
        Registers the job identified by the specified integer I{jobID} and
        represented by Python code contained in the string I{jobCode}.

        @return: C{True} if the I{jobCode} was accepted and executed OK,
            C{False} otherwise.
            
        """
        if not self.trusted:
            return False
        try:
            namespace = {}
            exec jobCode in namespace
        except:
            return False
        self.jobs[jobID] = namespace
        return True
    
    def remote_runJob(self, jobID, callName, *args, **kw):
        """
        Runs the specified callable object with any supplied
        arguments and keywords in the namespace of the specified I{jobID}.
        
        @param jobID: An integer uniquely specifying an already-registered job.

        @param callName: A string with the name of a callable object in the
            job's namespace.

        @args: Any arguments for the call.

        @kw: Any keywords for the call.
        
        @return: A deferred to the eventual result of the call.
        
        """
        if self.trusted:
            calledObject = getattr(self.jobs[jobID], callName, None)
            if callable(calledObject):
                self.d_runningJob = defer.maybeDeferred(
                    calledObject(*args, **kw))
                return self.d_runningJob
                

class ClientFactory(pb.PBClientFactory):
    """
    """
    def clientConnectionFailed(self, connector, reason):
        raise ConnectionError("Couldn't connect to server")


class Client(object):
    """
    I connect to the master TCP server via PB and offer it L{ClientRoot} as my
    root resource object.
    """
    def __init__(self, main):
        self.main = main
    
    def connect(self):
        """
        Connects to the master TCP server, returning a deferred that fires with
        a remote reference to the server's global session manager.
        """
        def gotAnswer(answer):
            if pb.IUnjellyable.providedBy(answer):
                self.perspective = answer
                return answer.callRemote('getSessionManager')
            raise ConnectionError("Couldn't authorize connection to server")
        
        cc = self.main.config['client']
        # TCP Connection
        factory = ClientFactory()
        port = int(self.main.config['common']['tcp port'])
        self.connector = reactor.connectTCP(cc['host'], port, factory)
        # Login parameters
        credential = credentials.UsernamePassword(cc['user'], cc['password'])
        serverPassword = self.main.config['common']['server password']
        self.root = ClientRoot(self.main, serverPassword)
        # Do the login
        return factory.login(credential, self.root).addBoth(gotAnswer)

    def disconnect(self):
        """
        Disconnects from the master TCP server, returning a deferred that fires
        when the disconnection is complete. Before the TCP disconnection
        occurs, any jobs that are running are allowed to finish and any active
        session is ended.
        """
        # Get a deferred that will have fired when any running jobs are done.
        d = getattr(self.root, 'd_runningJob', None)
        if d is None or d.called:
            d = defer.succeed(None)
        # When that happens, we will want to:
        # (1) end any active session, and
        d.addCallback(lambda _: self.main.sessionEnd())
        # (2) disconnect from the server
        d.addCallback(lambda _: self.connector.disconnect())
        # The returned deferred only fires once all this is done.
        return d
        
            
        
        

        

    

