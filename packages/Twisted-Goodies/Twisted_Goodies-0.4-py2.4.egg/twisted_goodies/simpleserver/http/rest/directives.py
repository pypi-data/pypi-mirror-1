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
Module for reStructuredText Directives

"""

import sre
from docutils import nodes
from docutils.parsers.rst import directives

import nevow.tags as T


class Manager:
    """
    I register reStructuredText directives (as d_* methods of a Directives()
    object) and provide lock/unlock methods for setting them up for per-page
    use
    """
    def __init__(self):
        """
        Constructs a separate button object for each instance and (just the
        first time) registers all of my d_* methods as rEST directive(s)
        """
        # Construct a new button object, every time
        button = Button(page.parentResource, bgColor='#FFFFFF')
        # Register directives, just the first time I'm instantiated as their
        # attributes are frozen anyhow
        if not self.__class__.buttonDict:
            myDirectives = Directives(self)
            self.directiveNames = [x.replace('d_','')
                                  for x in myDirectives.__class__.__dict__.keys()
                                  if str(x).startswith('d_')]
            for name in self.directiveNames:
                object = getattr(myDirectives, 'd_'+name)
                directives.register_directive(name, object)
        # I also store a reference to the page's ActiveConfig object for my
        # directives to obtain from me
        self.__class__.buttonDict[id(page)] = page.config, button

    def get(self, objectName):
        """
        Returns the named object, used by directives because their attributes
        are frozen when registered

        """
        pageID = self.__class__.pageID
        self.config, self.button = self.__class__.buttonDict[pageID]
        print "DEBUG dir: %s" % dir(self)
        return getattr(self, objectName)

    def lock(self, page):
        """
        Locks all instances of me to the supplied parent resource
        
        THREADS BEWARE
        """
        self.__class__.pageID = id(page)

    def unlock(self):
        """
        Unlocks (really just a feel-good placeholder for now)

        """
        self.__class__.pageID = None


class Directives:
    """
    I house custom reStructuredText directives as d_* methods.
    """
    # Compiled regexps I may use a lot
    rePatentNumber = sre.compile(r"[0-9],?[0-9]{3},?[0-9]{3}")

    def error(self, textProto, textTuple, *arg):
        """
        Generates a suitable error message from the supplied text
        
        """
        text = textProto % textTuple
        error = arg[8].reporter.error(
            text,
            nodes.literal_block(arg[6], arg[6]), line=arg[4])
        return [error]

    def parse(self, *arg):
        """
        Parses the args for a rEST directive function, returning a tuple with the
        first (only?) argument and the options dictionary
        
        """
        return arg[1][0], arg[2]


    #================ The directive methods (functions) ================

    def d_patent(self, *arg):
        """
        Returns a link to full text of a patent whose number is supplied
        
        """
        pn, opts = self.parse(*arg)
        if not self.rePatentNumber.match(pn):
            return self.error('"%s" is not a valid patent number',
                              pn, *arg)
        url = 'http://patft.uspto.gov/netacgi/nph-Parser?patentnumber=%s' \
              % pn.replace(',','')
        html = '<a href="%s">%s</a>' % (url, pn)
        return [nodes.raw('', html, format='html')]

    # Arguments: 1 required (patent number), none optional, no whitespace
    d_patent.arguments = (1, 0, 0)
    # Options: none yet (TODO: fulltext, pdf format)
    d_patent.options = {}
    # No content
    d_patent.content = False

