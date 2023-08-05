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
Unit tests for taskqueue
"""

import time, random, threading
from twisted.internet import defer
from twisted.trial.unittest import TestCase

from util import base
from util import MockWorker


VERBOSE = False


class TestTaskQueueGeneric(TestCase):
    def setUp(self):
        self.queue = base.TaskQueue()

    def tearDown(self):
        return self.queue.shutdown()

    def testOneTask(self):
        worker = MockWorker(0.5)
        self.queue.attachWorker(worker)
        d = self.queue.call(lambda x: 2*x, 15)
        d.addCallback(self.failUnlessEqual, 30)
        return d

    def testOneWorker(self):
        N = 30
        mutable = []

        def checkResults(null):
            self.failUnlessEqual(len(mutable), N)
            self.failUnlessEqual(
                sum(mutable),
                sum([2*x for x in xrange(N)]))

        worker = MockWorker(0.01)
        self.queue.attachWorker(worker)
        dList = []
        for x in xrange(N):
            d = self.queue.call(lambda y: 2*y, x)
            d.addCallback(lambda result: mutable.append(result))
            dList.append(d)
        d = defer.DeferredList(dList)
        d.addCallback(checkResults)
        return d

    def testMultipleWorkers(self):
        N = 100
        mutable = []

        def checkResults(null):
            self.failUnlessEqual(len(mutable), N)
            self.failUnlessEqual(
                sum(mutable),
                sum([2*x for x in xrange(N)]))

        for runDelay in (0.05, 0.1, 0.4):
            worker = MockWorker(runDelay)
            ID = self.queue.attachWorker(worker)
            worker.ID = ID
        dList = []
        for x in xrange(N):
            d = self.queue.call(lambda y: 2*y, x)
            d.addCallback(lambda result: mutable.append(result))
            dList.append(d)
        d = defer.DeferredList(dList)
        d.addCallback(checkResults)
        return d
