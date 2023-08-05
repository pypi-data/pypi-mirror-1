"""
simpleserver

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

import pwd, grp, os, os.path, imp
import configobj, pkg_resources
from twisted.internet import reactor, ssl, defer
from twisted.cred import checkers
from twisted.names import client
from twisted.application import internet, service


class MasterService(service.Service):
    """
    I am the chief executive for all simple services.

    I instantiate a C{twisted.application.service.Application} object with a
    service collection, of which I am the first memeber. All your C{twistd}
    needs to do is instantiate me and get a reference to the application object
    via my I{application} attribute.

    @ivar application: A C{twisted.application.service.Application}
      object that I instantiate and that represents the entire server.

    """
    def __init__(self, configPath):
        """
        I am constructed with the path of the server configuration file.
        """
        # Everything starts with the server-wide config file
        self._loadConfig(configPath)
        # The user and group to run as in non-privileged mode
        try:
            self.uid = pwd.getpwnam(self.config['user'])[2]
            self.gid = grp.getgrnam(self.config['group'])[2]
        except:
            raise OSError("Desired user or group not defined")
        # The credentials checker for all services
        self.checker = checkers.FilePasswordDB(self.config['passwd'])
        # Set up the application and its service collection
        self.application = service.Application(
            "SIMPLESERVER", uid=self.uid, gid=self.gid)
        serviceCollection = service.IServiceCollection(self.application)
        self.setName("MASTER")
        self.setServiceParent(serviceCollection)
        # Add the subordinate services to the service collection
        for serviceObject in self._serviceGenerator():
            serviceObject.setServiceParent(serviceCollection)
    
    def _loadConfig(self, configPath):
        """
        Returns a config object, or complains if one not readable.
        """
        if os.path.exists(configPath):
            try:
                self.config = configobj.ConfigObj(infile=configPath)
                return
            except:
                pass
        raise EnvironmentError("No readable config file '%s'" % configPath)

    def _getFactoryFunction(self, name):
        """
        Attempts to import the specified module or package from my module's
        package path and return a function named 'factory' within that module.
        """
        name = name.lower()
        exec "from twisted_goodies.simpleserver.%s import factory" % name
        # Yes, 'factory' is now in the local namespace. Deal with it, pylint
        return factory
    
    def _serviceGenerator(self):
        """
        Yields a service object for each service enabled in my config.
        """
        for key in self.config['services']:
            if key not in self.config:
                continue
            factoryFunction = self._getFactoryFunction(key)
            if not callable(factoryFunction):
                continue
            serviceConfig = self.config[key]
            factory = factoryFunction(self, serviceConfig)
            for portName in ('tcp', 'ssl'):
                if portName not in serviceConfig:
                    continue
                port = int(serviceConfig[portName])
                if portName == 'tcp':
                    serviceObject = internet.TCPServer(port, factory)
                else:
                    if 'ctx' not in locals():
                        ctx = ssl.DefaultOpenSSLContextFactory(
                            self.config['private key'],
                            self.config['certificate'])
                    serviceObject = internet.SSLServer(port, factory, ctx)
                serviceName = "%s-%s" % \
                              tuple([x.upper() for x in (key, portName)])
                print "... subordinate service %s" % serviceName
                serviceObject.setName(serviceName)
                yield serviceObject

    def startService(self):
        """
        Starts non-privileged operation with a umask that permits equivalent
        user and group file access, and installs a (hopefully) better DNS
        resolver.
        """
        os.umask(0003)
        reactor.installResolver(client.createResolver())


