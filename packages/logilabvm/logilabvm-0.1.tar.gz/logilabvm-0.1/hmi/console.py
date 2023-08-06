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
from optparse import OptionParser
from logilabvm.lib import VMError, ExecError, HookCall, \
    archives, create, migrate, restore, resume, save, \
    show, start, stop, suspend

def run():
    """
    Fonction that execute the proper VM function
    """
    parser = OptionParser()
    parser.add_option("--show", action="store_true", dest="show", 
        default=False, help="Show a list of existing VMs")
    parser.add_option("--start", action="store_true", dest="start", 
        default=False, help="Start one or more existing VMs")
    parser.add_option("--stop", action="store_true", dest="stop", 
        default=False, help="Stop one or more existing VMs")
    parser.add_option("--migrate", action="store_true", dest="migrate", 
        default=False, help="Migrate an existing VM")
    parser.add_option("--create", action="store_true", dest="create", 
        default=False, help="Create a VM")
    parser.add_option("--archives", action="store_true", dest="archives", 
        default=False, help="Show the archive list of an existing VM")
    parser.add_option("--save", action="store_true", dest="save", 
        default=False, help="Save an active VM (this shuts down the VM)")
    parser.add_option("--restore", action="store_true", dest="restore", 
        default=False, help="Restore an inactive VM")
    parser.add_option("--suspend", action="store_true", dest="suspend", 
        default=False, help="Suspend an active VM")
    parser.add_option("--resume", action="store_true", dest="resume", 
        default=False, help="Resume an active VM")

    (options, _) = parser.parse_args(sys.argv[1:2])

    try:
        if options.show:
            result = show.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --show [options]")
            display_show(result)
        elif options.start:
            result = start.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --start [options] [name1 name2 ...]")
            display_start(result)
        elif options.stop:
            result = stop.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --stop [options] [name1 name2 ...]")
            display_stop(result)
        elif options.migrate:
            result = migrate.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --migrate <name> <destination> [options]")
            raise NotImplementedError
        elif options.create:
            result = create.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --create --type <type> --sys <sys_options> [options]")
            display_create(result)
        elif options.archives:
            result = archives.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --archives <name>")
            display_archives(result)
        elif options.save:
            result = save.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --save <name> [options]")
            display_save(result)
        elif options.restore:
            result = restore.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --restore <name> [options] (default archive: last save)")
            display_restore(result)
        elif options.suspend:
            result = suspend.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --suspend <name>")
            display_suspend(result)
        elif options.resume:
            result = resume.run(sysargs=sys.argv[2:], 
                usage="usage: %prog --resume <name>")
            display_resume(result)
        else:
            parser.print_help()
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

if __name__ == "__main__":
    run()

