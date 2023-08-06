#!/usr/bin/env python
# Copyright (c) 2008 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from os import system
from logilabvm.lib import show, stop

def run():
    """
    stop and undefine all VMs
    """
    for vm in show.run(["--active",]):
        info = stop.run(["--force",vm['name']])
        if not info[0]['value']:
            print info[0]['stdout']
        else:
            raise Exception, info[0]['stderr']

    for vm in show.run(["--all",]):
        system("virsh -c %s:///system undefine %s" % (vm['hyper'], vm['name']))

if __name__ == "__main__":
    run()
