# -*- mode:python -*-
#
# SIMPLESERVER: (Hopefully) dirt-simple twisted-based Internet servers
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

from twisted_goodies.simpleserver.service import MasterService

# The server configuration file
CONFIG = '/etc/simpleserver/server.conf'

# The master service runs everything and provides the application object
master = MasterService(CONFIG)
application = master.application
