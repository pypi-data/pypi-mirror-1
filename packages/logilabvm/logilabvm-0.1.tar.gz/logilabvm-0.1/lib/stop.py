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
VM Function to stops one or more existing VMs
"""

from optparse import OptionParser
from logilabvm.lib import _execute, _gethooks, VMError, HookCall, show

def run(sysargs, usage=None):
    """
    Function that stops VMs and return command results
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--all", action="store_true", dest="all", 
        default=False, help="Stops all active VMs")
    parser.add_option("-f", "--force", action="store_true", dest="force", 
        default=False, help="Force to stop VMs")

    (options, args) = parser.parse_args(sysargs)

    # retrieve hooks
    hooks = _gethooks("STOP")

    active = show.run(["--active", ])
    result = []
    if options.all:
        for vm in active:
            # first, try to execute the hook
            if hooks[vm['hyper']]:
                hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
                raise HookCall(hookres)

            if options.force:
                cmdres = _execute("virsh -c %s:///system destroy %s" % (vm['hyper'], vm['id']))
            else:
                cmdres = _execute("virsh -c %s:///system shutdown %s" % (vm['hyper'], vm['id']))
            vm.update(cmdres)
            result.append(vm)

    elif len(args) > 0:
        # retrieve vm to desactivate
        desactivate = []
        names = [ el['name'] for el in active ]
        for arg in args:
            try:
                desactivate.append(active[names.index(arg)])
            except ValueError:
                raise VMError("%s not an active VM" % arg)
        # desactive VMs
        for vm in desactivate:
            # first, try to execute the hook
            if hooks[vm['hyper']]:
                hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
                raise HookCall(hookres)

            if options.force:
                cmdres = _execute("virsh -c %s:///system destroy %s" % (vm['hyper'], vm['id']))
            else:
                cmdres = _execute("virsh -c %s:///system shutdown %s" % (vm['hyper'], vm['id']))
            vm.update(cmdres)
            result.append(vm)

    else:
        raise AttributeError, usage

    return result
