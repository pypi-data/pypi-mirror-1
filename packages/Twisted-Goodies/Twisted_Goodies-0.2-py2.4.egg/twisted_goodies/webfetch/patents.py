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
Fetching of U.S. patents and published patent applications from the USPTO web
server.
"""

import os.path, re
from twisted.internet import defer, utils
from twisted.python import procutils

from twisted_goodies.webfetch import FetchFailure, SiteGetter


# Required Executables
TIFF2PDF = procutils.which("tiff2pdf")[0]
if not TIFF2PDF:
    raise ImportError("Can't locate tiff2pdf executable")

TIFFCP = procutils.which("tiffcp")[0]
if not TIFFCP:
    raise ImportError("Can't locate tiffcp executable")


class Imagerator(object):
    """
    I do the heavy lifting for acquiring and assembling the images that make up
    a patent or patent application PDF.

    Instantiate me with the following arguments:

        - The directory I{dirPath} in which the temporary files and final
          output PDF file should be written.

        - The I{initialSchemePart} of the URL used to access the TIFF source
          images.

        - The number of image pages I{numPages}.

        - An instance I{getter} of L{SiteGetter} for obtaining the TIFF source
          images.

    Once you've constructed an instance of me, iterate over that instance to
    fetch all the TIFF source images.  (The iterated output isn't important.)
    Then call L{combine} to combine all the images into a single TIFF
    file. When that's done, call L{convert} with the publication number of the
    patent or patent application to convert the TIFF file into a PDF.
    """
    def __init__(self, pubNum, dirPath, initialSchemePart, numPages, getter):
        # Basis for TIFF image and final output files
        self.pubNum = pubNum
        self.dirPath = dirPath
        # TIFF scheme part left and right segments
        self.left, self.right = re.split(
            "PageNum\=1", initialSchemePart.replace("\n", ""))
        # Page files
        self.pageFiles = []
        self.numPages = numPages
        # Image file getter
        self.getter = getter

    def _imageFile(self, page=0):
        """
        Returns a suitable path for a TIFF source image file of the specified
        I{page}, or the combined TIFF file if no page number is supplied.
        """
        fileName = "tmppat-%d-%03d.tiff" % (self.pubNum, page)
        return os.path.join(self.dirPath, fileName)

    #--- Iterator implementation ----------------------------------------------

    def __iter__(self):
        return self

    def next(self):
        page = len(self.pageFiles)+1
        if page > self.numPages:
            del self.getter
            raise StopIteration()
        schemePart = "%sPageNum=%d%s" % (self.left, page, self.right)
        filePath = self._imageFile(page)
        self.pageFiles.append(filePath)
        return self.getter.savePage(schemePart, filePath)

    #--- Public methods -------------------------------------------------------

    def combine(self):
        """
        Combines the TIFF source image files into a single TIFF file, deleting
        the source files when done.

        @return: A deferred that fires when the destination file is accessible.
        """
        def cleanup(code):
            if code:
                raise OSError("Error running TIFFCP")
            for filePath in self.pageFiles:
                os.remove(filePath)
            del self.pageFiles
        
        args = self.pageFiles + [self._imageFile()]
        d = utils.getProcessValue(TIFFCP, args)
        d.addCallback(cleanup)
        return d

    def convert(self):
        """
        Converts the combined TIFF file into a PDF whose name is based on the
        validated publication number supplied to my constructor. Deletes the
        TIFF file when done.
        
        @return: A deferred that fires with the path of the PDF file when it is
          accessible.
        
        """
        def cleanup(code):
            if code:
                raise OSError("Error running TIFF2PDF")
            os.remove(destFile)
            return pdfFile

        pdfFile = os.path.join(self.dirPath, "US%d.pdf" % self.pubNum)
        destFile = self._imageFile()
        args = ['-p', 'letter', '-o', pdfFile, destFile]
        d = utils.getProcessValue(TIFF2PDF, args)
        d.addCallback(cleanup)
        return d
    

class FetcherBase(object):
    """
    I am an abstract class containing methods and attributes common to
    L{PatentFetcher} and L{AppFetcher}.
    
    The C{filePath} and C{Fetch} methods are called with the publication number
    of the U.S. patent or published patent application as their sole argument.
    The number must have 7 digits for a patent, and 11 digits for a published
    application.  The argument can be supplied as an integer or a string with
    or without a prepended 'US' and commas.
    """
    # Number of pages extraction
    re_num_pages = re.compile("\-{2,}\ +NumPages\=(\d+)\ +\-{2,}")

    # Initial image page source extraction
    re_tiff_src = re.compile(
        "<embed\ src\=\"(/\.DImg\?Docid\=[uU][sS]\d+[ki\n]*&PageNum\=1&\n?"+\
        "IDKey=[0-9A-F]+\n?&ImgFormat\=tif)")
    
    def __init__(self, dirPath):
        self.dirPath = dirPath
        getter = self._siteGetterFactory()
        for k, regex in enumerate(self.spec[2:]):
            getter.setRegex(k, regex)

    def _siteGetterFactory(self, server=None):
        if not hasattr(self, 'getters'):
            self.getters = {}
        if server is None:
            server = self.spec[0]
        if server not in self.getters:
            self.getters[server] = SiteGetter(server)
        return self.getters[server]

    def _getImageTools(self, schemePart):
        """
        Returns a deferred that fires with a tuple of objects that serve as
        tools for fetching the source TIFF files for the document. They are:

            - An I{imageSchemePart} string defining the schema part of a URL
              for the initial source TIFF file.

            - An instance of L{SiteGetter} for the server of the TIFF files.
            
        """
        def first(m, getter):
            if m is None:
                return FetchFailure("Error isolating URL from results page")
            fulltextURL = m.group(1)
            return getter.searchPage(fulltextURL, 1)

        def second(m):
            if m is None:
                return FetchFailure(
                    "Error isolating image server and scheme part "+\
                    "from fulltext page")
            imageServer, imageSchemePart = m.group(1, 2)
            host = imageServer.split(":")[0]
            getter = self._siteGetterFactory(host)
            return imageSchemePart, getter

        getter = self._siteGetterFactory()
        d = getter.searchPage(schemePart, 0)
        d.addCallback(first, getter)
        d.addCallback(second)
        return d

    def _getImagerator(self, imageTools, validatedPubNumber):
        """
        Returns an instance of L{Imagerator} that is used to fetch the source
        TIFF files and compile them into a PDF document.
        """
        def gotImagePage(html):
            m = self.re_num_pages.search(html)
            if m is None:
                return FetchFailure("Error obtaining number of pages")
            numPages = int(m.group(1))
            m = self.re_tiff_src.search(html)
            if m is None:
                return FetchFailure("Error obtaining TIFF file URL")
            tiff_src = m.group(1)
            return Imagerator(
                validatedPubNumber, self.dirPath, tiff_src, numPages, getter)

        schemePart, getter = imageTools
        return getter.getPage(schemePart).addCallback(gotImagePage)

    @defer.deferredGenerator
    def _getImagePages(self, imagerator):
        """
        Runs the supplied I{imagerator} instance to generate the desired PDF
        document, returning a deferred that fires with the I{filePath} of the
        PDF when it is accessible.
        """
        # Fetch TIFF images
        for d in imagerator:
            yield defer.waitForDeferred(d)
        # Combine them into one and clean up temp files
        yield defer.waitForDeferred(imagerator.combine())
        # Convert into PDF and clean up combination TIFF file
        wfd = defer.waitForDeferred(imagerator.convert())
        yield wfd
        # Conclude with the PDF file path
        filePath = wfd.getResult()
        yield filePath

    def shutdown(self):
        """
        Shuts down all my active site getters, returning a deferred
        that fires when done.
        """
        dList = []
        for getter in self.getters.itervalues():
            dList.append(getter.shutdown())
        return defer.DeferredList(dList)

    def filePath(self, pubNumber):
        """
        Returns the path of an archived PDF copy of the specified patent or
        published application, or C{None} if no such copy exists.
        """
        fileName = "US%d.pdf" % pubNumber
        thePath = os.path.join(self.dirPath, fileName)
        if os.path.exists(thePath):
            return thePath

    def fetch(self, pubNumberString, update=False):
        """
        Fetches a PDF copy of the specified U.S. patent or published
        application, returning a deferred that fires with the path of the PDF
        copy once it is accessible.

        If the PDF copy already exists, nothing is fetched, unless I{update} is
        set C{True}.
        """
        pubNumber = self.parsePubNumber(pubNumberString)
        if pubNumber:
            pubPath = self.filePath(pubNumber)
            if pubPath:
                return defer.succeed(pubPath)
            schemePart = self.spec[1] % pubNumber
            d = self._getImageTools(schemePart)
            d.addCallback(self._getImagerator, pubNumber)
            d.addCallback(self._getImagePages)
            return d


class PatentFetcher(FetcherBase):
    """
    I provide PDF copies of U.S. patents based on TIFF source files
    fetched from the USPTO web servers.
    """
    spec = (
        # The patent server
        "patft.uspto.gov",
        # The prototype scheme part of the initial search page
        "/netacgi/nph-Parser?patentnumber=%d",
        # Fulltext URL extraction
        "URL\=(/netacgi/nph-Parse.+?)\">",
        # Image server and scheme part extraction
        "a\ href\=http://(patimg.+)(/\.piw.+?)>",
        )

    def parsePubNumber(self, pubNumberString):
        """
        Validates and standardizes U.S. patent publication numbers.
        """
        pn = str(pubNumberString)
        m = re.match("(US\s?|U.S.\s|)(\d),?(\d{3}),?(\d{3})(\D|$)", pn)
        if m:
            return int(''.join(m.group(2,3,4)))


class AppFetcher(FetcherBase):
    """
    I provide PDF copies of U.S. published patent applications based
    on TIFF source files fetched from the USPTO web servers.
    """
    spec = (
        # The patent application server
        "appft1.uspto.gov",
        # The prototype scheme part of the initial search page
        "/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF" +\
        "&u=%%2Fnetahtml%%2FPTO%%2Fsearch-adv.html&r=0&p=1&" +\
        "f=S&l=50&Query=DN%%2F%d&d=PG01",
        # Fulltext URL extraction
        "HREF\=(/netacgi/nph-Parse.+?)\"?>",
        # Image server and scheme part extraction
        "a\s+href\=http://(aiw.+)(/\.aiw\?.+?idkey\=[0-9A-F]+)",
        )

    def parsePubNumber(self, pubNumberString):
        """
        Validates and standardizes U.S. patent application publication numbers.
        """
        pn = str(pubNumberString)
        m = re.match("(US)?\s?(\d{4})/?(\d{7})(\D|$)", pn)
        if m:
            return int(''.join(m.group(2,3)))
