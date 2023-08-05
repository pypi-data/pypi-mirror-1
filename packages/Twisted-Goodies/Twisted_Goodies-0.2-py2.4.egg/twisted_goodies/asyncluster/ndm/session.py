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
Session management for cluster node's workstation desktop.
"""

import os, os.path, pwd
from twisted.internet import defer, protocol, reactor
from PyQt4 import QtCore, QtGui

from twisted_goodies.asyncluster import util


class WindowManagerProcessProtocol(protocol.ProcessProtocol):
    def __init__(self):
        self.d = defer.Deferred()
        self.errorData = []

    def errReceived(self, data):
        self.errorData.append(data)

    def processEnded(self, reason):
        if reason.value.exitCode == 1:
            util.log("Error running Window manager:\n%s" % \
                     ''.join(self.errorData))
        else:
            util.log("Window manager shutdown with exit code '%s'" \
                % reason.value.exitCode)
        self.d.callback(None)


class SessionWindow(QtGui.QWidget):
    """
    I am a standalone window that manages the active session and displays its
    status.
    """
    def __init__(self, client, user):
        QtGui.QWidget.__init__(self)
        self.client, self.user = client, user
        self.setup()
        del self.minutesLeft
        self.runWindowManager()

    def _getML(self):
        return self.progressBar.value()
    def _setML(self, minutes):
        if not self._setAlready:
            self._setAlready = True
            self.progressBar.setMaximum(minutes)
        self.progressBar.setValue(minutes)
    def _delML(self):
        self._setAlready = False
    minutesLeft = property(_getML, _setML, _delML)

    def setup(self):
        """
        Window and widget setup.
        """
        def sp(*policyNames):
            policies = [
                getattr(QtGui.QSizePolicy, x) for x in policyNames]
            w.setSizePolicy(*policies)
        
        self.setWindowTitle(self.tr("NDM Session"))
        layout = QtGui.QGridLayout(self)
        # Fixed top label
        text = self.tr("User Session for <b>%s</b>" % self.user)
        w = self.topLabel = QtGui.QLabel(text)
        util.biggerFont(w, 2.0)
        sp('MinimumExpanding', 'Fixed')
        layout.addWidget(w, 0, 0, 1, 3)
        # Status display label
        w = self.statusLabel = QtGui.QLabel()
        sp('MinimumExpanding', 'Fixed')
        layout.addWidget(w, 1, 0, 1, 3)
        # Progress bar for showing time left
        w = self.progressBar = QtGui.QProgressBar()
        sp('MinimumExpanding', 'Fixed')
        layout.addWidget(w, 2, 0, 1, 3)
        # Logout button
        #w = self.quitButton = QtGui.QPushButton(self.tr("&Logout"))
        #sp('Fixed', 'Fixed')
        #QtCore.QObject.connect(w, QtCore.SIGNAL("clicked()"), self.end)
        #layout.addWidget(w, 3, 1, 1, 1)
        # That's all         

    def update(self, hoursLeft):
        """
        Call this method to updates the status label and progress bar in
        accordance with the number of hours left, and to end the session when
        the time's up.
        """
        hrs, minutes = divmod(int(60*hoursLeft), 60)
        msg = "Remaining: %d:%02d" % (hrs, minutes)
        if minutes < 10:
            msg += " !!!"
        self.status(msg)
        self.minutesLeft = 60*hrs + minutes

    def end(self, stopWindowManager=True):
        """
        Call this to have me take care of session-ending stuff under my
        control.

        Repeated calls to this method are ignored.
        """
        if getattr(self, 'isRunning', False):
            self.isRunning = False
            if stopWindowManager and hasattr(self, 'process'):
                self.process.loseConnection()
                os.system("killall --user %s" % self.user)
                util.log("Killed all user processes")
            self.close()
    
    def status(self, msg):
        """
        Updates the status label with the supplied I{msg}.
        """
        if msg.endswith("!"):
            msg = "<b>%s</b>" % msg
            self.activateWindow()
        self.statusLabel.setText(self.tr(msg))

    def runWindowManager(self):
        """
        Spawns a process for the window manager such that the session is ended
        when the process ends, or vice versa.
        
        Adapted from L{twisted.internet.util}.
        """
        p = WindowManagerProcessProtocol()
        niceness = int(self.client.config['display']['niceness'])
        windowManager = self.client.config['display']['window manager']
        homeDir = os.path.expanduser("~%s" % self.user)
        env = {'USER':      self.user,
               'LOGNAME':   self.user,
               'HOME':      homeDir}
        for varName in ('DISPLAY', 'PATH', 'TERM',
                        'SHELL', 'LANG', 'LANGUAGE', 'PS1'):
            if varName in os.environ:
                env[varName] = os.environ[varName]
        uid = pwd.getpwnam(self.user)[2]
        self.process = reactor.spawnProcess(
            p, windowManager, (windowManager,),
            env=env, path=homeDir, uid=uid)
        os.system("renice +%d --user %s" % (niceness, self.user))
        p.d.addCallback(lambda _: self.end(stopWindowManager=False))

        
