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

"""
Unit tests for asyncluster
"""

import sys, os.path

# Ensure that the package under test and its modules can all be imported by
# name only
packagePath = os.path.dirname(__file__)
for k in xrange(2):
    packagePath = os.path.dirname(packagePath)
    if packagePath not in sys.path:
        sys.path.insert(0, packagePath)

# Ensure that any helper modules in the "real" test package (containing the
# target file for any symlinks to this file) can be imported by name only
packagePath = os.path.dirname(os.path.realpath(__file__))
if packagePath not in sys.path:
    sys.path.append(packagePath)
