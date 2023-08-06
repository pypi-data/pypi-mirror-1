# -*- mode:python -*-
#
# AsynCluster
# A cluster management server based on Twisted's Perspective Broker and a Node
# Display Manager (NDM) client. The server dispatches cluster jobs and
# regulates when and how much each user can use his account on any of the
# cluster node workstations.
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

import configobj
from twisted.spread import pb
from twisted.application import internet, service

from asyncluster.master import nodes, control

# The NDM configuration file
configFile = '/etc/asyncluster.conf'
config = configobj.ConfigObj(configFile)

# Everything runs under the oversight and direction of a Controller object
ctl = control.Controller(config)

# Set up the service collection with:
application = service.Application("ASYNCLUSTER")
serviceCollection = service.IServiceCollection(application)

# (1) a node-master PB server, via TCP, and
nmFactory = nodes.ServerFactory(ctl)
port = int(config['common']['tcp port'])
nmServer = internet.TCPServer(port, nmFactory)
nmServer.setServiceParent(serviceCollection)

# (2) a cluster master control PB server, via a UNIX socket
mcRoot = control.Root(ctl)
mcFactory = pb.PBServerFactory(mcRoot)
mcServer = internet.UNIXServer(config['common']['socket'], mcFactory)
mcServer.setServiceParent(serviceCollection)

