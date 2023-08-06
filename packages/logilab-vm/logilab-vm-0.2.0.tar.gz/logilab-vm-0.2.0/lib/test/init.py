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

# should correspond to VM files with correct information in them (images path etc.)
KVM = ("kvm01", "kvm02")
OPENVZ = ("101", "102")

def run():
    """
    define selected VMs
    """
    for vm in KVM:
        system("virsh -c qemu:///system define %s.xml" % vm)
    for vm in OPENVZ:
        system("virsh -c openvz:///system define %s.xml" % vm)

if __name__ == "__main__":
    run()
