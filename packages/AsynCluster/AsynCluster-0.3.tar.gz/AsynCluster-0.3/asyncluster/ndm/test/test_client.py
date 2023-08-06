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
Unit tests for asyncluster.ndm.client
"""

import os, signal
from twisted.internet import defer, utils, reactor
from twisted.trial.unittest import TestCase

import client


def deferToDelay(delay=0.4):
    d = defer.Deferred()
    reactor.callLater(delay, d.callback, None)
    return d


class Test_NodeRoot(TestCase):
    def setUp(self):
        self.root = client.NodeRoot("foo", None)
        self.root.trusted = True

    def _pids(self, *null):
        def gotPS(psOutput):
            pids = []
            for line in psOutput.strip().split("\n")[1:]:
                fields = line.split()
                if fields[-2:] == ['sleep', '100']:
                    pids.append(int(fields[1]))
            return pids

        d = utils.getProcessOutput("/bin/ps", args=("-Af",))
        return d.addCallback(gotPS)

    def test_bash(self):
        def gotPids(pids):
            self.failUnlessEqual(len(pids), self._count+2)
            for pid in pids:
                os.kill(pid, signal.SIGHUP)
        
        script = """
        for X in 1 2
          do
          sleep 100 &
        done
        """
        d = self._pids()
        d.addCallback(lambda x: setattr(self, '_count', len(x)))
        d.addCallback(lambda _: self.root.remote_bash(script))
        d.addCallback(self.failUnlessEqual, True)
        d.addCallback(self._pids)
        d.addCallback(gotPids)
        return d

    def test_mips(self):
        mips = self.root._mips()
        self.failUnless(len(mips) >= 1)
        self.failUnless(isinstance(mips[0], float))

    def test_pids(self):
        def next(null):
            pidsNew = [x for x in self.root._pids() if x not in pidsBefore]
            self.failUnlessEqual(len(pidsNew), 1)
            pidNew = pidsNew[0]
            self.failUnless(pidNew > pid)
            os.kill(pidNew, signal.SIGHUP)
        
        pidsBefore = self.root._pids()
        pid = os.spawnl(
            os.P_NOWAIT,
            client.PYTHON, client.PYTHON, "-c", self.root.workerCmd)
        return deferToDelay().addCallback(next)

    def _killWorkers(self):
        for pid in self.root._pids():
            os.kill(pid, signal.SIGHUP)

    def test_spawnWorkers_normal(self):
        def first(null):
            # Running spawn should start a new worker per core
            self.root.remote_spawnWorkers()
            return deferToDelay().addCallback(second)

        def second(null):
            pids = self.root._pids()
            self.failUnlessEqual(len(pids), len(self.root._mips()))
            # Running spawn again shouldn't do anything
            self.root.remote_spawnWorkers()
            self.failUnlessEqual(pids, self.root._pids())
            # Kill the spawned worker process(es)
            self._killWorkers()
            
        self._killWorkers()
        return deferToDelay().addCallback(first)
    
    def test_spawnWorkers_restart(self):
        def first(null):
            # Running spawn again with restart should result in all new workers
            self.root.remote_spawnWorkers(restart=True)
            return deferToDelay().addCallback(second)

        def second(null):
            for pid in self.root._pids():
                self.failIf(pid in pidsA)
            self._killWorkers()
        
        # The worker(s) after the first spawn
        self.root.remote_spawnWorkers()
        pidsA = self.root._pids()
        return deferToDelay().addCallback(first)

