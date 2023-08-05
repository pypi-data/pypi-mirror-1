# SIMPLEMAIL: (Hopefully) dirt-simple twisted-based mail server
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
The simplemail POP3 server.

Copyright (C) 2006-2007 by Edwin A. Suominen, http://www.eepatents.com

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the file COPYING for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
Street, Fifth Floor, Boston, MA 02110-1301, USA
"""

import os.path
from zope.interface import implements
from twisted.internet import defer, protocol
from twisted.cred import portal
from twisted.mail import pop3, maildir


class Realm(object):
    """
    The Realm for the authenticated POP3 server.
    """
    implements(portal.IRealm)

    def __init__(self, baseDir):
        self.baseDir = baseDir

    def logout(self):
        """
        The user logged out, so what?
        """
    
    def requestAvatar(self, avatarId, mind, *interfaces):
        """
        Returns the required I{interface, avatar, logout} tuple.
        """
        if pop3.IMailbox not in interfaces:
            raise NotImplementedError(self, interfaces)
        thisMaildir = os.path.join(self.baseDir, avatarId)
        avatar = maildir.MaildirMailbox(thisMaildir)
        result = (pop3.IMailbox, avatar, self.logout)
        return defer.succeed(result)


class ServerFactory(protocol.Factory):
    """
    I am a POP3 server factory, constructed with a checker and a string
    pointing to my maildir base directory.
    """
    protocol = pop3.POP3
    
    def __init__(self, checker, baseDir):
        realm = Realm(baseDir)
        self.portal = portal.Portal(realm)
        self.portal.registerChecker(checker)

    def buildProtocol(self, address):
        p = self.protocol()
        p.portal = self.portal
        p.factory = self
        return p


def factory(master, config):
    baseDir = config['base dir']
    return ServerFactory(master.checker, baseDir)


        
