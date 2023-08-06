#!/usr/bin/env python
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

NAME = "AsynCluster"


### Imports and support
import ez_setup, postsetup
ez_setup.use_setuptools()
from setuptools import setup, find_packages


### Define requirements
required = [
    'sAsync>=0.4',
    'Twisted-Goodies>=0.4',
    'AsynQueue>=0.2',
    'configobj']


### Define setup options
kw = {'version':'0.3',
      'license':'GPL',
      'platforms':'OS Independent',

      'url':"http://foss.eepatents.com/%s/" % NAME,
      'author':'Edwin A. Suominen',
      'author_email':'ed@eepatents.com',
      
      'maintainer':'Edwin A. Suominen',
      'maintainer_email':'ed@eepatents.com',

      'install_requires':required,
      'packages':find_packages(exclude=["*.test"]),
      'scripts':['ndm', 'console', 'coreworker'],
      
      'zip_safe':True
      }

kw['keywords'] = [
    'Twisted', 'asynchronous',
    'taskqueue', 'queue', 'priority', 'tasks', 'jobs',
    'cluster', 'clustering', 'parallel', 'grid',
    'genetic', 'evolution', 'evolutionary computing', 'GE', 'GA', 'GP']

kw['classifiers'] = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Object Brokering',
    'Topic :: System :: Distributed Computing',
    'Topic :: Terminals :: Terminal Emulators/X Terminals',
    'Topic :: Desktop Environment :: Window Managers',
    ]

kw['description'] = " ".join("""
Asynchronous cluster management based on the Twisted framework, with
evolutionary computing tools for asynchronous node processing.
""".split("\n"))

kw['long_description'] = " ".join("""
Asynchronous operation of a computing cluster with a Node Display Manager (NDM)
that allows regular workstation usage of cluster nodes with computing jobs
running behind the scenes. Includes evolutionary computing tools (under
construction) that make effective use of the asynchronous node processing
capabilities that are provided.
""".split("\n"))

### Finally, run the setup
setup(name=NAME, **kw)
postsetup.run(NAME, "daemon", "daemon")

