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
VM Function to restore an existing VM
"""

from optparse import OptionParser
from os import listdir
import os.path as osp
import ConfigParser
from logilabvm.lib import HookCall, _CONFIGFILE, _execute, _gethooks, VMError, show

def run(sysargs, usage=None):
    """
    Function that returns the result of the 'restore' command
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--archive", action="store", dest="archive", 
        help="Name of the archive")
    parser.add_option("-f", "--filename", action="store", dest="filename", 
        help="Full path to the restore file")

    (options, _) = parser.parse_args(sysargs)

    if options.archive and options.filename:
        raise AttributeError, usage

    # check arguments
    if len(sysargs) < 1:
        raise AttributeError, usage
    allvm = show.run(["--all", ])
    names = [ el['name'] for el in allvm ]
    if not sysargs[0] in names:
        raise VMError("%s not an existing VM" % sysargs[0])
    vm = allvm[names.index(sysargs[0])]

    config = ConfigParser.ConfigParser()
    config.read(_CONFIGFILE)

    open(_CONFIGFILE)

    # options
    if options.filename:
        file = osp.abspath(options.filename)
    elif options.archive:
        file = osp.join(config.get('MAIN','archivesdir'), vm['hyper'], vm['name'], options.archive)
    else:
        dir = osp.join(config.get('MAIN','archivesdir'), vm['hyper'], vm['name'])
        try:
            archives = listdir(dir)
            archives.sort()
            archives.reverse()
            file = osp.join(dir, archives[0])
        except OSError or IndexError:
            raise VMError("no archive for %s" % vm['name'])

    # retrieve hooks
    hooks = _gethooks("RESTORE")
    if hooks[vm['hyper']]:
        hookres = _execute("%s %s" % (hooks[vm['hyper']], ' '.join(sysargs)))
        raise HookCall(hookres)

    if vm['hyper'] == "qemu":
        cmdres = _execute("virsh -c %s:///system restore %s" % (vm['hyper'], file))
        vm.update(cmdres)
    else:
        raise NotImplementedError

    return vm
