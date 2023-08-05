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
The worker interface and some implementors.
"""

from zope.interface import implements, invariant, Interface, Attribute
from twisted.python import failure
from twisted.internet import defer, reactor

import errors


class IWorker(Interface):
    """
    Provided by worker objects that can have tasks assigned to them for
    processing.

    All worker objects are considered qualified to run tasks of the default
    C{None} series. To indicate that subclasses or subclass instances are
    qualified to run tasks of user-defined series in addition to the default,
    the hashable object that identifies the additional series must be listed in
    the C{cQualified} or C{iQualified} class or instance attributes,
    respectively.
        
    """
    cQualified = Attribute(
        """
        A class-attribute list containing all series for which all instances of
        the subclass are qualified to run tasks.
        """)

    iQualified = Attribute(
        """
        An instance-attribute list containing all series for which the subclass
        instance is qualified to run tasks.
        """)

    def _check_qualifications(ob):
        """
        Qualification attributes must be present as lists.
        """
        for attrName in ('cQualified', 'iQualified'):
            x = getattr(ob, attrName, None)
            if not isinstance(x, list):
                raise errors.InvariantError(ob)
    invariant(_check_qualifications)

    def setResignator(callableObject):
        """
        Registers the supplied I{callableObject} to be called if the
        worker deems it necessary to resign, e.g., a remote connection
        has been lost.
        """

    def run(task):
        """
        Adds the task represented by the specified I{task} object to the list
        of tasks pending for this worker, to be run however and whenever the
        worker sees fit.

        Make sure that any callbacks you add to the task's internal deferred
        object C{task.d} return the callback argument. Otherwise, the result of
        your task will be lost in the callback chain.
        
        @return: A deferred that fires when the worker is ready to be assigned
          another task.

        """

    def stop():
        """
        Attempts to gracefully shut down the worker, returning a deferred that
        fires when the worker is done with all assigned tasks and will not
        cause any errors if the reactor is stopped or its object is deleted.

        The deferred returned by your implementation of this method must not
        fire until B{after} the results of all pending tasks have been
        obtained. Thus the deferred must be chained to each C{task.d} somehow.

        Make sure that any callbacks you add to the task's internal deferred
        object C{task.d} return the callback argument. Otherwise, the result of
        your task will be lost in the callback chain.
        """

    def crash():
        """
        Takes drastic action to shut down the worker, rudely and
        synchronously.

        @return: A list of I{task} objects, one for each task left
          uncompleted. You shouldn't have to call this method if no
          tasks are left pending; the L{shutdown} method should be
          enough in that case.
        
        """


class ThreadWorker:
    """
    I implement an L{IWorker} that runs tasks in a dedicated worker thread.
    """
    implements(IWorker)
    cQualified = []

    def __init__(self):
        import threading
        self.iQualified = []
        self.event = threading.Event()
        self.thread = threading.Thread(target=self._loop)
        self.thread.start()

    def _loop(self):
        """
        Runs a loop in a dedicated thread that waits for new tasks. The loop
        exits when a C{None} object is supplied as a task.
        """
        while True:
            # Wait here on the threading.Event object
            self.event.wait()
            task = self.task
            if task is None:
                break
            # Ready for the task attribute to be set to another task object
            self.event.clear()
            reactor.callFromThread(self.d.callback, None)
            f, args, kw = task.callTuple
            try:
                result = f(*args, **kw)
                # If the task causes the thread to hang, the method
                # call will not reach this point.
            except Exception, e:
                reactor.callFromThread(task.d.errback, failure.Failure(e))
            else:
                reactor.callFromThread(task.d.callback, result)
        # Broken out of loop, ready for the thread to end
        reactor.callFromThread(self.d.callback, None)

    def setResignator(self, callableObject):
        """
        There's nothing that would make me resign.
        """

    def run(self, task):
        """
        Starts a thread for this worker if one not started already, along with
        a L{threading.Event} object for cross-thread signaling.
        """
        if hasattr(self, 'd') and not self.d.called:
            raise ImplementationError(
                "Task Loop not ready to deal with a task now")
        self.d = defer.Deferred()
        self.task = task
        self.event.set()
        return self.d
    
    def stop(self):
        """
        The returned deferred fires when the task loop has ended and its thread
        terminated.
        """
        def joinIfPossible(null):
            if hasattr(self, 'task'):
                self.thread.join()

        if hasattr(self, 'task') and self.task is None:
            d = defer.succeed(None)
        else:
            d = defer.Deferred()
            if hasattr(self, 'd') and not self.d.called:
                d.addCallback(lambda _: self.stop())
                self.d.chainDeferred(d)
            else:
                d.addCallback(joinIfPossible)
                self.d = d
                self.task = None
                self.event.set()
        return d

    def crash(self):
        """
        Unfortunately, a thread can only terminate itself, so calling
        this method only forces firing of the deferred returned from a
        previous call to L{stop} and returns the task that hung the
        thread.
        """
        if self.task is not None and not self.task.d.called:
            result = [self.task]
        else:
            # This shouldn't happen
            result = []
        if hasattr(self, 'd') and not self.d.called:
            del self.task
            self.d.callback(None)


class CallRemoteWorker:
    """
    Instances of me provide an L{IWorker} that dispatches
    C{callRemote} tasks, no more than I{N} at a time, to a particular
    I{remoteReference} to a referenceable at a connected PB server.
    """
    implements(IWorker)
    cQualified = []

    N = 3
    
    def __init__(self, remoteReference, interface, subseries=None):
        # Setup resignation-upon-disconnect
        self.resignators = []
        from twisted.spread import pb
        self.disconnectErrors = (pb.DeadReferenceError, pb.PBConnectionLost)
        # Check supplied remote reference object
        if not hasattr(remoteReference, 'callRemote'):
            raise TypeError("You must construct me with a PB RemoteReference")
        # Setup attributes
        self.remoteCaller = remoteReference.callRemote
        self.interface = interface
        qualification = interface.__name__
        if subseries:
            qualification += ":%s" % subseries
        self.iQualified = [qualification]
        # Prepare the run request queue
        self.jobs = []
        self.runRequestQueue = defer.DeferredQueue()
        for k in xrange(self.N):
            self.runRequestQueue.put(None)

    def setResignator(self, callableObject):
        """
        I will resign upon having one of my tasks turn up a connection
        fault.
        """
        self.resignators.append(callableObject)
    
    def run(self, task):
        """
        Runs the specified task, which must be a string specifying the suffix
        portion of a method of the referenceable, e.g., I{'foo'} for
        C{remote_foo} or C{perspective_foo}.

        Returns a deferred that fires when one of the pending tasks is done
        running and I can accept another one.
        """
        def runNow(null):
            suffix, args, kw = task.callTuple
            if not [True for x in self.interface if x.endswith('_'+suffix)]:
                raise AttributeError(
                    "Interface '%s' defines no remote method *_%s" \
                    % (self.interface.__name__, suffix))
            d = self.remoteCaller(suffix, *args, **kw)
            job = (task, d)
            self.jobs.append(job)
            d.addBoth(doneTrying, job)

        def doneTrying(result, job):
            if isinstance(result, self.disconnectErrors):
                for callableObject in self.resignators:
                    callableObject()
                # The task's deferred is preserved for another try
                # with a new connection.
            else:
                self.jobs.remove(job)
                self.runRequestQueue.put(None)
                if isinstance(result, failure.Failure):
                    task.d.errback(result)
                else:
                    task.d.callback(result)
        
        if getattr(self, 'isShuttingDown', False):
            raise errors.QueueRunError
        return self.runRequestQueue.get().addCallback(runNow)
    
    def stop(self):
        """
        The returned deferred fires when all pending tasks are done.
        """
        self.isShuttingDown = True
        return defer.DeferredList([job[1] for job in self.jobs])

    def crash(self):
        """
        Return all tasks not completed by the (disconnected) PB server.
        """
        return [job[0] for job in self.jobs]
