#!/usr/bin/env python
#
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

NAME = "Twisted-Goodies"


### Imports and support
import ez_setup, postsetup
ez_setup.use_setuptools()
from setuptools import setup, find_packages


### Define setup options
kw = {'version':'0.3',
      'license':'GPL',
      'platforms':'OS Independent',

      'url':"http://foss.eepatents.com/%s/" % NAME,
      'author':'Edwin A. Suominen',
      'author_email':'ed@eepatents.com',
      
      'maintainer':'Edwin A. Suominen',
      'maintainer_email':'ed@eepatents.com',
      
      'packages':find_packages(exclude=["*.test"]),
      'scripts':['pat2pdf', 'ndm'],
      
      'zip_safe':True
      }

kw['keywords'] = [
    'Twisted', 'asynchronous', 'threads',
    'taskqueue', 'queue', 'priority', 'tasks', 'jobs',
    'cluster', 'clustering', 'parallel', 'grid',
    'web', 'fetch', 'patent', 'wget']

kw['classifiers'] = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Object Brokering',
    'Topic :: System :: Distributed Computing',
    'Topic :: Terminals :: Terminal Emulators/X Terminals',
    'Topic :: Desktop Environment :: Window Managers',
    ]

kw['description'] = " ".join("""
Asynchronous task queueing, HTTP fetching, cluster management, and other
goodies for the Twisted framework.
""".split("\n"))

kw['long_description'] = """
The Twisted (TM) asynchronous processing framework is made even more powerful
with this package of goodies:

+---------------+-------------------------------------------------------------+
| Sub-Package   | Description                                                 |
+===============+=============================================================+
| taskqueue     | Asynchronous task queueing with a powerful worker/manager   |
|               | interface                                                   |
+---------------+-------------------------------------------------------------+
| asyncluster   | Asynchronous operation of a computing cluster with a Node   |
|               | Display Manager (NDM) that allows regular workstation usage |
|               | of cluster nodes with computing jobs running behind the     |
|               | scenes.                                                     |
+---------------+-------------------------------------------------------------+
| webfetch      | Fetching of web server content including PDFs of patent and |
|               | published patent applications from the USPTO servers.       |
+---------------+-------------------------------------------------------------+
| misc          | Miscellaneous goodies, including a deferred tracker for     |
|               | waiting on the firing of one or more deferreds without      |
|               | needing references to them.                                 |
+---------------+-------------------------------------------------------------+

Twisted-Goodies is maintained and licensed separately from the Twisted
framework. The name is used by permission.
"""

### Finally, run the setup
setup(name=NAME, **kw)
postsetup.run("daemon", "daemon")

