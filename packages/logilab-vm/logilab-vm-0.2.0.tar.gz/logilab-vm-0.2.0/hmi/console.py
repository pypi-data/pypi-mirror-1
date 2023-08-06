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
IHM Console to manage VMs
"""

import sys
from os.path import basename
from logilabvm.lib import VMError, ExecError, HookCall, \
    archives, create, migrate, restore, resume, save, \
    show, start, stop, suspend, delete

help = """Logilab-vm

Usage: <command> [options]

Commands:

    logilab-vm             Print this help and exit
    logilab-vm-show        Show a list of existing VMs
    logilab-vm-start       Start one or more existing VMs
    logilab-vm-stop        Stop one: or more existing VMs
    logilab-vm-migrate     Migrate an existing VM
    logilab-vm-create      Create a VM
    logilab-vm-archives    Show the archive list of an existing VM
    logilab-vm-save        Save an active VM (this shuts down the VM)
    logilab-vm-restore     Restore an inactive VM
    logilab-vm-suspend     Suspend an active VM
    logilab-vm-resume      Resume an active VM
    logilab-vm-delete      Delete an inactive VM

Note: <command> help for more informations a specific command
"""
def run():
    """
    Fonction that execute the proper VM function
    """
    
    command = basename(sys.argv[0])

    try:
        if command == "logilab-vm":
            print help
            sys.exit(0)
        elif command == "logilab-vm-show":
            result = show.run(sysargs=sys.argv[1:], 
                usage="usage: %prog [options]")
            display_show(result)
        elif command == "logilab-vm-start":
            result = start.run(sysargs=sys.argv[1:], 
                usage="usage: %prog [options] [name1 name2 ...]")
            display_start(result)
        elif command == "logilab-vm-stop":
            result = stop.run(sysargs=sys.argv[1:], 
                usage="usage: %prog [options] [name1 name2 ...]")
            display_stop(result)
        elif command == "logilab-vm-migrate":
            result = migrate.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name> <destination> [options]")
            raise NotImplementedError
        elif command == "logilab-vm-create":
            result = create.run(sysargs=sys.argv[1:], 
                usage="usage: %prog --type <type> --sys <sys_options> [options]")
            display_create(result)
        elif command == "logilab-vm-archives":
            result = archives.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name>")
            display_archives(result)
        elif command == "logilab-vm-save":
            result = save.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name> [options]")
            display_save(result)
        elif command == "logilab-vm-restore":
            result = restore.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name> [options] (default archive: last save)")
            display_restore(result)
        elif command == "logilab-vm-suspend":
            result = suspend.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name>")
            display_suspend(result)
        elif command == "logilab-vm-resume":
            result = resume.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name>")
            display_resume(result)
        elif command == "logilab-vm-delete":
            result = delete.run(sysargs=sys.argv[1:], 
                usage="usage: %prog <name>")
            display_delete(result)
        else:
            print help
            sys.exit(1)
    except AttributeError, msg:
        print "Wrong arguments: %s" % msg
        sys.exit(2)
    except VMError, msg:
        print "Failure: %s" % msg
        sys.exit(3)
    except HookCall, msg:
        print "Result from hook call:\n%s" % msg
        sys.exit(4)
    except NotImplementedError:
        print "Functionality not implemented for this hypervisor, please set a hook"
        sys.exit(5)
    except ExecError, msg:
        print "Execute error:\n%s" % msg
        sys.exit(6)
    except Exception, msg:
        print "Unhandled error: %s" % msg

def display_show(results):
    """
    Display results of show
    """
    if not results:
        print "No results"
    successes = []
    failures = []
    for result in results:
        if result['value']:
            failures.append(result)
        else:
            successes.append(result)

    # print success
    if successes:
        print "id".center(10), "name".center(10), "state".center(10), "hyper".center(10)
        print '-' * 40
        for success in successes:
            print success['id'].center(10), success['name'].center(10), \
                success['state'].center(10), success['hyper'].center(10)
    # print failures
    if failures:
        print "Failures:"
        for failure in failures:
            print failure['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_start(results):
    """
    Display results of start
    """
    if not results:
        print "No results"
    successes = []
    failures = []
    for result in results:
        if result['value']:
            failures.append(result)
        else:
            successes.append(result)

    # print success
    if successes:
        print "name".center(10), "result".center(30)
        print '-' * 40
        for success in successes:
            print success['name'].center(10), success['stdout'].strip().center(30)
    # print failures
    if failures:
        print "Failures:"
        for failure in failures:
            print failure['name'], failure['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_stop(results):
    """
    Display results of stop
    """
    if not results:
        print "No results"
    successes = []
    failures = []
    for result in results:
        if result['value']:
            failures.append(result)
        else:
            successes.append(result)

    # print success
    if successes:
        print "name".center(10), "result".center(30)
        print '-' * 40
        for success in successes:
            print success['name'].center(10), success['stdout'].strip().center(30)
    # print failures
    if failures:
        print "Failures:"
        for failure in failures:
            print failure['name'], failure['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_create(result):
    """
    Display results of create
    """
    print "Success: %s created. Domain description in %s" % (result[0], result[1])
    sys.exit(0)

def display_archives(result):
    """
    Display results of archives
    """
    if not result['result']:
        print "No results"
    # print success
    elif not result['value']:
        print "%s archives".center(25) % result['name']
        print '-' * 25
        for element in result['result']:
            print element.center(25)
    else:
        print "Failure: %s" % result['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_save(result):
    """
    Display results of save
    """
    # print success
    if not result['value']:
        print "Success: %s" % result['stdout'].strip()
    # print failure
    else:
        print "Failure: %s" % result['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_restore(result):
    """
    Display results of restore
    """
    # print success
    if not result['value']:
        print "Success: %s" % result['stdout'].strip()
    # print failure
    else:
        print "Failure: %s" % result['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_suspend(result):
    """
    Display results of restore
    """
    # print success
    if not result['value']:
        print "Success: %s" % result['stdout'].strip()
    # print failure
    else:
        print "Failure: %s" % result['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_resume(result):
    """
    Display results of restore
    """
    # print success
    if not result['value']:
        print "Success: %s" % result['stdout'].strip()
    # print failure
    else:
        print "Failure: %s" % result['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

def display_delete(result):
    """
    Display results of restore
    """
    # print success
    if not result['value']:
        print "Success: %s" % result['stdout'].strip()
    # print failure
    else:
        print "Failure: %s" % result['stderr'].strip()
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    run()

