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
Running jobs on cluster nodes.
"""

from zope.interface import implements, Interface
from twisted.internet import defer

from twisted_goodies import taskqueue


class NodeWorker(taskqueue.RemoteCallWorker):
    """
    I implement a L{taskqueue.IWorker} that runs tasks, up to I{N} pending at a
    time, in a particular job on a particular node.
    """
    def _runNow(self, null, task):
        funcName, args, kw = task.callTuple
        d = self.remoteCaller('runJob', task.series, funcName, *args, **kw)
        job = (task, d)
        self.jobs.append(job)
        d.addBoth(self._doneTrying, job)
        # This task's deferred is NOT returned!


class JobManager(object):
    """
    I keep jobs running on attached cluster nodes, maintaining a pipeline of no
    fewer than I{N} calls pending on each node to minimize the effects of
    network latency and balance the load across the nodes while still
    permitting some priority queueing of jobs by niceness.
    """
    def __init__(self):
        self.jobs  = {}
        self.queue = taskqueue.TaskQueue()

    def shutdown(self):
        """
        Shuts down my task queue, returning a deferred that fires when the
        queue has emptied and all node workers have finished and been
        terminated.
        """
        return self.queue.shutdown()

    def attachNode(self, nodeRoot):
        """
        Attaches a new node.
        
        @return: A deferred that fires with a unique ID for the node when all
            of the currently registered jobs have been tried on the node.
        """
        def tried(success, worker, jobID):
            if success:
                worker.iQualified.append(jobID)
                
        worker = NodeWorker(nodeRoot)
        nodeID = self.queue.attachWorker(worker)
        dList = []
        for jobID, jobInfo in self.jobs.iteritems():
            jobCode = jobInfo[0]
            d = nodeRoot.callRemote('newJob', jobID, jobCode)
            d.addCallback(tried, worker, jobID)
            dList.append(d)
        return defer.DeferredList(dList).addCallback(lambda _: nodeID)
    
    def detachNode(self, nodeID):
        """
        Detaches and terminates the node worker specified by the supplied
        I{nodeID}.
        """
        return self.queue.detachWorker(nodeID, reassign=True, crash=True)

    def new(self, jobCode, niceness=0):
        """
        Registers a new job for execution on qualified nodes.
        
        @param jobCode: A string containing Python code that defines the job
            and its namespace.

        @keyword niceness: Scheduling niceness for all calls of the job.

        @type niceness: An integer between -20 and 20, with lower numbers
            having higher scheduling priority as in UNIX C{nice} and C{renice}.
        
        @return: A deferred that fires with a unique ID for the job.
    
        """
        jobID = self._jobCounter = getattr(self, '_jobCounter', 0) + 1
        self.jobs[jobID] = (jobCode, niceness)
        
        def tried(success, nodeID):
            if success:
                worker = self.queue.workers[nodeID]
                worker.iQualified.append(jobID)
        
        dList = []
        for nodeID, worker in self.queue.workers.iteritems():
            nodeRoot = worker.nodeRoot
            d = nodeRoot.callRemote('newJob', jobID, jobCode)
            d.addCallback(tried, nodeID)
            dList.append(d)
        d = defer.DeferredList(dList)
        d.addCallback(lambda _: jobID)
        return d
    
    def run(self, jobID, callName, *args, **kw):
        """
        Runs the specified I{jobID} by putting a call to the specified callable
        object in the job's namespace, with any supplied arguments and
        keywords, into the queue.

        Scheduling of the job is impacted by the niceness of the job itself. As
        with UNIX niceness, the value should be an integer where 0 is normal
        scheduling, negative numbers are higher priority, and positive numbers
        are lower priority. Calls for a job having niceness N+10 are dispatched
        at approximately half the rate of calls for a job with niceness N.

        @note: The task object generated contains the name of a callable (as a
            string) for the first element of its I{callTuple} attribute,
            instead of a callable itself.
        
        @return: A deferred to the eventual result of the call when it is
            eventually pulled from the queue and run.

        """
        if jobID not in self.jobs:
            raise ValueError("No job '%s' registered" % jobID)
        kw['series'] = jobID
        kw['niceness'] = self.jobs[jobID][1]
        return self.queue.task(callName, *args, **kw)
