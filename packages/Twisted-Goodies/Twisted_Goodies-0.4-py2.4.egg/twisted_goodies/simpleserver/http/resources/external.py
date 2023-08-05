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
External web resources
"""

import trac.web.main
import nevow
from zope.interface import implements
from twisted.internet import reactor, protocol, ssl
from twisted.web2 import iweb
import twisted.web2.client.http as chttp

from twisted_goodies.simpleserver.http import wsgi, util


class TracResource(wsgi.WSGIResource):
    """
    I provide a Trac site for a specified path via a WSGI gateway.

    The WSGI application is L{trac.web.main.dispatch_request}, the 'Main entry
    point for the Trac web interface.' It accepts the following required
    WSGI-compliant parameters:
    
        - B{environ:} The WSGI environment dict
        - B{start_response:} The WSGI callback for starting the response

    The WSGI environment value 'trac-env_path' is set to the path provided to
    my constructor as its first argument. You can supply additional WSGI
    environment values via the I{env} option.
    """
    def __init__(self, path, env={}):
        self.path, self.env = path, env
        wsgi.WSGIResource.__init__(self, self.tracApplication)

    def tracApplication(self, environ, start_response):
        """
        This method is the callable object that provides access to my
        particular Trac environment via WSGI.
        """
        environ['trac.env_path'] = self.path
        environ.update(self.env)
        return trac.web.main.dispatch_request(environ, start_response)


class NevowResource(wsgi.WSGIResource):
    """
    I provide a Nevow site for a specified path via a WSGI gateway.

    The WSGI application is L{nevow.wsgi.WSGIRequest}. It takes the required
    WSGI-compliant arguments I{environ}, the WSGI environment dict, and
    I{start_response}, the WSGI callback for starting the response.
    """
    def __init__(self, path):
        self.path = path
        wsgi.WSGIResource.__init__(self, self.nevowApplication)

    def nevowApplication(self, environ, start_response):
        """
        This method is the callable object that provides access to my
        particular Nevow environment via WSGI.
        """
        # environ modifications?
        return nevow.wsgi.WSGIRequest(environ, start_response)


class ProxyResource(object):
    """
    I provide proxied resources from another HTTP server.

    When the first instance for a particular upstream server is constructed,
    the client protocol for proxy connections to its I{upstreamHost} and
    I{upstreamPort} is created and cached, with an I{SSL} option for securing
    those connections.
    """
    implements(iweb.IResource)

    upstreamSpecs = {}

    def __init__(self, upstreamHost, upstreamPort, SSL=False):
        self.cacheKey = (upstreamHost, upstreamPort, SSL)
        if self.cacheKey not in self.upstreamSpecs:
            thisProtocol = protocol.ClientCreator(
                reactor, chttp.HTTPClientProtocol)
            specs = {'protocol': thisProtocol,
                     'host': upstreamHost,
                     'port': upstreamPort}
            if SSL:
                specs['context'] = ssl.ClientContextFactory()
            self.upstreamSpecs[self.cacheKey] = specs

    def renderHTTP(self, request):
        """
        Returns a deferred to the HTTP rendered by forwarding a client version
        of the supplied I{request} to another HTTP server. Any I{:<port}
        substring appearing in the response from that server is removed to
        ensure that further requests are proxied through me.
        """
        def gotResponse(response):
            location = response.headers.getHeader('location')
            if location is not None:
                newLocation = location.replace(":%d" % specs['port'], "")
                response.headers.setHeader('location', newLocation)
            return response

        def connected(protocolObject):
            self.uri = request.uri
            newRequest = chttp.ClientRequest(
                request.method, request.uri, request.headers, request.stream)
            return protocolObject.submitRequest(
                newRequest).addCallbacks(gotResponse)

        specs = self.upstreamSpecs[self.cacheKey]
        if 'context' in specs:
            d = specs['protocol'].connectSSL(
                specs['host'], specs['port'], specs['context'])
        else:
            d = specs['protocol'].connectTCP(specs['host'], specs['port'])
        d.addCallback(connected)
        return d

    def locateChild(self, request, segments):
        return self, ()
