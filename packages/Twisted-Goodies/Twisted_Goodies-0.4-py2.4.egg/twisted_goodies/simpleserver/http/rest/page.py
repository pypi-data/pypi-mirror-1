# twisted_goodies.simpleserver.http:
# A virtual hosting twisted.web2 HTTP server that uses subdirectories for
# virtual host content. Subdirectories can be python packages providing dynamic
# content with a root resource object, or sources of static content.
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
Page Module

Provides per-page content and page-level utilities

"""

# Stdlib imports
import os.path as ospath
import os, sre
from shutil import copyfile
from HTMLParser import HTMLParser

# Package imports
from docutils.core import publish_string

# Module imports
from directives import Manager


class TagProcessor:
    """
    I provide a 'build' method for building text of opening tag strings based
    on supplied tag names and attributes

    """
    def patternToURL(self, pattern):
        """
        Attempts to translate a pattern to a local page URL by looking for a
        substring match in the name portion (not the suffix) of each local
        page's entry

        """
        url = None
        re = sre.compile('^[^,]*'+pattern.lower())
        for DLO in self.cPages:
            for name in DLO.values():
                if re.search(name.lower()):
                    null, url = self.parsePageEntry(name)
            if url is not None: break
        else:
            # No match found, return original pattern
            return pattern
        # Return URL generated for matching page
        return url

    def _test(self, *args):
        """
        Indicates pattern match

        """
        if self.tag == args[0]:
            if len(args) > 1 and self.name != args[1]:
                return False
            else:
                return True
        else:
            return False
        
    def build(self, tag, attrs):
        """
        Builds an opening tag with (possibly modified) attributes

        """
        text = '<' + tag
        self.tag = tag; self.attrs = attrs
        # Attribute modification
        for self.name, value in self.attrs:
            if self._test('a', 'href') and value.find('.') == -1:
                # Likely local page reference: look it up and translate it
                value = self.patternToURL(value)
            text += " %s=\"%s\"" % (self.name, value)
        return text + '>'
        

class Parser(HTMLParser):
    """
    I am a customized HTML parser that converts full-page HTML output (e.g.,
    from a docutils reStructuredText parser) into a dictionary of DIVs for my
    client to position wherever is desired

    """
    def __init__(self, buildMethod):
        """
        Instantiates me with a reference to a build method of a TagProcessor
        object, which I use for applying optional paragraph justification and
        translating local page references

        """
        HTMLParser.__init__(self)
        self.buildOpenTag = buildMethod
    
    def setDict(self, divDict):
        """
        Provides me with a reference to my client's current DIV dictionary,
        into which I place my results

        """
        self.ignoredTags = ('div',)
        self.divs = divDict
        self.key = None
        self.tag = [] # Empty tag stack
        self.flags = {}

    def first(self, flag):
        """
        Indicate first check for flag

        """
        if flag in self.flags:
            return False
        else:
            self.flags[flag] = 1
            return True
        
    def handle_starttag(self, tag, attrs):
        """
        Points the key of my client's DIV dictionary to the appropriate DIV, if
        the tag indicates such. Otherwise, if there is a valid key, sends the
        open tag to the text sink for that dictionary entry.

        """
        if tag == 'title':
            self.key = 'heading'
        elif tag == 'body':
            self.key = 'main'
        elif tag == 'h1':
            # Ignore H1 (duplicate of page title)
            self.key = None
        elif self.key:
            if tag not in self.ignoredTags:
                # Push new opening tag onto stack
                self.tag.append(tag)
                # Reproduce opening tag with any attributes present and/or
                # added below
                if self.key == 'main' and self.first('para'):
                    # First paragraph in main has no top margin
                    attrs.append(('id', 'first'))
                self.divs[self.key] += self.buildOpenTag(tag, attrs)
            return
        self.divs[self.key] = ''

    def handle_data(self, data):
        """
        If there is a valid key, sends the data to the text sink for that
        dictionary entry.

        """
        if self.key:
            self.divs[self.key] += data

    def handle_charref(self, data):
        """
        If there is a valid key, sends the original HTML for the special
        character to the text sink for that dictionary entry.

        """

        if self.key:
            self.divs[self.key] += '&#%s;' % data

    def handle_entityref(self, data):
        """
        If there is a valid key, sends the original HTML for the special
        entity to the text sink for that dictionary entry.

        """
        if self.key:
            self.divs[self.key] += '&%s;' % data

    def handle_endtag(self, tag):
        """
        Disables the key of my client's DIV dictionary if the tag indicates
        such. Otherwise, if there is a valid key, sends the ending tag to the
        text sink for that dictionary entry.

        """
        if tag == 'title':
            self.key = None
        elif tag == 'body':
            self.key = None
        elif tag == 'h1':
            # Done ignoring H1
            self.key = 'main'
        elif self.key and tag not in self.ignoredTags:
            self.divs[self.key] += '</%s>' % self.tag.pop()
        

class Page(ImageResource):
    """
    I handle the generation of page objects from content files. I subclass
    ImageResource because one of the page objects I can generate is an image.

    """
    blank = '&nbsp;'
    pageGroup = None
    pageNumber = None
    specialPageName = None
    
    def __init__(self, config, parentResource, *arg, **kw):
        """
        Instantiates me with a reference to an ActiveConfig object, from which
        I obtain references to automatically-updated configuration data
        objects, a parentResource object into which I register my images, and a
        directives object that I lock to my parentResource when doing
        reStructuredText rendering

        Builds a DLO of page-global config options and a dictionary-like LLO
        for each group of pages in the page table, all with independent
        caches. (Both objects are shared with a TagProcessor instance.)
        
        """
        # First process pwd option if defined
        if 'pwd' in kw:
            self.pwd = kw.pop('pwd')
        else:
            self.pwd = '/var/www-dn'
        # Then do my base class init with any args, kws provided
        ImageResource.__init__(self, parentResource, *arg, **kw)
        # My config object
        self.config = config
        # Location of page files
        self.dir = ospath.dirname(config.file)
        # My directives manager object
        self.directives = Manager(self)
        # My DLOs
        self.cPage = config.getSection('Page')
        self.cPages = config.getSectionList('Group',
                                            dictAccess=True,
                                            independent=True)
        self.cLayout = config.getSection('Layout')
        # Instantiate an html parser for picking out sections from
        # reStructuredText output
        self.parser = Parser(TagProcessor(self).build)

    def pageGroupNumber(self, name, template=False):
        """
        Returns a tuple with page group and number if the name matches. Raises
        an exception if not.

        The default is to match the page name, but the template name can be
        matched instead if template=True

        """
        number = None
        if not template:
            name = self.pageName(name)
        for group, DLO in self.cPages.iteritems():
            for key, rawName in DLO.items():
                nameList = rawName.split(',')
                if template and len(nameList) == 1:
                    # If seeking a template, add default as needed
                    nameList.append('default')
                elif not template:
                    # If seeking a name, transform each one searched
                    nameList[0] = self.pageName(nameList[0])
                # Assign page number if name/template matches
                if nameList[template].strip() == name:
                    number = key
            if number is not None: break
        else:
            return (None, None)
        return group, number

    def isCurrent(self, name):
        """
        Indicates whether the supplied page name is an active page or heading

        """
        if self.pageGroup is None or self.pageNumber is None:
            return False
        else:
            activeName = self.cPages.get(
                self.pageGroup)[self.pageNumber].split(',')[0]
            return (name == activeName)

    def parsePageEntry(self, item):
        """
        Parses a page entry to return (name, url)

        """
        if item == self.blank:
            # Blank item with no link target
            return item, ''
        pair = [x.strip() for x in item.split(',')]
        if len(pair) == 1:
            # Default templated link target
            url = 'default'
        elif pair[1].startswith('http://'):
            # Fully specified link target
            return tuple(pair)
        else:
            # Specified-template link target
            url = pair[1]
        if url != 'home':
            # The 'home' template permits no per-page distinctions
            url = url+'/'+self.pageName(pair[0])+'.html'
        return pair[0], url

    def setSpecialPage(self, sanitizedName):
        """
        Sets the page name to a special, pre-sanitized one outside the
        group/number hierarchy.

        This setter is mutually exclusive with setPage.

        """
        self.pageGroup, self.pageNumber = None, None
        self.specialPageName = sanitizedName

    def setPage(self, *arg):
        """
        Sets the page group and number for my page operations, either from a
        page name (single arg) or a page group and number (two args). Returns
        with error status.

        This setter is mutually exclusive with setSpecialPage.

        """
        if len(arg) == 1:
            pageGroup, pageNumber = self.pageGroupNumber(arg[0])
            if pageGroup is None or pageNumber is None:
                self.pageGroup, self.pageNumber = None, None
                return True
        elif len(arg) == 2:
            pageGroup, pageNumber = arg
            if pageNumber == 0:
                pageNumber = 'heading'
        else:
            raise TypeError, \
                  '.setPage() method takes 1-2 arguments (%d given)' % len(arg)
        # Coerce non-strings to strings EXCEPT None objects
        for srcValue, destName in ((pageGroup, 'pageGroup'),
                          (pageNumber, 'pageNumber')):
            if srcValue is None:
                x = None
            else:
                x = str(srcValue)
            setattr(self, destName, x)
        self.specialPageName = None
        return False

    def pageName(self, *arg):
        """
        Computes a sanitized but still recognizable page name based on its
        group, number, and link name. If an argument is supplied, use it as the
        page name instead of looking one up.

        """
        if len(arg):
            linkName = arg[0]
        elif self.pageGroup is not None and self.pageNumber is not None:
            linkName = self.cPages.get(self.pageGroup)[self.pageNumber]
            linkName = linkName.split(',')[0]
        elif self.specialPageName is not None:
            return self.specialPageName
        else:
            return ''
        # Build a page filename based on link name
        pageName = ''
        for word in linkName.split():
            alphaPart = sre.search('[a-zA-Z]*', word).group()
            if len(alphaPart):
                pageName += alphaPart.replace(alphaPart[0],
                                              alphaPart[0].upper(), 1)
        return pageName

    def pageFile(self, pageName=None):
        """
        Returns a dict with info about the page file, keyed as follows:

        name    = pageName
        mtime   = modification time
        path    = path (directory/name.extension)
        type    = .html (as-is) or .txt (rEST for parsing)

        Uses the current sanitized name for the current page file, unless
        pageName is provided in which case <pageName>.html <pageName>.txt is
        used, in that order of preference
        
        """
        if pageName is None:
            name = self.pageName()
        else:
            name = pageName
        fileInfo = {'name':name}
        for fileType in ('html', 'txt'):
            path = ospath.join(self.dir, name+'.'+fileType)
            if ospath.exists(path):
                fileInfo['mtime'] = os.stat(path).st_mtime
                break
        else:
            fileInfo['mtime'] = None
        for name, value in (('path', path),
                            ('type', fileType)):
            fileInfo[name] = value
        return fileInfo

    def pageFileRead(self, pageName=None):
        """
        Returns the contents of a page file. If none exists, creates one
        with page template content and returns that.

        The page files go in the same directory as the config object's
        configuration file, as determined from the config object's file
        attribute.

        Uses the current sanitized name for the current page file, unless
        pageName is provided in which case <pageName>.html <pageName>.txt is
        used, in that order of preference

        """
        fileInfo = self.pageFile(pageName=pageName)
        path = fileInfo['path']
        if not ospath.exists(path):
            # No page file yet, use page template
            copyfile(ospath.join(self.pwd, 'page.txt'), path)
        fh = open(path)
        fileInfo['data'] = fh.read()
        fh.close()
        return fileInfo

    def pageCache(self, *arg):
        """
        If an argument is supplied, sets the page cache dictionary item for
        this page's group DLO to the object referenced by the argument.
        
        With no argument, returns the cached contents of the specified page if
        the page group configuration has not changed and the source text file
        for the page is not newer than it was when the page was last
        rendered. Otherwise, returns None.

        """
        pageGroupCache = self.cPages.get(self.pageGroup).getCache()
        if len(arg):
            if pageGroupCache is None:
                pageGroupCache = {}
                pageGroupCache[self.pageNumber] = arg[0]
            self.cPages.get(self.pageGroup).setCache(pageGroupCache)
        else:
            if pageGroupCache is None:
                return None
            elif pageGroupCache.has_key(self.pageNumber):
                cacheTime, cacheContents = pageGroupCache[self.pageNumber]
                mtime = self.pageFile()['mtime']
                if mtime and cacheTime >= mtime:
                    return cacheContents
                else:
                    return None
            else:
                return None

    def getHTML(self, pageName, divName=None, literal=False):
        """
        Returns HTML of the selected content page, which is generated from a
        plain-text file in reStructuredText format unless an .html file with
        the sanitized page name is available, in which case that .html file is
        returned as-is.

        """
        if literal:
            error = False
            literalPageName = pageName
        else:
            error = self.setPage(pageName)
            literalPageName = None
        if error:
            self.setSpecialPage(pageName)
        # Page caching is disabled to avoid missing updated graphics
        # See SVN:62 for cache code
        divs = {}
        fileInfo = self.pageFileRead(pageName=literalPageName)
        if fileInfo['type'] == 'html':
            html = fileInfo['data']
        else:
            # No one else can use their instances of Manager() while I'm
            # using mine (due to central registration)
            self.directives.lock(self)
            html = publish_string(
                fileInfo['data'],
                writer_name='html',
                settings_overrides={'--footnote-references':'brackets'})
            self.directives.unlock()
        # Give the parser a reference to our DIV dictionary
        self.parser.setDict(divs)
        # Feed the HTML to the parser
        self.parser.feed(html)
        # Force the parser to fill our DIV dictionary with parsed HTML
        self.parser.close()
        if divName:
            return divs[divName]
        else:
            return divs

    def getImage(self, pageName, type):
        """
        Returns a PIL image object for .registerImage() to make a Nevow
        static.Data object from

        """
        pagePath = self.pageFile(pageName)['path']
        imagePath = ospath.splitext(pagePath)[0] + '.' + type
        if not ospath.exists(imagePath):
            # Oops, I have no image file to serve so come up with a placeholder
            # to alert the designer without incurring an error
            # TODO
            raise IOError, "No image file '%s' found" % imagePath
        # I have an image file to serve, so load it
        image = Image.open(imagePath)
        # Config-controlled per-site image processing
        oldWidth, oldHeight = image.size
        newWidth = int(self.cLayout['image width'])
        newHeight = int(round(oldHeight * float(newWidth)/float(oldWidth)))
        return image.resize((newWidth, newHeight), Image.ANTIALIAS)

        
__all__ = ["Page"]
