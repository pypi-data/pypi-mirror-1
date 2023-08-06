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
#
# -----------------------------------------------------------------------------
#
# Daemonization code adapted from
#     http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66012

"""
The main module for worker clients, running as daemons.
"""

import os, sys


CONFIG_PATH = "/etc/asyncluster.conf"


class Manager(object):
    """
    I manage a child worker client.

    @ivar config: A L{configobj} config object loaded from the config file.
    
    """
    def __init__(self):
        # Imports
        from twisted.internet import reactor
        import configobj, client
        # The config object
        self.config = configobj.ConfigObj(CONFIG_PATH)
        # The session-less client
        self.client = client.Client(self)
        # Go!
        reactor.callWhenRunning(self.client.connect)
        reactor.run()


def run():
    """
    Runs a child worker L{Manager} in a process forked into the background.
    """
    # First fork
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.exit(1)
    # Decouple from parent environment
    os.chdir(".")
    os.umask(0)
    os.setsid()
    # Second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)
    except OSError, e: 
        sys.exit(1)
    # Remap standard file descriptors to /dev/null
    si = file("/dev/null", 'r')
    os.dup2(si.fileno(), sys.stdin.fileno())
    so = file("/dev/null", 'a+')
    os.dup2(so.fileno(), sys.stdout.fileno())
    se = file("/dev/null", 'a+', 0)
    os.dup2(se.fileno(), sys.stderr.fileno())
    # Finally, run the child worker
    Manager()

