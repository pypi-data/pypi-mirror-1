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
# Copyright (C) 2006-2008 by Edwin A. Suominen, http://www.eepatents.com
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
The main module for node workers.

"""


CONFIG_PATH = "/etc/asyncluster.conf"


class Manager(object):
    """
    I manage a node client. Instantiate me with I{headless} set C{True} if
    there will be no GUI for user logins or display management.
    
    @ivar config: A L{configobj} config object loaded from the config file.
    
    """
    def __init__(self, headless=False, duration=None):
        import configobj
        self.config = configobj.ConfigObj(CONFIG_PATH)
        if headless:
            self.gui = None
        else:
            import gui
            self.gui = gui
        # Regular reactor import comes after possible Qt reactor integration in
        # gui module
        from twisted.internet import reactor
        reactor.callWhenRunning(self.startup)
        if isinstance(duration, (float, int)):
            reactor.callLater(float(duration), reactor.stop)
        reactor.run()

    def startup(self):
        """
        Instantiates a session-capable client and connects it to the server.
        """
        def gotSessionMgr(sessionMgr):
            self.sessionMgr = sessionMgr
            if self.gui:
                self.loginWindow = self.gui.LoginWindow(self)        

        import client
        self.client = client.Client(self, session=True)
        d = self.client.connect()
        d.addCallback(lambda p: p.callRemote('getSessionManager'))
        d.addCallback(gotSessionMgr)
        return d

    def sessionBegin(self, user, password):
        """
        Requests a session for the specified I{user}, authenticated with the
        supplied I{password}.
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
        Updates the session.
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
        Ends the session, returning a deferred that fires when I'm ready for a
        new session.
        """
        if hasattr(self, 'loginWindow'):
            self.loginWindow.show()
            self.loginWindow.repaint()
        if hasattr(self, 'sessionWindow'):
            self.sessionWindow.wmStop()
            self.sessionWindow.close()
            del self.sessionWindow
        self.activeUser = None
        if callServer:
            return self.sessionMgr.callRemote('end')
        from twisted.internet import defer
        return defer.succeed(None)


def run():
    Manager()

def runHeadless(duration=None):
    Manager(headless=True, duration=duration)
