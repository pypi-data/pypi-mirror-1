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
Unit tests for master.jobs
"""

from twisted.internet import defer
from twisted.python import failure
from twisted.trial.unittest import TestCase

import mock
import jobs


class MockTask(object):
    def __init__(self, f, args, kw, priority, series):
        self.ran = False
        self.callTuple = (f, args, kw)
        self.priority = priority
        self.series = series
        self.d = defer.Deferred()
    
    def __cmp__(self, other):
        if other is None:
            return -1
        return cmp(self.priority, other.priority)

    def __str__(self):
        return str(self.callTuple[0])


class TestNodeWorker(TestCase):
    def tearDown(self):
        if hasattr(self, 'worker'):
            return self.worker.stop()

    def testSingleTask(self):
        def checkResult(result):
            count = 0
            for call in root.calls:
                if call['called'] in ('runJob', 'aFunction'):
                    count += 1
            self.failUnlessEqual(count, 2)

        root = mock.Root()
        task = MockTask('aFunction', (1,), {}, 0, None)
        self.worker = jobs.NodeWorker(root, noTypeCheck=True)
        self.worker.run(task)
        task.d.addCallback(checkResult)
        return task.d
