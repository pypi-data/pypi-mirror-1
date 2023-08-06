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
VM Function to starts one or more existing VMs
"""

from optparse import OptionParser
from logilabvm.lib import _execute, _gethooks, VMError, HookCall, show

def run(sysargs, usage=None):
    """
    Function that starts VMs and return command results
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="Start all inactive VMs")

    (options, args) = parser.parse_args(sysargs)

    # retrieve hooks
    hooks = _gethooks("START")

    inactive = show.run(["--inactive", ])
    result = []
    if options.all:
        for vm in inactive:
            # first, try to execute the hook
            if hooks[vm['hyper']]:
                hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
                raise HookCall(hookres)

            cmdres = _execute("virsh -c %s:///system start %s" % (vm['hyper'], vm['name']))
            vm.update(cmdres)
            result.append(vm)

    elif len(args) > 0:
        # retrieve vm to activate
        activate = []
        names = [ el['name'] for el in inactive ]
        for arg in args:
            try:
                activate.append(inactive[names.index(arg)])
            except ValueError:
                raise VMError("%s not an inactive VM" % arg)
        # active VMs
        for vm in activate:
            # first, try to execute the hook
            if hooks[vm['hyper']]:
                hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
                raise HookCall(hookres)

            cmdres = _execute("virsh -c %s:///system start %s" % (vm['hyper'], vm['name']))
            vm.update(cmdres)
            result.append(vm)

    else:
        raise AttributeError, usage

    return result
