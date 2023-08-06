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
VM Function to migrate an exsting VM
"""

from optparse import OptionParser
from logilabvm.lib import _execute, _gethooks, VMError, HookCall, show

def run(sysargs, usage=None):
    """
    Function that migrate a VM and return command results
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-l", "--live", action="store_true", dest="live", default=False, help="Migrate VM while running")

    (options, _) = parser.parse_args(sysargs)

    # check arguments
    if len(sysargs) < 2:
        raise AttributeError, usage
    allvm = show.run(["--all", ])
    names = [ el['name'] for el in allvm ]
    if not sysargs[0] in names:
        raise VMError("%s not an existing VM" % sysargs[0])

    # retrieve hooks
    hooks = _gethooks("MIGRATE")

    # first, try to execute the hook
    vm = allvm[names.index(sysargs[0])]
    if hooks[vm['hyper']]:
        hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
        raise HookCall(hookres)

    raise NotImplementedError

    return
