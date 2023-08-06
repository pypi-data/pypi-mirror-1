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

"""
VM Function to resume an existing VM
"""

from optparse import OptionParser
from shutil import rmtree
import os.path as osp
import ConfigParser
from logilabvm.lib import _execute, _gethooks, _CONFIGFILE, HookCall, VMError, show

def run(sysargs, usage=None):
    """
    Function that returns the result of the 'resume' command
    """
    parser = OptionParser(usage=usage)

    (_, _) = parser.parse_args(sysargs)

    # check arguments
    if len(sysargs) < 1:
        raise AttributeError, usage
    allvm = show.run(["--inactive", ])
    names = [ el['name'] for el in allvm ]
    if not sysargs[0] in names:
        raise VMError("%s not an inactive VM" % sysargs[0])
    vm = allvm[names.index(sysargs[0])]

    config = ConfigParser.ConfigParser()
    config.read(_CONFIGFILE)

    open(_CONFIGFILE)

    archivedir = osp.join(config.get('MAIN','archivesdir'), vm['hyper'], vm['name'])

    # retrieve hooks
    hooks = _gethooks("DELETE")
    if hooks[vm['hyper']]:
        hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
        raise HookCall(hookres)

    cmdres = _execute("virsh -c %s:///system undefine %s" % (vm['hyper'], vm['name']))
    vm.update(cmdres)

    # if command succeeded the delete all archives
    if not vm['value']:
        try:
            rmtree(archivedir)
        except OSError:
            pass

    return vm
