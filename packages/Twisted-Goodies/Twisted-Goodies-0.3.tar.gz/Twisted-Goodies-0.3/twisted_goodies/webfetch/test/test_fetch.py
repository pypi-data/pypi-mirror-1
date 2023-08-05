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
Unit tests for twisted_goodies.webfetch.fetch
"""

import os, os.path, re
from zope.interface import implements
from twisted.internet import defer, task
from twisted.web2 import http_headers
from twisted.web2 import responsecode, iweb, stream as stream_mod
from twisted.trial.unittest import TestCase

from twisted_goodies.webfetch import fetch


VERBOSE = True


class MockStream(object):
    implements(stream_mod.IStream)

    def __init__(self, fh, chunkSize, interval):
        self.fh = fh
        self.waiting = []
        self.pending = []
        self.open = True

        print "\nLOOPING"
        self.looper = task.LoopingCall(self._write, chunkSize)
        self.d = self.looper.start(interval)
        self.d.addCallback(lambda _: self.close())

    def _write(self, chunkSize):
        if self.open:
            data = self.fh.read(chunkSize)
            if VERBOSE:
                print "Stream is providing chunk:\n%s\n%s\n" \
                      % ('-'*40, data)
        else:
            data = ""

        print "WRITE",
        if self.waiting:
            print "A"
            self.waiting.pop(0).callback(data)
        elif self.open:
            print "B"
            self.pending.append(data)
        else:
            print "C"

        if len(data) < chunkSize:
            self.looper.stop()

    #--- IStream implementation -----------------------------------------------

    def read(self):
        print "READ",
        if self.pending:
            print "AA"
            return defer.succeed(self.pending.pop(0))
        elif self.open:
            print "BB"
            d = defer.Deferred()
            self.waiting.append(d)
            return d
        print "CC"

    def close(self):
        print "CLOSE"
        if self.open:
            for d in self.waiting:
                d.callback(None)
            self.open = False
            self.fh.close()


class MockResponse(object):
    implements(iweb.IResponse)

    code = responsecode.OK
    headers = None

    writeInterval = 0.3
    writeChunks = 5
    writePages = {
        "/":                "eepatents.com_index.html",
        "/background.html": "eepatents.com_background.html"
        }

    def __init__(self, schemePart):
        self.headers = http_headers.Headers()
        responseFile = self.writePages.get(schemePart, "err404")
        filePath = os.path.join(os.path.dirname(__file__), responseFile)
        fileSize = os.stat(filePath).st_size
        chunkSize = fileSize/self.writeChunks + 1
        fh = open(filePath)
        self.stream = MockStream(fh, chunkSize, self.writeInterval)
        self.d = self.stream.d


class TestableSiteGetter(fetch.SiteGetter):
    def connect(self, schemePart):
        self.response = MockResponse(schemePart)
        return defer.succeed(self.response)


class TestSiteGetterWithMock(TestCase):
    def setUp(self):
        self.sg = TestableSiteGetter("eepatents.com", 88)
        
    def tearDown(self):
        return self.sg.response.d

    def test_getPage(self):
        def gotPage(html):
            m = re.match(
                "<HTML>.+Suominen.+Patent\ Agent.+</HTML>", html.strip())
            self.failIf(m is not None, "Expected page not fetched")
        
        return self.sg.getPage("/").addCallback(gotPage)

    def test_searchPage(self):
        def gotMatch(m):
            if VERBOSE:
                print "\nGot purported match object:", m
            self.failUnlessEqual(m.group(1), "Suominen")

        regex = "<title>.+?(S.+n),.+?</title>"
        d = self.sg.searchPage("/background.html", regex)
        d.addCallback(gotMatch)
        return d


class TestSiteGetter(TestCase):
    def setUp(self):
        self.sg = fetch.SiteGetter("eepatents.com")

    def tearDown(self):
        return self.sg.shutdown()

    def test_getPage(self):
        def gotPage(html):
            m = re.match(
                "<HTML>.+Suominen.+Patent\ Agent.+</HTML>", html.strip())
            self.failIf(m is not None, "Expected page not fetched")
        
        return self.sg.getPage("/").addCallback(gotPage)

    def test_searchPage(self):
        def gotMatch(m):
            if VERBOSE:
                print "\nGot purported match object:", m
            self.failUnlessEqual(m.group(1), "Suominen")

        regex = "<title>.+?(S.+n),.+?</title>"
        d = self.sg.searchPage("/background.html", regex)
        d.addCallback(gotMatch)
        return d
