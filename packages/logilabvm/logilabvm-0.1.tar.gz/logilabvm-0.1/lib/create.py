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
VM Function to create a VM
"""

from optparse import OptionParser, BadOptionError, OptionValueError
import os.path as osp
from re import compile as comp, match
from tempfile import mkstemp
from xml.dom.minidom import Document, Element, Text
import ConfigParser
from logilabvm.lib import _CONFIGFILE, _execute, _gethooks, HookCall, ExecError, VMError, show

OPT_RGX = comp("(?P<key>[^=,]+)=(?P<value>[^,]+)|(?P<flag>[^=,]+)")
def run(sysargs, usage=None):
    """
    Function that migrate a VM and return command results
    """
    parser = OptionParser(usage=usage)
    parser.add_option("--type", action="store", dest="type", type="choice", 
        choices=["qemu", "kvm", "openvz"], help="Define type of VM")
    parser.add_option("--sys", action="store", dest="sys", 
        help="Define system parameters")
    parser.add_option("--dev", action="append", dest="dev", 
        help="Define a device for the VM (can set multiple)")
    parser.add_option("--net", action="append", dest="net", 
        help="Define a network interface for the VM (can set multiple)")
    parser.add_option("--other", action="store", dest="other", 
        help="Define other parameters")
    parser.add_option("--verbose", action="store_true", dest="verbose", 
        default=False, help="Display outputs from scripts")

    (options, _) = parser.parse_args(sysargs)

    if not options.type:
        raise AttributeError, "--type must be set"
    if not options.sys:
        raise AttributeError, "--sys must be set"

    # retrieve hooks
    hooks = _gethooks("CREATE")

    # kvm is just a layer over qemu: same hypervisor
    if options.type == "kvm":
        hyp = "qemu"
    else:
        hyp = options.type
    if hooks[hyp]:
        hookres = _execute("%s %s" % (hooks[hyp], ' '.join(sysargs)))
        raise HookCall(hookres)

    config = ConfigParser.ConfigParser()
    config.read(_CONFIGFILE)
    
    open(_CONFIGFILE)

    ## create the XML docment

    doc = Document()
    ## system
    sysopts = OPT_RGX.findall(options.sys)
    domain = _system(options.type, options.sys) 
    # get the name of the vm
    for opt in sysopts:
        if opt[0] == "name":
            name = opt[1]
            break
    ## devices
    if not options.dev:
        raise AttributeError, "at least on --dev must be set"
    devices = doc.createElement("devices")
    if options.type in ("qemu", "kvm"):
        emulator = Element("emulator")
        vmemulator = Text()
        vmemulator.data = config.get("MAIN", options.type)
        emulator.appendChild(vmemulator)
        devices.appendChild(emulator)
    for device in options.dev:
        devices.appendChild(_device(options.type, device))
    ## network
    if options.net:
        for network in options.net:
            devices.appendChild(_network(options.type, network))
    ## other
    # WARN: actually only support vnc which belongs to the devices subtree
    # result of others is then append to devices but might be diffrent
    # for furthur options
    if options.other:
        othtree = _other(options.type, options.other)
        if othtree:
            devices.appendChild(othtree)
    domain.appendChild(devices)
    doc.appendChild(domain)

    ## run sciprts
    # retrieve scripts
    scripts = _getscripts(hyp)

    ## pre script with no args
    cmdres = _runscript(scripts['pre'], verbose=options.verbose)
    ## sys script
    try:
        cmdres = _runscript(scripts['sys'], 
            args=options.sys, verbose=options.verbose)
    except ExecError:
        _runscript("%s %s sys" % (scripts['failure'], name), 
            args=options.sys, verbose=options.verbose)
        raise
    ## dev script
    iteration = 1
    for device in options.dev:
        try:    
            cmdres = _runscript("%s %s %d" % (scripts['dev'], name, iteration), 
                args=device, verbose=options.verbose)
            iteration = iteration + 1
        except ExecError:
            _runscript("%s %s dev" % (scripts['failure'], name), 
                args=device, verbose=options.verbose)
            raise
    ## net script
    iteration = 1
    if options.net:
        for network in options.net:
            try:
                cmdres = _runscript("%s %s %d" % (scripts['net'], name, iteration), 
                    args=network, verbose=options.verbose)
                iteration = iteration + 1
            except ExecError:
                _runscript("%s %s net" % (scripts['failure'], name), 
                    args=network, verbose=options.verbose)
                raise
    ## other scipt
    if options.other:
        try:
            cmdres = _runscript("%s %s" % (scripts['other'], name), 
                args=options.other, verbose=options.verbose)
        except ExecError, error:
            _runscript("%s %s other" % (scripts['failure'], name), 
                args=options.other, verbose=options.verbose)
            raise error

    # create a tmp file
    tmpfile = mkstemp()
    file = open(tmpfile[1], 'w')
    file.write(doc.toprettyxml(indent='', newl=''))
    file.close()
    # virsh call on for qemu/kvm

    # libvirt is linked to openvz hypervisor deamon so by creating the vm using scripts, 
    # it will automaticly be added to libvirt
    if hyp == "qemu":
        cmdres = _execute("virsh -c %s:///system define %s" % (hyp, tmpfile[1]))
        if cmdres['value']:
            _runscript("%s %s post" % (scripts['failure'], name), verbose=options.verbose)
            raise ExecError(cmdres)

    ## post script with 'name' as args
    try:
        cmdres = _runscript("%s %s" % (scripts['post'], name), verbose=options.verbose)
    except ExecError:
        _runscript("%s post %s" % (scripts['failure'], name), verbose=options.verbose)
        raise

    # post script with args = 'name'
    cmdres = _runscript(scripts['post'], name)
    if cmdres['value']:
        _runscript(scripts['failure'], name)
        raise ExecError(cmdres)

    return name, tmpfile[1]

def _system(type, system):
    """
    Create (and return) an XML tree for the sys option and execute the associated scripts
    """
    sysparser = PermissiveOptionParser()
    sysparser.add_option("--name", action="store", dest="name", 
        help="Name of the VM")
    sysparser.add_option("--mem", action="store", dest="mem", type="int", 
        help="Memory in kB to allocate")
    sysparser.add_option("--vcpu", action="store", dest="vcpu", 
        default=1, type="int", help="Number of CPUs")
    sysparser.add_option("--boot", action="store", dest="boot", default="hd",
        type="choice", choices=["hd", "cdrom", "network"], help="Boot mode (only for Qemu/KVM)")

    # change usage that is used as comment on exception raises
    sysparser.set_usage("--sys %s,other_options=other_values,other_flags,..." % \
        ','.join([ "%s=<value>" % \
        opt._long_opts[0][2:] for opt in sysparser.option_list[1:] ]))
    sysargv = []
    for key, value, flag in OPT_RGX.findall(system):
        if key and value:
            sysargv.append("--%s" % key)
            sysargv.append(value)
        elif flag:
            sysargv.append("--%s" % flag)
        else:
            raise AttributeError, sysparser.get_usage()

    (sysoptions, _) = sysparser.parse_args(sysargv)

    if not sysoptions.name:
        raise AttributeError, "name=<value> must be set"
    if not sysoptions.mem:
        raise AttributeError, "mem=<value> must be set"

    # check if 'name' isn't already used
    allvm = show.run(["--all", ])
    names = [ el['name'] for el in allvm ]
    if sysoptions.name in names:
        raise VMError("%s already exists" % sysoptions.name)

    # domain
    result = Element("domain")
    result.setAttribute("type", type)
    # name
    name = Element("name")
    vmname = Text()
    vmname.data = sysoptions.name
    name.appendChild(vmname)
    result.appendChild(name)
    # memory
    memory = Element("memory")
    vmmemory = Text()
    vmmemory.data = str(sysoptions.mem)
    memory.appendChild(vmmemory)
    result.appendChild(memory)
    # vcpus
    vcpu = Element("vcpu")
    vmvcpu = Text()
    vmvcpu.data = str(sysoptions.vcpu)
    vcpu.appendChild(vmvcpu)
    result.appendChild(vcpu)

    # clock
    clock = Element("clock")
    clock.setAttribute("sync", "utc")
    result.appendChild(clock)

    # os
    osys = Element("os")
    ostype = Element("type")
    ostype.setAttribute("arch", "i686")
    ostype.setAttribute("machine", "pc")
    osvirt = Text()
    if type == "qemu" or type == "kvm":
        osvirt.data = "hvm"
        # boot
        boot = Element("boot")
        boot.setAttribute("dev", sysoptions.boot)
        osys.appendChild(boot)
        # features
        features = Element("features")
        acpi = Element("acpi")
        features.appendChild(acpi)
        result.appendChild(features)
    elif type == "openvz":
        osvirt.data = "exe"
        # init
        initpath = Text()
        initpath.data = "/sbin/init"
        init = Element("init")
        init.appendChild(initpath)
        osys.appendChild(init)
    else:
        raise NotImplementedError
    ostype.appendChild(osvirt)
    osys.appendChild(ostype)
    result.appendChild(osys)

    # states
    vmstate = Text()
    vmstate.data = "destroy"
    state = Element("on_poweroff")
    state.appendChild(vmstate)
    result.appendChild(state)
    vmstate = Text()
    vmstate.data = "restart"
    state = Element("on_reboot")
    state.appendChild(vmstate)
    result.appendChild(state)
    vmstate = Text()
    vmstate.data = "restart"
    state = Element("on_crash")
    state.appendChild(vmstate)
    result.appendChild(state)

    return result

def _device(type, dev):
    """
    Create (and return) an XML tree for the dev option and execute the associated scripts
    """
    devparser = PermissiveOptionParser()
    devparser.add_option("--template", action="store", dest="template", 
        help="Name of the template to use for the guest system \
        (only for OpenVz / if set, this should be the only option)")
    devparser.add_option("--file", action="store", dest="file", 
        help="ISO/Image file to use")
    devparser.add_option("--device", action="store", dest="device", type="choice", 
        choices=["disk", "cdrom"], help="Device type (used with 'file' option)")
    devparser.add_option("--target", action="store", dest="target", 
        help="OpenVz: path to the target (default: '/') / Qemu/KVM: name of the target device")

    # change usage that is used as comment on exception raises
    devparser.set_usage("--dev %s,other_options=other_values,other_flags,..." % \
        ','.join([ "%s=<value>" % \
        opt._long_opts[0][2:] for opt in devparser.option_list[1:] ]))
    devargv = []
    for key, value, flag in OPT_RGX.findall(dev):
        if key and value:
            devargv.append("--%s" % key)
            devargv.append(value)
        elif flag:
            devargv.append("--%s" % flag)
        else:
            raise AttributeError, devparser.get_usage()

    (devoptions, _) = devparser.parse_args(devargv)

    if devoptions.template:
        if type != "openvz":
            raise AttributeError, "%s does not handle templates" % type
        result = Element("filesystem")
        result.setAttribute("type", "template")
        source = Element("source")
        source.setAttribute("name", devoptions.template)
        target = Element("target")
        if devoptions.target:
            target.setAttribute("dir", devoptions.target)
        else:
            target.setAttribute("dir", "/")
        result.appendChild(source)
        result.appendChild(target)
    elif devoptions.file:
        if not devoptions.device and not devoptions.target:
            raise AttributeError, "'device' and 'target' must be set with 'file' option"
        result = Element("disk")
        result.setAttribute("type", "file")
        result.setAttribute("device", devoptions.device)
        source = Element("source")
        source.setAttribute("file", devoptions.file)
        target = Element("target")
        target.setAttribute("dev", devoptions.target)
        result.appendChild(source)
        result.appendChild(target)
    else:
        raise AttributeError, "'template' or 'file' must be set"

    return result

def _network(type, net):
    """
    Create (and return) an XML tree for the net option and execute the associated scripts
    """
    netparser = PermissiveOptionParser()
    netparser.add_option("--method", action="store", dest="method", type="choice", 
        choices=["bridge", "user"], help="Method to use for the network interface")
    netparser.add_option("--mac", action="store", dest="mac", help="Mac address")
    netparser.add_option("--bridge", action="store", dest="bridge", 
        help="The bridge to connect to (used with 'bridge' method / only for Qemu/KVM)")
    netparser.add_option("--interface", action="store", dest="interface", 
        help="The virtual network interface name mapped on the host \
        (used with 'bridget' method / automatic if not set)")

    # change usage that is used as comment on exception raises
    netparser.set_usage("--net %s,other_options=other_values,other_flags,..." % \
        ','.join([ "%s=<value>" % \
        opt._long_opts[0][2:] for opt in netparser.option_list[1:] ]))
    devargv = []
    for key, value, flag in OPT_RGX.findall(net):
        if key and value:
            devargv.append("--%s" % key)
            devargv.append(value)
        elif flag:
            devargv.append("--%s" % flag)
        else:
            raise AttributeError, netparser.get_usage()

    (netoptions, _) = netparser.parse_args(devargv)

    if netoptions.method == "bridge":
        result = Element("interface")
        if not netoptions.mac or not netoptions.bridge:
            raise AttributeError, "'mac' and 'bridge' must be set"
        result.setAttribute("type", "bridge")
        mac = Element("mac")
        mac.setAttribute("address", netoptions.mac)
        source = Element("source")
        source.setAttribute("bridge", netoptions.bridge)
        if netoptions.interface:
            target = Element("target")
            target.setAttribute("dev", netoptions.interface)
            result.appendChild(target)
        result.appendChild(mac)
        result.appendChild(source)
    elif netoptions.method == "user":
        result = Element("interface")
        if not netoptions.mac:
            raise AttributeError, "'mac' must be set"
        result.setAttribute("type", "user")
        mac = Element("mac")
        mac.setAttribute("address", netoptions.mac)
        result.appendChild(mac)
    else:
        raise AttributeError, "'template' or 'file' must be set"

    return result

def _other(type, other):
    """
    Create (and return) an XML tree for the other option and execute the associated scripts
    """
    othparser = PermissiveOptionParser()
    othparser.add_option("--vnc", action="store", dest="vnc", type="int",
        help="Add vnc support with associated port")

    # change usage that is used as comment on exception raises
    othparser.set_usage("--sys %s,other_options=other_values,other_flags,..." % \
        ','.join([ "%s=<value>" % \
        opt._long_opts[0][2:] for opt in othparser.option_list[1:] ]))
    othargv = []
    for key, value, flag in OPT_RGX.findall(other):
        if key and value:
            othargv.append("--%s" % key)
            othargv.append(value)
        elif flag:
            othargv.append("--%s" % flag)
        else:
            raise AttributeError, othparser.get_usage()

    (othoptions, _) = othparser.parse_args(othargv)

    if othoptions.vnc:
        result = Element("graphics")
        result.setAttribute("type", "vnc")
        result.setAttribute("port", str(othoptions.vnc))
        result.setAttribute("keymap", "fr")
    else:
        result = None

    return result

def _getscripts(hyper):
    """
    Retrieve scripts from _CONFIGFILE for the hypervisor. Return a dictionary with None if no scripts
    """
    config = ConfigParser.ConfigParser()
    config.read(_CONFIGFILE)

    open(_CONFIGFILE)

    dir = config.get('MAIN','scriptsdir')
    scripts = config.items('CREATE')
    
    result = {}
    for script in scripts:
        mat = match("%s_(?P<step>\w+)" % hyper, script[0])
        if mat:
            result[mat.groupdict()['step']] = osp.join(dir, script[1])
    
    return result

def _runscript(script, args=None, verbose=False):
    """
    Run the script with args formated: KEY=value or flag and return result.
    """
    if not args:
        cmdres = _execute("%s" % script, verbose=verbose)
        return cmdres

    argv = []
    env = {}
    for key, value, flag in OPT_RGX.findall(args):
        if key and value:
            argv.append("%s=%s" % (key.upper(), value))
            env[key.upper()] = value
        elif flag:
            argv.append(flag)
            env[flag] = ''
    cmdres = _execute("%s %s" % (script, ' '.join(argv)), verbose=verbose, env=env)
    if cmdres['value']:
        raise ExecError(cmdres)

    return cmdres

class PermissiveOptionParser(OptionParser):
    """
    OptionParser with no exit on unknown options
    """
    def parse_args(self, args=None, values=None):
        """
        Same as OptionParser.parse_args except don't fail on BadOptionError
        """
        rargs = self._get_args(args)
        if values is None:
            values = self.get_default_values()

        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        try:
            self._process_args(largs, rargs, values)
        # Here is the fix
        except BadOptionError:
            pass
        except OptionValueError, err:
            self.error(str(err))

        args = largs + rargs
        return self.check_values(values, args)
