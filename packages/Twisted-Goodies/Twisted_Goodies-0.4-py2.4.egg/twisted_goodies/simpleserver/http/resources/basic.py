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
Basic resources
"""

from twisted.internet import defer
from twisted.web2 import http, http_headers
from twisted.web2.resource import Resource
from nevow import flat, tags as T

from twisted_goodies.simpleserver.http import util


class StanResource(Resource):
    """
    I provide the foundation for you to write a C{render} method that simply
    returns a Stan document.

    I take care of flattening the Stan document that your C{render} method
    returns and turning it into a L{twisted.web2.http.Response}, even if your
    Stan tags have deferreds.

    You can include a C{<style>} block in the your document's HTML by setting
    my C{.style} attribute to a dictionary that contains definitions for CSS
    class or ID attributes. Each definition is itself a dictionary for one CSS
    class or ID with entries containing CSS properties and their values. A
    definition whose key starts with a capital letter is for a CSS class,
    otherwise it's for an ID.
    """
    def html(self, text):
        html = ' '.join([x.strip() for x in text.split('\n')])
        return T.xml(html)

    def render_head(self, ctx, data):
        """
        Renders the C{<head>} block of the HTML I return based on special
        attributes C{.title} and C{.style} that may or may not have been set.
        """
        # Start with Title...
        tags = [T.title[getattr(self, 'title', "Untitled")]]
        # Then Style...
        styleDict = getattr(self, 'style', None)
        if isinstance(styleDict, dict):
            styleLines = [""]
            for styleName, properties in styleDict.iteritems():
                if styleName == styleName.capitalize():
                    styleLines.append("%s {" % styleName)
                else:
                    styleLines.append("#%s {" % styleName)
                for name, value in properties.iteritems():
                    styleLines.append("\t%s: %s;" % (name, value))
                styleLines.extend(["}", ""])
            tags.append(T.style["\n".join(styleLines)])
        # All done
        return tags

    def render(self, request):
        raise NotImplementedError(
            "Must provide a render method that returns Stan of an HTML body")

    def http_GET(self, request):
        """
        Override to L{RenderMixin.http_GET} that flattens a Stan document
        representing the <body> block of my HTML and generates a complete
        L{twisted.web2.http.Response} based on it.

        You can return either an instance of C{T.body} or the tags inside it.
        """
        def gotHTML(html):
            return http.Response(
                200,
                {'content-type': http_headers.MimeType('text', 'html')}, html)

        def oops(failure):
            return util.showException(failure.getTraceback())

        try:
            stanBody = Resource.http_GET(self, request)
        except:
            return util.showException()
        else:
            if getattr(stanBody, 'title', lambda : "")() != "Body":
                stanBody = T.body[stanBody]
            stanHTML = T.html[T.head(render=self.render_head), stanBody]
            d = defer.maybeDeferred(flat.flatten, stanHTML)
            d.addCallbacks(gotHTML, oops)
            return d
