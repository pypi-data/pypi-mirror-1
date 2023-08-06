"""
twisted_goodies.simpleserver.http

A virtual hosting twisted.web2 HTTP server that uses subdirectories for
virtual host content. Subdirectories can be python packages providing dynamic
content with a root resource object, or sources of static content.

Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the file COPYING for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 51
Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
"""

from twisted.web2 import server, channel

import startup


def factory(master, config):
    baseDir = config['base dir']
    defaultHost = config['default host']
    root = startup.VHostSiteRoot(baseDir, defaultHost)
    return channel.HTTPFactory(server.Site(root))
