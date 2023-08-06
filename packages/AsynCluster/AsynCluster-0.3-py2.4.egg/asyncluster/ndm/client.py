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
The PB-based network client for the cluster node.
"""

import os, signal, sys
from twisted.internet import defer, threads, reactor
from twisted.cred import credentials
from twisted.spread import pb

from asynqueue import jobs

PYTHON = "/usr/bin/python"
RETRY_DELAY = 10.0  # sec


def checkTrust(f):
    """
    Decorates methods so that they only run if their class instance has a
    I{trusted} attribute that is set C{True}.
    """
    def wrapper(self, *args, **kw):
        if self.trusted:
            return f(self, *args, **kw)
        raise jobs.TrustError()

    wrapper.__name__ = f.__name__
    return wrapper


class ConnectionError(Exception):
    """
    An error occurred while trying to connect to the AsynCluster
    server.
    """


class ChildRoot(jobs.ChildRoot):
    """
    I am the root resource for one child worker client capable of running
    cluster jobs.
    """
    trusted = False
    
    def __init__(self, serverPassword):
        self.serverPassword = serverPassword

    def remote_reverseLogin(self, password):
        """
        The server calls this method with its own password to authenticate
        itself to the client, in this case a child worker client.

        If the server is authenticated, returns the string 'child' to identify
        me to the server as a child root. Otherwise, returns C{None}.
        """
        self.trusted = (password == self.serverPassword)
        if self.trusted:
            return 'child'


class NodeRoot(pb.Root):
    """
    I am the root resource for one NDM client capable of spawning worker
    clients and managing user sessions.
    """
    workerCmd = "from asyncluster.ndm import worker; worker.run()"
    
    def __init__(self, serverPassword, main):
        self.serverPassword = serverPassword
        self.main = main

    def remote_reverseLogin(self, password):
        """
        The server calls this method with its own password to authenticate
        itself to the client, in this case a node client.

        If the server is authenticated, returns the string 'node' to identify
        me to the server as a node root. Otherwise, returns C{None}.
        """
        self.trusted = (password == self.serverPassword)
        if self.trusted:
            return 'node'

    def remote_setTimeLeft(self, hoursLeft):
        """
        Sets the number of hours left (a float) to the user.
        """
        self.main.sessionUpdate(hoursLeft)
    
    def remote_message(self, message):
        """
        Displays a pop-up message for the current user.
        """
        pass

    @checkTrust
    def remote_bash(self, script):
        """
        Runs the supplied I{script} in a bash shell, returning a deferred that
        fires with C{True} if the shell finishes without error, i.e., with a
        zero exit code, or C{False} otherwise.
        """
        def done(result):
            return (result[1] == 0)
        
        pid = os.spawnl(os.P_NOWAIT, "/bin/sh", "/bin/sh", "-c", script)
        return threads.deferToThread(os.waitpid, pid, 0).addCallback(done)

    def _mips(self):
        """
        Returns a list of bogomips float values for each core in the client's
        CPU, in order of CPU number.
        """
        values = {}
        fh = open("/proc/cpuinfo", 'r')
        for line in fh:
            if line.startswith("processor"):
                cpuNumber = int(line.split()[-1])
            elif line.startswith("bogomips"):
                values[cpuNumber] = float(line.split()[-1])
        fh.close()
        keys = values.keys()
        keys.sort()
        return [values[key] for key in keys]

    def _pids(self):
        """
        Returns a list of PIDs of all child worker processes currently running
        on the client node.
        """
        pids = []
        for subdir in os.listdir("/proc/"):
            if not subdir.isdigit():
                continue
            procPath = "/proc/%s/cmdline" % subdir
            if not os.access(procPath, os.R_OK):
                continue
            fh = open(procPath, 'rb')
            cmdline = fh.read().split('\x00')
            fh.close()
            if cmdline[0] != PYTHON:
                continue
            if cmdline[1] != '-c':
                continue
            if cmdline[2] == self.workerCmd:
                pids.append(int(subdir))
        return pids

    @checkTrust
    def remote_spawnWorkers(self, restart=False):
        """
        Spawns child processes as needed to keep one child worker client
        running for each CPU core of the node.

        If the I{restart} keyword is set C{True}, kills any child processes
        currently running and then spawns one new child process per CPU core.
        """
        pids = self._pids()
        N = len(self._mips())
        if restart:
            for pid in pids:
                os.kill(pid, signal.SIGHUP)
        else:
            N -= len(pids)
        for k in xrange(N):
            os.spawnl(os.P_NOWAIT, PYTHON, PYTHON, "-c", self.workerCmd)


class ClientFactory(pb.PBClientFactory):
    """
    I am a client factory that terminates my Python process upon disconnection
    from the AsynCluster server.
    """
    def clientConnectionFailed(self, connector, reason):
        """
        Called to indicate that I couldn't connect to the PB server
        (yet). Retry after a while.
        """
        pb.PBClientFactory.clientConnectionFailed(self, connector, reason)
        reactor.callLater(RETRY_DELAY, connector.connect)
        
    def clientConnectionLost(self, *args, **kw):
        """
        Called to terminate my process upon loss of connection to the PB server.
        """
        pb.PBClientFactory.clientConnectionLost(self, *args, **kw)
        try:
            reactor.stop()
        except:
            pass


class Client(object):
    """
    I connect to the master TCP server via PB and offer it L{ClientRoot} as my
    root resource object.

    If I am constructed with the I{session} keyword set C{True}, any connection
    to the server will be as a node client. In that case, I will obtain and
    return a remote reference to the server's global session manager upon
    connecting. Otherwise, I'm just a lowly worker client.
    """
    def __init__(self, main, session=False):
        self.main = main
        self.session = session
    
    def connect(self):
        """
        Connects to the master TCP server. Returns a deferred that fires with
        the perspective provided by the server if and when the connection
        succeeds.
        """
        def gotAnswer(answer):
            if pb.IUnjellyable.providedBy(answer):
                self.perspective = answer
                return answer
            raise ConnectionError("Couldn't authorize connection to server")

        cc = self.main.config['client']
        # TCP Connection
        factory = ClientFactory()
        port = int(self.main.config['common']['tcp port'])
        self.connector = reactor.connectTCP(cc['host'], port, factory)
        # Login parameters
        credential = credentials.UsernamePassword(cc['user'], cc['password'])
        serverPassword = self.main.config['common']['server password']
        if self.session:
            self.root = NodeRoot(serverPassword, self.main)
        else:
            self.root = ChildRoot(serverPassword)
        # Do the login
        return factory.login(credential, self.root).addBoth(gotAnswer)

    def disconnect(self):
        """
        Disconnects from the master TCP server, returning a deferred that fires
        when the disconnection is complete. Before the TCP disconnection
        occurs, any jobs that are running are allowed to finish and any active
        session is ended.
        """
        # Get a deferred that will have fired when any running jobs are done.
        d = getattr(self.root, 'd_runningJob', None)
        if d is None or d.called:
            d = defer.succeed(None)
        # When that happens, we will want to:
        # (1) end any active session, and
        if self.session:
            d.addCallback(lambda _: self.main.sessionEnd())
        # (2) disconnect from the server
        d.addCallback(lambda _: self.connector.disconnect())
        # The returned deferred only fires once all this is done.
        return d
        
            
        
        

        

    

