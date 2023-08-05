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
An all-powerful Controller object and a UNIX socket PB interface to it.
"""

from twisted.python.failure import Failure
from twisted.internet import defer, reactor, task
from twisted.spread import pb

import database, jobs


UNRESTRICTED_LOGIN_HOURS = 10.0


class RemoteCallError(Exception):
    """
    A remote call raised an exception.
    """


class SessionManager(pb.Viewable):
    """
    This viewable permits a node client to begin and end user access sessions.
    
    @ivar t: An L{AccessBroker} object that manages user session data.
    
    """
    updateInterval = 30.0
    updateFirstDelay = 1.0
    
    def __init__(self, ctl):
        self.ctl = ctl
        self.sessionMap = {}
        url = self.ctl.config['server']['database']
        self.t = database.UserDataTransactor(url)
        self.looper = task.LoopingCall(self._update)
        self.d = self.looper.start(self.updateInterval, now=True)

    def _update(self):
        dList = []
        for ID in self.sessionMap.iterkeys():
            hoursLeft = self.sessionMap[ID][1]
            hoursLeft -= float(self.updateInterval) / 3600.0
            self.sessionMap[ID][1] = hoursLeft
            if hoursLeft >= 0.0:
                d = self.ctl.nodeRemote(ID, 'setTimeLeft', hoursLeft)
            else:
                d = self.end(ID)
            dList.append(d)
        return defer.DeferredList(dList)
    
    def view_begin(self, node, userID, password):
        """
        Begins a user access session for the specified I{node} perspective and
        the specified I{userID} and I{password}.

        @return: A (possibly deferred) boolean indicating whether the
          session is authorized and was started.
        
        """
        def gotAuthorizationResult(authorized):
            if not authorized:
                print "Unauthorized session attempt for '%s'" % userID
                return False
            d = self.t.restricted(userID)
            d.addCallback(gotRestrictionResult)
            return d

        def gotRestrictionResult(restricted):
            if not restricted:
                print "Unrestricted session started for '%s'" % userID
                self.sessionMap[node.ID] = [userID, UNRESTRICTED_LOGIN_HOURS]
                return True
            d = self.t.sessionStart(userID)
            d.addCallback(gotHoursAvailable)
            return d

        def gotHoursAvailable(hours):
            if hours <= 0.0:
                print "No usage time available for '%s'" % userID
                return False
            self.sessionMap[node.ID] = [userID, hours]
            print "Session started, %f hours left, for '%s'" % (hours, userID)
            self.t.recordSessionStartTime(userID)
            return True
        
        for info in self.sessionMap.itervalues():
            if info[0] == userID:
                return False
        d = self.t.sessionAuthorized(userID, password)
        d.addCallback(gotAuthorizationResult)
        return d

    def view_timeLeft(self, node):
        """
        """
        if node.ID in self.sessionMap:
            return self.sessionMap[node.ID][1]
        return 0.0
    
    def view_end(self, node):
        """
        Ends the current user access session for the specified I{node}
        perspective.

        See L{end}.
        """
        return self.end(node.ID, callClient=False)

    def end(self, ID, callClient=True):
        """
        Ends the current user access session for the specified node I{ID}.
        """
        if ID not in self.sessionMap:
            return
        userID, hoursLeft = self.sessionMap.pop(ID)
        print "Node %s detaching, ending session for user '%s'" \
              % (str(ID), userID)
        d = self.t.sessionEnd(userID)
        if callClient:
            d.addCallback(
                lambda _: self.ctl.nodeRemote(ID, 'setTimeLeft', 0.0))
        return d


class Controller(object):
    """
    I control everything, I{heh heh heh...}
    """
    def __init__(self, config):
        self.config = config
        self.nodes = {}
        self.jobber = jobs.JobManager()

    def getSessionManager(self):
        """
        Returns references to a single instance of the L{SessionManager}
        viewable.
        """
        if not hasattr(self, 'sessionManager'):
            self.sessionManager = SessionManager(self)
        return self.sessionManager

    def attachNode(self, nodePerspective, nodeRoot):
        """
        Another mutually authenticated node client has connected, so give it a
        unique ID, attach its root referenceable to my map of node roots under
        that ID, and return a deferred that fires with the ID when the jobber
        has attached the node as well.
        """
        def gotID(ID):
            self.nodes[ID] = nodePerspective, nodeRoot
            return ID
        
        return self.jobber.attachNode(nodeRoot).addCallback(gotID)
    
    def detachNode(self, ID):
        """
        A node client has disconnected, so detach its root referenceable from
        my map of node roots.
        """
        self.nodes.pop(ID, None)
        d = self.jobber.detachNode(ID)
        if hasattr(self, 'sessionManager'):
            d.addCallback(
                lambda _: self.sessionManager.end(ID, callClient=False))
        return d

    def _remoteError(self, failure, ID):
        if failure.check(pb.DeadReferenceError, pb.PBConnectionLost):
            return self.sessionManager.end(ID, callClient=False)
        return failure
    
    def nodeRemote(self, nodeID, called, *args, **kw):
        """
        Immediately runs a non-queued call to the object specified by the
        string I{called} on the node identified by the integer I{nodeID},
        supplying any provided arguments or keywords.
        """
        if nodeID not in self.nodes:
            return defer.fail(Failure(
                RemoteCallError("Invalid node '%s'" % nodeID)))
        nodeRoot = self.nodes[nodeID][1]
        d = nodeRoot.callRemote(called, *args, **kw)
        d.addErrback(self._remoteError, nodeID)
        return d
    
    def userRemote(self, userID, called, *args, **kw):
        """
        Calls the object specified by the string I{called} on the node on which
        the user identified by the string I{userID} has an active session,
        supplying any provided arguments or keywords.
        """
        for ID, nodeStuff in self.nodes.iteritems():
            nodePerspective, nodeRoot = nodeStuff
            if getattr(nodePerspective, 'userID', None) == userID:
                d = nodeRoot.callRemote(called, *args, **kw)
                d.addErrback(self._remoteError, ID)
                return d
        return defer.fail(Failure(
            RemoteCallError("Invalid user '%s'" % userID)))


class Root(pb.Root):
    """
    I am the root object that each control client receives upon making its UNIX
    socket connection to the master control server.

    All of the heavy lifting is done by an instance of L{Controller}, a
    reference to which is supplied to my constructor.
    """
    def __init__(self, ctl):
        self.ctl = ctl

    def remote_userAction(self, userID, action, actionArg=None):
        """
        Carries out the specified I{action} concerning the user account
        I{userID}. If the action requires an argument, it is supplied as the
        I{actionArg} option.

        The actions are as follows:
            - B{password}: use the supplied string as the password
            - B{disable}: disable the account
            - B{disable}: enable the account
            - B{msg}: send the supplied string to the user as a pop-up message
            - B{kick}: kick the user off the system, disabling his account
            
        """
        t = self.ctl.getSessionManager().t
        if action == 'password':
            d = t.password(userID, actionArg)
        if action == 'disable':
            d = t.enabled(userID, False)
        elif action == 'enable':
            d = t.enabled(userID, True)
        if action == 'restrict':
            d = t.restricted(userID, True)
        elif action == 'unrestrict':
            d = t.restricted(userID, False)
        elif action == 'msg':
            d = self.ctl.userRemote(userID, 'message', actionArg)
        elif action == 'kick':
            d = self.ctl.userRemote(userID, 'kick')
        return d

    def remote_newJob(self, jobCode, niceness=0):
        """
        Registers a new computing job with the supplied I{jobCode}, returning a
        deferred to an integer jobID identifying the job.

        See L{jobs.JobManager.new}.
        """
        return self.ctl.jobber.new(jobCode, niceness)
    
    def remote_runJob(self, jobID, callName, *args, **kw):
        """
        Queues up a call to the callable object specified in the namespace of
        the specified I{jobID}. The call will be dispatched to the next node
        that is qualified and becomes available to run it.

        See L{jobs.JobManager.run}.

        @param jobID: An image identifying the namespace of a job previously
            registered on one or more of the nodes.

        @param callName: A string identifying a callable object in the job
            namespace.

        @*args: Any arguments to pass to the callable object.

        @**kw: Any keywords to pass to the callable object.

        @return: A deferred to the eventual result of the dispatch when it
            eventually runs on a qualified node.

        """
        return self.ctl.jobber.run(jobID, callName, *args, **kw)


