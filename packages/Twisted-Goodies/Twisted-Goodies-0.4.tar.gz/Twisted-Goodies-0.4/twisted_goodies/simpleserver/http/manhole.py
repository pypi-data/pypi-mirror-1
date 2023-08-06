# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.
 
"""
An interactive Python interpreter with syntax coloring.
 
Nothing interesting is actually defined here.  Two listening ports are
set up and attached to protocols which know how to properly set up a
ColoredManhole instance.
"""
 
from twisted.conch.manhole import ColoredManhole
from twisted.conch.insults import insults
from twisted.conch.telnet import TelnetTransport, TelnetBootstrapProtocol
from twisted.conch.manhole_ssh import ConchFactory, TerminalRealm
 
from twisted.internet import protocol
from twisted.application import internet, service
from twisted.cred import checkers, portal
 

def makeService(port, interface, username, password, namespace):
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(
        **{username: password})
 
    def chainProtocolFactory():
        return insults.ServerProtocol(ColoredManhole, namespace)
 
    rlm = TerminalRealm()
    rlm.chainedProtocolFactory = chainProtocolFactory
    ptl = portal.Portal(rlm, [checker])
    f = ConchFactory(ptl)
    return internet.TCPServer(port, f, interface=interface)
