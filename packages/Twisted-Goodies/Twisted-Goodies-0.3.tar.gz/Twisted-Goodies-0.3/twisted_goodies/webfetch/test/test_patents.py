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
Unit tests for twisted_goodies.webfetch.patents
"""

import os, os.path, re, tarfile
from zope.interface import implements
from twisted.internet import reactor, defer, utils
from twisted.python import procutils
from twisted.trial.unittest import TestCase

from twisted_goodies import taskqueue
from twisted_goodies.webfetch import patents


VERBOSE = False
VERBOSE_QUEUE = False

PATENT_NUMBER = 7150245
PATENT_PAGES = 4

APP_NUMBER = 20060267524


#--- Mock and testable objects ------------------------------------------------

def call(f):
    def wrapper(self, *args):
        if VERBOSE:
            argString = ", ".join(["'%s'" % str(x) for x in args])
            print "\nCALL: %s(%s)\n" % (f.__name__, argString)
        self.member = self._getMember(args[0])
        self.calls.append((f,)+args)
        d = f(self, *args)
        d.addErrback(self._oops)
        return d
    wrapper.__name__ = f.__name__
    return wrapper


class ThreadQueue(taskqueue.ThreadQueue):
    """
    I am a task queue that can display calls and results in a logging window.
    """
    def __init__(self):
        taskqueue.ThreadQueue.__init__(self, 1)
        self.callCounter = 0

    def call(self, *args, **kw):
        def done(result, wrapped):
            if hasattr(result, '__str__'):
                displayable = str(result)
            else:
                displayable = "-"
            print "< %d %s" % (wrapped, displayable)
            return result

        d = taskqueue.ThreadQueue.call(self, *args, **kw)
        if VERBOSE_QUEUE:
            self.callCounter += 1
            wrapped = self.callCounter % 1000
            print "> %d: %s %s" % (wrapped, str(args), str(kw))
            d.addCallback(done, wrapped)
        return d


class MockSiteGetter(object):
    pMembers = [
        ("/netacgi/nph-Parser\?patentnumber=\d{7}",
         "page_1.html"),

        ("/.+Sect1=PTO1&Sect2=HITOFF&d=PALL.+&s1=\d+.PN.&OS=PN/\d+&RS=PN/\d+",
         "page_2.html"),

        ("/\.piw\?Docid=\d+.+PageNum.+Input\=View\+first\+page",
        "page_3.html"),

        ("/.DImg\?Docid=US00%d&PageNum=(\d)&IDKey=.+&ImgFormat=tif" \
         % PATENT_NUMBER,
        "tmppat-%d-00\\1.tiff" % PATENT_NUMBER)
        ]

    aMembers = [
        ("/netacgi/nph-Parser\?Sect1=PTO2&Sect2=HITOFF"+\
         "&u=%2Fnetahtml%2FPTO%2Fsearch-adv.html&r=0&p=1&f=S&l=50"+\
         "&Query=DN%%2F%d&d=PG01" % (APP_NUMBER,),
         "page_1.html"),

        ("/netacgi/nph-Parser\?Sect1=PTO2&Sect2=HITOFF"+\
         "&u=%2Fnetahtml%2FPTO%2Fsearch-adv.html&r=1&p=1&f=G&l=50&d=PG01"+\
         "&S1=%d.PGNR.&OS=DN/%d&RS=DN/%d" % ((APP_NUMBER,)*3),
         "page_2.html"),

        ("/.aiw\?Docid=%d" % APP_NUMBER +\
         "&homeurl=http%3A%2F%2Fappft1.uspto.gov.+PageNum="+\
         "&Rtype=&SectionNum=&idkey=[0-9A-F]+",
         "page_3.html"),

        ("/.DImg\?Docid=us%dki&PageNum=(\d)&IDKey=[0-9A-F]+&ImgFormat=tif" \
         % APP_NUMBER,
        "tmppat-%d-00\\1.tiff" % APP_NUMBER)
        ]

    @classmethod
    def startQueue(cls):
        cls.Q = ThreadQueue()

    @classmethod
    def stopQueue(cls):
        if VERBOSE:
            print "\nStopping Queue"
        d = cls.Q.shutdown()
        d.addCallback(lambda _: delattr(cls, "Q"))
        return d

    def __init__(self, host, port=80):
        self.host, self.port = host, port
        self.calls = []
        if re.match("pat.+gov", host):
            tarName = "patent.tbz2"
            self.memberList = self.pMembers
            self.spec = patents.PatentFetcher.spec
        else:
            tarName = "app.tbz2"
            self.memberList = self.aMembers
            self.spec = patents.AppFetcher.spec
        dirPath = os.path.dirname(__file__)
        self.tarBall = tarfile.open(
            os.path.join(dirPath, tarName), 'r:bz2')
        self.members = self.tarBall.getnames()
        self.savedFiles = []
        self.trialTempDir = os.getcwd()

    def getSchemePart(self, spNumber):
        fh = self.tarBall.extractfile("schemepart_%d.txt" % spNumber)
        result = fh.read().strip()
        fh.close()
        return result

    def _getMember(self, schemePart):
        for regex, sub in self.memberList:
            m = re.match(regex, schemePart)
            if VERBOSE:
                print "\nMATCHING:\n%s\n\nagainst\n%s\n\n-> %s" \
                      % (schemePart, regex, m)
            if m is not None:
                member = m.expand(sub)
                return member
        raise Exception("No match for scheme part:\n\n'%s'\n" % schemePart)

    def _oops(self, failure):
        failure.printDetailedTraceback()
    
    @call
    def getPage(self, schemePart):
        def gotHandle(fh):
            html = fh.read()
            fh.close()
            if VERBOSE:
                print "\nHTML for member '%s':" % self.member, html, "\n\n"
            return html

        d = self.Q.call(self.tarBall.extractfile, self.member)
        d.addCallback(gotHandle)
        return d

    def setRegex(self, ID, regex):
        pass

    @call
    def searchPage(self, schemePart, regex):
        def gotHandle(fh, regex):
            html = fh.read()
            fh.close()
            if isinstance(regex, int):
                regex = self.spec[regex+2]
            m = re.search(regex, html)
            if VERBOSE:
                print "\nSEARCHING:\n\n", html, "\n\nAGAINST '%s'\n" % regex, "\nHAS MATCH: ", m.groups(), "\n\n"
            return m
        
        d = self.Q.call(self.tarBall.extractfile, self.member)
        d.addCallback(gotHandle, regex)
        return d
    
    @call
    def savePage(self, schemePart, filePath):
        fileDir = os.path.dirname(filePath)
        self.savedFiles.append(os.path.join(fileDir, self.member))
        return self.Q.call(self.tarBall.extract, self.member, fileDir)


class MockGetterFactoryMixin(object):
    def _siteGetterFactory(self, server=None):
        if not hasattr(self, 'getters'):
            self.getters = {}
        if server is None:
            server = self.spec[0]
        if server not in self.getters:
            self.getters[server] = MockSiteGetter(server)
        return self.getters[server]

class TestableFetcherBase(MockGetterFactoryMixin, patents.FetcherBase):
    pass

class TestablePatentFetcher(MockGetterFactoryMixin, patents.PatentFetcher):
    pass

class TestableAppFetcher(MockGetterFactoryMixin, patents.AppFetcher):
    pass


#--- Unit tests ---------------------------------------------------------------

class TestImagerator(TestCase):
    def setUp(self):
        MockSiteGetter.startQueue()
        self.getter = MockSiteGetter("patft.uspto.gov")
        firstPageSP = "/.DImg?Docid=US00%d" % PATENT_NUMBER +\
                      "&PageNum=1&IDKey=1FD7CA8B4446&ImgFormat=tif"
        self.trialTempDir = os.getcwd()
        self.i = patents.Imagerator(
            PATENT_NUMBER, self.trialTempDir,
            firstPageSP, PATENT_PAGES, self.getter)

    def tearDown(self):
        return MockSiteGetter.stopQueue()

    def _iterate(self):
        dList = []
        for d in self.i:
            dList.append(d)
        return defer.DeferredList(dList)

    def test_iterate(self):
        def doneIterating(null):
            files = self.getter.savedFiles
            self.failUnlessEqual(len(files), PATENT_PAGES)
            pattern = ".*tmppat\-%d+\-00[1-9]\.tiff" % PATENT_NUMBER
            for fileName in files:
                m = re.match(pattern, fileName)
                self.failIf(
                    m is None, "Improper image file name '%s'" % fileName)
                self.failUnless(
                    os.path.exists(fileName),
                    "File '%s' wasn't saved" % fileName)
        
        d = self._iterate()
        d.addCallback(doneIterating)
        return d

    def test_combine(self):
        def doneIterating(null):
            return self.i.combine()
        
        d = self._iterate()
        d.addCallback(doneIterating)
        return d

    def test_convert(self):
        def doneIterating(null):
            return self.i.combine()
        
        d = self._iterate()
        d.addCallback(doneIterating)
        d.addCallback(lambda _: self.i.convert())
        return d


class FetcherTC(TestCase):
    def setUp(self):
        MockSiteGetter.startQueue()
        self.trialTempDir = os.getcwd()
        if self.fetcherType == 'patent':
            self.fetcher = TestablePatentFetcher(self.trialTempDir)
        elif self.fetcherType == 'app':
            self.fetcher = TestableAppFetcher(self.trialTempDir)

    def tearDown(self):
        return MockSiteGetter.stopQueue()

    def _isPDF(self, filePath):
        def checkFile(result):
            return "PDF document" in result
        
        executable = procutils.which("file")[0]
        if not executable:
            raise ImportError("Can't locate 'file' executable")
        d = utils.getProcessOutput(executable, args=(filePath,))
        d.addCallback(checkFile)
        return d
    
    
class FetcherBaseMixin(object):
    fetcherType = 'patent'
    
    def test_getImageTools(self):
        def gotTools(tools):
            imageSchemePart, getter = tools
            if self.fetcherType == 'patent':
                re_SP = "/\.piw[^>]+"
                re_host = "patimg[a-z1-9\.]+"
                
            else:
                re_SP = "/\.aiw.+idkey\=[0-9A-F]{3,}"
                re_host = "aiw[a-z1-9\.]+"
            m = re.match(re_SP, imageSchemePart)
            self.failIf(
                m is None,
                "Improper image scheme part '%s'" % imageSchemePart)
            m = re.match(re_host, getter.host)
            self.failIf(
                m is None,
                "Getter set to improper host '%s'" % getter.host)
            # USED TO GENERATE schemepart_1.txt
            # fh = open(os.path.join(self.trialTempDir, "schemepart_1.txt"), 'w')
            # fh.write(imageSchemePart)
            # fh.close

        schemePart = self.fetcher.spec[1] % self.testPubNumber
        d = self.fetcher._getImageTools(schemePart)
        d.addCallback(gotTools)
        return d
        
    def test_getImagerator(self):
        def gotImagerator(i):
            self.failUnless(
                isinstance(i, patents.Imagerator),
                "Returned '%s', not an Imagerator" % repr(i))

        schemePart = self.fetcher._siteGetterFactory().getSchemePart(1)
        if self.fetcherType == 'app':
            server = patents.AppFetcher.spec[0]
        else:
            server = patents.PatentFetcher.spec[0]
        getter = MockSiteGetter(server)
        imageTools = (schemePart, getter)
        d = self.fetcher._getImagerator(imageTools, self.testPubNumber)
        d.addCallback(gotImagerator)
        return d


class TestFetcherBasePatent(FetcherBaseMixin, FetcherTC):
    fetcherType = 'patent'
    testPubNumber = PATENT_NUMBER
    

class TestFetcherBaseApp(FetcherBaseMixin, FetcherTC):
    fetcherType = 'app'
    testPubNumber = APP_NUMBER

        
class TestPatentFetcher(FetcherTC):
    fetcherType = 'patent'

    def test_fetchMock(self):
        def doneFetching(filePath):
            self.failUnless(
                filePath.endswith(".pdf"),
                "Mock patent fetch result should have PDF file extension")

        d = self.fetcher.fetch(PATENT_NUMBER)
        d.addCallback(doneFetching)
        return d

    def test_fetchReal(self):
        def doneFetching(filePath):
            d = self._isPDF(filePath)
            d.addCallback(
                self.failUnless, "Fetch didn't produce PDF of patent")
            return d

        fetcher = patents.PatentFetcher(self.trialTempDir)
        d = fetcher.fetch(PATENT_NUMBER)
        d.addCallback(doneFetching)
        return d
    

class TestAppFetcher(FetcherTC):
    fetcherType = 'app'

    def test_fetchMock(self):
        def doneFetching(filePath):
            self.failUnless(
                filePath.endswith(".pdf"),
                "Mock app fetch result should have PDF file extension")

        d = self.fetcher.fetch(APP_NUMBER)
        d.addCallback(doneFetching)
        return d

    def test_fetchReal(self):
        def doneFetching(filePath):
            d = self._isPDF(filePath)
            d.addCallback(
                self.failUnless, "Fetch didn't produce PDF of app")
            return d

        fetcher = patents.AppFetcher(self.trialTempDir)
        d = fetcher.fetch(APP_NUMBER)
        d.addCallback(doneFetching)
        return d
            
