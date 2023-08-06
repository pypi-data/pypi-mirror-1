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
VM Function to show the archive list of one existing VM
"""

from optparse import OptionParser
from re import compile as comp
from logilabvm.lib import _HYPERVISORS, _execute, _gethooks, HookCall

def run(sysargs, usage=None):
    """
    Function that returns list of VMs { id, name, state, hypervisor }
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="Show active and inactive VMs")
    parser.add_option("-0", "--inactive", action="store_true", dest="inactive", 
        default=False, help="Show inactive VMs only")
    parser.add_option("-1", "--active", action="store_false", dest="active", 
        default=True, help="Show active VMs only")

    (options, _) = parser.parse_args(sysargs)

    # retrieve hooks
    hooks = _gethooks("SHOW")

    result = []
    for hyp in _HYPERVISORS:
        # first, try to execute the hook
        if hooks[hyp]:
            hookres = _execute("%s %s" % (hooks[hyp], ' '.join(sysargs)))
            raise HookCall(hookres)

        if options.all:
            cmdres = _execute("virsh -c %s:///system list --all" % (hyp,))
        elif options.inactive:
            cmdres = _execute("virsh -c %s:///system list --inactive" % (hyp,))
        else:
            cmdres = _execute("virsh -c %s:///system list" % (hyp,))
        
        if cmdres['value']:
            result.append(cmdres)
        else:
            tmp = analyze(cmdres['stdout'])
            for vm in tmp:
                vm['hyper'] = hyp
                vm.update(cmdres)
            result = result + tmp

    return result

VM_RGX = comp('^(?P<id>(-|[0-9]+))\s+(?P<name>\w+)\s+(?P<state>\w.*)$')
def analyze(output):
    """
    Analyze the command output and fill results in a dictionary
    """
    result = []
    lines = output.splitlines()
    for line in lines:
        line = line.strip()
        vm = VM_RGX.match(line)
        if vm:
            result.append(vm.groupdict())
    return result
