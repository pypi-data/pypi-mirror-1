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
Utility stuff
"""

import traceback
from twisted.web2 import static


def showException(theTraceback=None):
    """
    Returns a C{static.Data} resource showing details about the last
    exception.

    """
    if theTraceback is None:
        theTraceback = traceback.format_exc()
    
    title = "Error importing index.py"
    html = ["<html>"]
    html.append(
        "<head><title>%s</title></head>" % title)
    html.append(
        "<body><h1>%s</h1>" % title)
    html.append(
        "<p><pre>%s</pre></p>" % theTraceback)
    html.append("</body></html>")
    exceptionResource = static.Data(data="\n".join(html), type='text/html')
    exceptionResource.addSlash = True
    return exceptionResource



