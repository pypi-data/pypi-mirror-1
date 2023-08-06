# AsynCluster: Node Display Manager (NDM)
# A simple X display manager for cluster nodes that also serve as
# access-restricted workstations.
#
# An NDM client runs on each node and communicates via Twisted's Perspective
# Broker to the Aysncluster server, which regulates when and how much each user
# can use his account on any of the workstations. The NDM server also
# dispatches cluster operations to the nodes via the NDM clients, unbeknownst
# to the workstation users.
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

import os
from twisted.internet import defer


CONFIG_PATH = "/etc/asyncluster.conf"


class BaseManager(object):
    """
    I am a base class for the node client, GUI or console.

    @ivar d: A deferred that fires when the client connects to the
      AsynCluster server.

    @ivar config: A L{configobj} config object loaded from the config file.
    
    """
    def __init__(self):
        # The Twisted reactor, with no GUI integration needed
        from twisted.internet import reactor; self.reactor = reactor
        # Go!
        self.reactor.callWhenRunning(self.startup)
        self.reactor.run()

    def gotConnected(self, sessionMgr):
        """
        Connected callback for console clients.
        """
        self.sessionMgr = sessionMgr

    def startup(self):
        import configobj, client
        self.config = configobj.ConfigObj(CONFIG_PATH)
        self.client = client.Client(self)
        self.activeUser = None
        self.client.connect().addCallback(self.gotConnected)
    
    def shutdown(self):
        d = self.client.disconnect()
        d.addCallback(lambda _: self.reactor.stop())
        return d

    def sessionBegin(self, user, password):
        """
        For all clients, requests a session for the specified I{user},
        authenticated with the supplied I{password}.
        """
        def gotSessionAnswer(approved):
            if approved:
                if hasattr(self, 'loginWindow'):
                    self.loginWindow.hide()
                    self.sessionWindow = self.gui.SessionWindow(self, user)
                    self.sessionWindow.show()
                self.activeUser = user
                d = self.sessionMgr.callRemote('timeLeft')
                d.addCallback(self.sessionUpdate)
                return d
        
        d = self.sessionMgr.callRemote('begin', user, password)
        d.addCallback(gotSessionAnswer)
        return d
        
    def sessionUpdate(self, hoursLeft):
        """
        For all clients, updates the session.
        """
        if self.activeUser is None:
            return
        if hoursLeft > 0.0:
            if hasattr(self, 'sessionWindow'):
                self.sessionWindow.update(hoursLeft)
        else:
            self.sessionEnd(callServer=False)

    def sessionEnd(self, callServer=True):
        """
        For all clients, ends the session.
        """
        self.activeUser = None
        if callServer:
            return self.sessionMgr.callRemote('end')
        return defer.succeed(None)


class GuiManager(BaseManager):
    """
    """
    def __init__(self):
        # Start PyQt4 with Twisted integration
        from twisted_goodies.qtwisted import qt4reactor
        from PyQt4.QtGui import QApplication
        self.app = QApplication([])
        qt4reactor.install(self.app)
        # Now get the regular reactor
        from twisted.internet import reactor; self.reactor = reactor
        # The gui module...
        import gui; self.gui = gui
        # Go!
        self.reactor.callWhenRunning(self.startup)
        self.reactor.run()

    def gotConnected(self, sessionMgr):
        """
        Connected callback for GUI clients.
        """
        self.sessionMgr = sessionMgr
        self.loginWindow = self.gui.LoginWindow(self)        

    def sessionEnd(self, callServer=True):
        """
        Ends the session for GUI clients.
        """
        self.loginWindow.show()
        self.loginWindow.repaint()
        if hasattr(self, 'sessionWindow'):
            self.sessionWindow.wmStop()
            self.sessionWindow.close()
            del self.sessionWindow
        return BaseManager.sessionEnd(self, callServer)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "-g", "--gui",
        action="store_true", dest="gui",
        help="Run the NDM application in a fixed-sized, unmanaged window")
    opts, args = parser.parse_args()

    if opts.gui:
        # Run the NDM application in a fixed-sized, unmanaged window with the
        # overall event loop under Twisted control.
        GuiManager()
    else:
        # Run a console-only client with no user session.
        BaseManager()    


