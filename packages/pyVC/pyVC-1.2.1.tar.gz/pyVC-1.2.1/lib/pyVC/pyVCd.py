"""
Module containing the data object for pyVCd.

"""

__revision__ = "$Revision: 245 $"

import Pyro

class pyVCdData(Pyro.core.ObjBase):
    def __init__(self):
        Pyro.core.ObjBase.__init__(self)

        self._machines = {}
        self._specification = None
        self._networks = {}
        self._vms = {}
        self._helpers = []

    def add_machine(self, newmachine ):
        """
        Adds a real machine to the pyVC ring.
        """

        from pyVC.Machine import Machine

        if issubclass( type( newmachine ), Machine ):
            self._machines[None] = newmachine
        else:
            machine = Pyro.core.getAttrProxyForURI(newmachine)
            print "DEBUG: joined machine: ", machine.hostname
            self._machines[machine.hostname] = machine

    def del_machine(self, hostname):
        """
        Deletes a real machine from the pyVC ring.
        """

        if hostname in self.machines():
            del self._machines[hostname]
            print "DEBUG: lost machine: ", hostname

#    def VM(self, vmtype, hostname, *args, **kwargs):
#
#        if vmtype == "qemu":
#            from pyVC.VirtualMachines.QEMU import VM
#        elif vmtype == "uml":
#            from pyVC.VirtualMachines.UML import VM
#        elif vmtype == "xen":
#            from pyVC.VirtualMachines.Xen import VM
#        else:
#            raise ValueError,  "ERROR: unsupported VM type %s" % (vmtype)
#
#        vm = VM(self.machine(hostname), *args, **kwargs)
#        self._vms[vm.name] = vm
#
#    def Network(self, networktype, hostnames, *args, **kwargs):
#
#        if networktype == "vde1":
#            from pyVC.Networks.VDE1 import Network
#        elif networktype == "multicast":
#            from pyVC.Networks.Multicast import Network
#        elif networktype == "linux":
#            from pyVC.Networks.Linux import Network
#        else:
#            raise ValueError,  "ERROR: unsupported network type %s" % (networktype)
#
#        network = Network([self.machine(hostname) for hostname in hostnames], *args, **kwargs)
#        self._networks[network.lanname] = network
#        
#    def Helper(self, helpertype, hostname, *args, **kwargs):
#
#        if helpertype == "dhcp":
#            from pyVC.Helpers.DHCP import Helper
#        elif helpertype == "interface":
#            from pyVC.Helpers.Interface import Helper
#        elif helpertype == "router":
#            from pyVC.Helpers.Router import Helper
#        else:
#            raise ValueError,  "ERROR: unsupported helper type %s" % (helpertype)
#
#        helper = Helper(self.machine(hostname), *args, **kwargs)
#        self._helpers.append(helper)

    def host(self, vmname):
        """
        Finds a VM from the pyVC ring's list of VMs.
        """

        for network in self._networks:
            for host in network.vms:
                if host.vmname == vmname:
                    return host

    def _get_machinenames(self):
        """
        Returns a list of machine names of machines in the pyVCd ring.
        """

        return [machine.hostname for machine in self._machines.values()]

    def _get_machines(self):
        """
        Returns a list of machines in the pyVCd ring.
        """
        
        return self._machines.values()

#    def _get_networks(self):
#        """
#        Returns a list of networks in the pyVCd ring.
#        """
#        
#        return self._networks.values()

#    def _get_vms(self):
#        """
#        Returns a list of VMs in the pyVCd ring.
#        """
#        
#        return self._vms.values()

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

        from pyVC.Specifications.VCML import Specification
        from pyVC.errors import PYVCDError

        for machine in self._machines.values():
            machine.refresh()

        if not self._specification:
            try:
                self._specification = Specification(self._machines, filename)
                self._networks = self._specification.create()
                self._specification.start()
            except:
                self._specification = None
                self._networks = {}
                raise
        else:
            raise PYVCDError, ( "ERROR: Specification already loaded.", \
                                1 \
                              )

    def stop(self):

        from pyVC.errors import PYVCDError

        if self._specification:
            self._specification.stop()
            self._networks = {}
            self._specification = None
        else:
            raise PYVCDError, ( "ERROR: Specification not loaded.", \
                                2 \
                              )

    def status(self):

        from pyVC.errors import PYVCDError

        if self._specification:
            return self._specification.status()
        else:
            raise PYVCDError, ( "ERROR: Specification not loaded.", \
                                2 \
                              )

    def initserver(self, vmname):

        from pyVC.errors import PYVCDError

        host = self.host(vmname)

        if host.status != "started":
            raise PYVCDError, ( "ERROR: VM not found / running.", \
                                3 \
                              )
        
        rc = host.console(socket=True)
        if rc == None:
            raise PYVCDError, ( "ERROR: Console already in use.", \
                                4 \
                              )
        else:
            return rc

    def startserver(self, vmname):
        self.host(vmname).serve()

    machinenames = property(_get_machinenames)
    machines = property(_get_machines)
#    networks = property(_get_networks)
#    vms = property(_get_vms)
    helpers = property(_get_helpers)
    hosts = property(_get_hosts)

