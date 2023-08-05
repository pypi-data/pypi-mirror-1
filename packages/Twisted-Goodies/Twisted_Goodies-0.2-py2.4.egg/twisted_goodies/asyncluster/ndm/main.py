# AsynCluster: Node Display Manager (NDM):
# A simple X display manager for cluster nodes that also serve as
# access-restricted workstations. An NDM client runs on each node and
# communicates via Twisted's Perspective Broker to the Aysncluster server,
# which regulates when and how much each user can use his account on any of the
# workstations. The NDM server also dispatches cluster operations to the nodes
# via the NDM clients, unbeknownst to the workstation users.
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
The main module of the NDM application. Installs a PyQt4 QApplication() object
into Twisted's qtreactor().
"""

# Start PyQt4 with Twisted integration
if True:
#try:
    from twisted_goodies.qtwisted import qt4reactor
    from PyQt4.QtGui import QApplication
    app = QApplication([])
    qt4reactor.install(app)
    import gui
#except:
#    print "Console mode"
from twisted.internet import reactor

# Other imports
import os
import configobj
from twisted.internet import defer

# Project imports
import client


CONFIG_PATH = "/etc/asyncluster.conf"


class MainManager(object):
    """
    I am the main object for the node client, GUI or console.

    @ivar d: A deferred that fires when the client connects to the
      AsynCluster server.

    @ivar config: A L{configobj} config object loaded from the config file.
    
    """
    def __init__(self, configPath, app=None):
        self.app = app
        self.config = configobj.ConfigObj(configPath)
        self.client = client.Client(self)
        self.d = defer.Deferred()
        self.activeUser = None
        reactor.callWhenRunning(self.startup)

    def startup(self):
        def connected(sessionMgr):
            self.sessionMgr = sessionMgr
            if self.app:
                self.loginWindow()
            else:
                print "Connected to AsynCluster server"
            self.d.callback(None)
        
        self.client.connect().addCallback(connected)
    
    def shutdown(self):
        d = self.client.disconnect()
        d.addCallback(lambda _: reactor.stop())
        return d

    def loginWindow(self):
        """
        Creates and displays a L{gui.LoginWindow}.
        """
        self.loginWindow = gui.LoginWindow(self)

    def sessionBegin(self, user, password):
        """
        Requests a session for the specified I{user}, authenticated with the
        supplied I{password}.
        """
        def gotAnswer(approved):
            if approved:
                if self.app:
                    self.loginWindow.hide()
                    self.sessionWindow = gui.SessionWindow(self, user)
                    self.sessionWindow.show()
                else:
                    print "Console session started for '%s'" % user
                self.activeUser = user
                d = self.sessionMgr.callRemote('timeLeft')
                d.addCallback(self.sessionUpdate)
                return d
            # Denied!
            if not self.app:
                print "Session denied for '%s'" % user
        
        d = self.sessionMgr.callRemote('begin', user, password)
        d.addCallback(gotAnswer)
        return d
        
    def sessionUpdate(self, hoursLeft):
        """
        """
        if self.activeUser is None:
            return
        if hoursLeft > 0.0:
            if self.app:
                if hasattr(self, 'sessionWindow'):
                    self.sessionWindow.update(hoursLeft)
            else:
                print "Hours left:", hoursLeft
        else:
            self.sessionEnd()

    def sessionEnd(self):
        """
        """
        self.activeUser = None
        if self.app:
            self.loginWindow.show()
            self.loginWindow.repaint()
            if hasattr(self, 'sessionWindow'):
                self.sessionWindow.wmStop()
                self.sessionWindow.close()
                del self.sessionWindow
        else:
            print "Console session ended"
        return self.sessionMgr.callRemote('end')


def runConsole(user, password):
    """
    Runs a console-only client.
    """
    mgr = MainManager(CONFIG_PATH)
    mgr.d.addCallback(lambda _: mgr.sessionBegin(user, password))
    reactor.run()


def runGUI():
    """
    Runs the NDM application in a fixed-sized, unmanaged window with the
    overall event loop under Twisted control.
    """
    mgr = MainManager(CONFIG_PATH, app=app)
    reactor.run()
