#!/usr/bin/env python
# Copyright (c) 2008-2009 LOGILAB S.A. (Paris, FRANCE).
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

from subprocess import Popen, PIPE
import os.path as osp
from os.path import expanduser, join, isfile, abspath
import ConfigParser

_HYPERVISORS = ("qemu", "openvz")
<<<<<<< /home/arthur/src/public/logilab-vm/lib/__init__.py
if isfile(expanduser('~/.logilab-vm/settings.ini')):
    _CONFIGFILE = expanduser('~/.logilab-vm/settings.ini')
else:
    _CONFIGFILE = abspath(join(__path__[0], '..', 'conf', 'settings.ini'))
=======
if osp.isfile(osp.expanduser('/etc/logilab-vm/settings.ini')):
    _CONFIGFILE = osp.expanduser('/etc/logilab-vm/settings.ini')
else:
    _CONFIGFILE = osp.abspath(osp.join(__path__[0], '..', 'conf', 'settings.ini'))
>>>>>>> /tmp/__init__.py~other.a7Csbm

def _execute(command, input=None, env=None, verbose=False):
    """
    Execute a command using subprocess. Return the tuple (returncode, stdout, stderr).
    """
    if verbose:
        process = Popen(command, stdin=None, stdout=None, stderr=None, shell=True, env=env)
    else:
        process = Popen(command, stdin=None, stdout=PIPE, stderr=PIPE, shell=True, env=env)
    result = process.communicate(input)
    return { 'cmd' : command,
             'value' : process.wait(),
             'stdout' : result[0],
             'stderr' : result[1] }

def _gethooks(command):
    """
    Retrieve hooks from _CONFIGFILE for each hypervisor.
    Return a dictionary with None if no hooks
    """
    config = ConfigParser.ConfigParser()
    config.read(_CONFIGFILE)

    open(_CONFIGFILE)

    dir = config.get('MAIN','hooksdir')
    hooks = {}
    for hyp in _HYPERVISORS:
        try:
            hooks[hyp] = osp.join(osp.abspath(dir), config.get(command, "hook" + hyp))
        except ConfigParser.NoOptionError:
            hooks[hyp] = None
    return hooks

class VMError(Exception):
    """
    Virtual Machines related error
    """
    pass

class ExecError(Exception):
    """
    Script execution error
    """
    def __init__(self, dict):
        self.cmd = dict['cmd']
        self.value = dict['value']
        self.stdout = dict['stdout']
        self.stderr = dict['stderr']
        Exception.__init__(self)

    def __str__(self):
        if not self.value:
            if self.stdout:
                return "Success executing \"%s\":\n%s" % (self.cmd, self.stdout)
            else:
                return "Success executing \"%s\"" % self.cmd
        else:
            if self.stderr:
                return "Failure executing \"%s\":\n%s" % (self.cmd, self.stderr)
            else:
                return "Failure executing \"%s\"" % self.cmd

class HookCall(ExecError):
    """
    Raised on hook call
    """
    pass

