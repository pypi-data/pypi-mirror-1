#!/usr/bin/python
from getopt import getopt, GetoptError
from sys import argv, exit
from time import sleep

from pyVC.RemoteMachine import RemoteMachine

import Pyro.core
import os
import socket

daemonize = False
hostname = ""
object = "pyvcd"
port = 7766
serverip = ""
serverport = 7766
logfile = ""
pidfile = ""

usage_str = """
Head node:
    %s [ -d [-l logfile] [-i pidfile] ] [-b server address] [-j server port]

Clients:
    %s -h hostname -p port [ -d [-l logfile] [-i pidfile] ] [-b server address] [-j server port]
""" % (argv[0], argv[0])

WORKDIR = "/tmp"
UMASK = 0
REDIRECT = os.devnull

class PyvcdData(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)

        self._machines = {}
        self._specification = None
        self._networks = {}
        self._vms = {}
        self._helpers = []

    def add_machine(self, newmachine ):

        from pyVC.Machine import Machine

        if issubclass( type( newmachine ), Machine ):
            self._machines[None] = newmachine
        else:
            machine = Pyro.core.getAttrProxyForURI(newmachine)
            print "DEBUG: joined machine: ", machine.hostname
            self._machines[machine.hostname] = machine

    def del_machine(self, hostname):

        if hostname in self.machines():
            del self._machines[hostname]
            print "DEBUG: lost machine: ", hostname

    def VM(self, vmtype, hostname, *args, **kwargs):

        if vmtype == "qemu":
            from pyVC.VirtualMachines.QEMU import VM
        elif vmtype == "uml":
            from pyVC.VirtualMachines.UML import VM
        elif vmtype == "xen":
            from pyVC.VirtualMachines.Xen import VM
        else:
            raise ValueError,  "ERROR: unsupported VM type %s" % (vmtype)

        vm = VM(self.machine(hostname), *args, **kwargs)
        self._vms[vm.name] = vm

    def Network(self, networktype, hostnames, *args, **kwargs):

        if networktype == "vde1":
            from pyVC.Networks.VDE1 import Network
        elif networktype == "multicast":
            from pyVC.Networks.Multicast import Network
        elif networktype == "linux":
            from pyVC.Networks.Linux import Network
        else:
            raise ValueError,  "ERROR: unsupported network type %s" % (networktype)

        network = Network([self.machine(hostname) for hostname in hostnames], *args, **kwargs)
        self._networks[network.lanname] = network
        
    def Helper(self, helpertype, hostname, *args, **kwargs):

        if helpertype == "dhcp":
            from pyVC.Helpers.DHCP import Helper
        elif helpertype == "interface":
            from pyVC.Helpers.Interface import Helper
        elif helpertype == "router":
            from pyVC.Helpers.Router import Helper
        else:
            raise ValueError,  "ERROR: unsupported helper type %s" % (helpertype)

        helper = Helper(self.machine(hostname), *args, **kwargs)
        self._helpers.append(helper)

    def host(self, vmname):

        for network in self._networks:
            for host in network.vms:
                if host.vmname == vmname:
                    return host

    def _get_machinenames(self):
        return [machine.hostname for machine in self._machines.values()]

    def _get_machines(self):
        return self._machines.values()

    def _get_networks(self):
        return self._networks.values()

    def _get_vms(self):
        return self._vms.values()

    def _get_hosts(self):
        hosts = []

        for network in self._networks:
            for host in network.vms:
                if host.vmname not in hosts:
                    hosts.append(host.vmname)

        return hosts

    def _get_helpers(self):
        return self._helpers

    def start(self, filename):

        for machine in self._machines.values():
            machine.refresh()

        from pyVC.Specifications.VCML import Specification

        try:
            self._specification = Specification(self._machines, filename)
            self._networks = self._specification.create()
            self._specification.start()
        except:
            self._specification = None
            self._networks = {}
            raise

    def stop(self):

        if self._specification:
            self._specification.stop()
            self._networks = {}
            self._specification = None
        else:
            return 'no configuration loaded'

    def status(self):

        if self._specification:
            return self._specification.status()
        else:
            return 'no configuration loaded'

    def initserver(self, vmname):
        host = self.host(vmname)

        if host.status != "started":
            raise RuntimeError, (2, 'ERROR: system not started')
        
        rc = host.console(socket=True)
        if rc == None:
            raise RuntimeError, (2, 'ERROR: console already connected')
        else:
            return rc

    def startserver(self, vmname):
        self.host(vmname).serve()

    machinenames = property(_get_machinenames)
    machines = property(_get_machines)
    networks = property(_get_networks)
    vms = property(_get_vms)
    helpers = property(_get_helpers)
    hosts = property(_get_hosts)

def usage ():
    print usage_str
    exit (-1)

try:
    optlist, otherlist = getopt(argv[1:], 'b:dl:h:p:i:n:v:j:')
except GetoptError:
    usage()

for opt in optlist:
    if opt[0] == '-h':
        hostname = str(opt[1])
    if opt[0] == '-p':
        port = str(opt[1])
    if opt[0] == '-b':
        serverip = str(opt[1])
    if opt[0] == '-j':
        serverport = str(opt[1])
    if opt[0] == '-d':
        daemonize = True
    if opt[0] == '-l':
        logfile = str(opt[1])
    if opt[0] == '-i':
        pidfile = str(opt[1])
    if opt[0] == '-n':
        networktype = str(opt[1])
    if opt[0] == '-v':
        vmtype = str(opt[1])

Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

def start_daemon(serverip, serverport):
    Pyro.core.initServer(banner=0)
    try:
        daemon = Pyro.core.Daemon(host=serverip, port=serverport)
    except socket.error, e:
        print "ERROR: please use -b to specify IP address to bind to"
        exit(0)

    return daemon

try:
    machine = RemoteMachine()
except ValueError, e:
    print e
    exit(0)

if not hostname:
    pyvcd = PyvcdData()
    pyvcd.add_machine(machine)

    daemon = start_daemon(serverip, serverport)
    
    uri = daemon.connect(pyvcd, "pyvcd")

    print "Server running at %s" % (uri)

else:
    Pyro.core.initClient(0)
    uri = "PYROLOC://%s:%s/%s" % (hostname, port, "pyvcd")
    pyvcd = Pyro.core.getAttrProxyForURI(uri)
    pyvcd._setOneway('add_machine')

    daemon = start_daemon(serverip, serverport)

    uri = daemon.connect(machine, "machine")

    if machine.hostname not in pyvcd.machinenames:
        try:
            pyvcd.add_machine(uri)
        except Pyro.errors.ProtocolError, e:
            print "ERROR: Pyro returned \"%s\"." % e
            exit(-1)
    else:
        print "ERROR: %s already exists in pyvcd." % machine.hostname
        exit(-1)

if daemonize:
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.strerror, e.errno)
    if (pid == 0):
        os.setsid()
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, "%s [%d]" % (e.strerror, e.errno)

        if (pid == 0):
            os.chdir(WORKDIR)
            os.umask(UMASK)
            daemon.requestLoop()
        else:
            try:
                pidfd = open(pidfile, 'w')
                pidfd.write("%s\n" % (pid))
                pidfd.close()
            except:
                pass
            os._exit(0)
    else:
        os._exit(0)
        
    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD
  
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass

    os.open(REDIRECT, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)
    
else:
    print "Press CTRL-C to exit"
    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        pass

if hostname:
    pyvcd.del_machine(machine.hostname)
