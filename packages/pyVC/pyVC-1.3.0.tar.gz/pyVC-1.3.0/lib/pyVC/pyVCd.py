##
# Module containing the data object for pyVCd.
##

__revision__ = "$Revision: 245 $"

import Pyro

##
# Class containing the shared data object for pyVCd and the wrapper methods to be called by the client programs.
#
class pyVCdData(Pyro.core.ObjBase):

    def __init__(self):
        Pyro.core.ObjBase.__init__(self)

        self._machines = {}
        self._specification = None
        #self._networks = {}
        #self._vms = {}
        #self._helpers = []

    ##
    # Adds a machine to the pyVCd list of machines.
    # 
    # @param machine A Machine object, a subclass of a Machine object, or a Pyro URI for a remote Machine object.
    def add_machine(self, machine ):
        """
        Adds a real machine to the pyVC ring.
        """

        from pyVC.Machine import Machine

        if issubclass( type( machine ), Machine ):
            self._machines[None] = machine
        else:
            machine = Pyro.core.getAttrProxyForURI(machine)
            print "DEBUG: joined machine: ", machine.hostname
            self._machines[machine.hostname] = machine
    ##
    # Deletes a real machine from the pyVCd list of machines.
    #
    # @param hostname The hostname of the Machine object to delete.
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

    ##
    # Finds a VM by name from the pyVCd's list of VMs.
    #
    # @param vmname The name of the virtual machine to find.
    def host(self, vmname):

        for network in self._networks:
            for host in network.vms:
                if host.vmname == vmname:
                    return host

    def _get_machinenames(self):

        return [machine.hostname for machine in self._machines.values()]

    def _get_machines(self):

        return [machine for machine in self._machines.values()]

#    def _get_networks(self):
#        return self._networks.values()

#    def _get_vms(self):
#        return self._vms.values()

#    def _get_helpers(self):
#        return self._helpers

    def _get_hosts(self):
        hosts = []

        for network in self._networks:
            for host in network.vms:
                if host.vmname not in hosts:
                    hosts.append(host.vmname)

        return hosts
    ##
    # Loads a Specification from the specified file and starts the virtual network.
    #
    # @param filename The full path to the VCML specification.
    # @exception pyVCdError Specification is already loaded.
    def start(self, filename):

        from pyVC.Specifications.VCML import Specification
        from pyVC.errors import pyVCdError

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
            raise pyVCdError, ( "ERROR: Specification is already loaded.", \
                                1 \
                              )

    ## 
    # Stops the currently loaded virtual network.
    #
    # @exception pyVCdError Specification is not loaded.
    def stop(self):

        from pyVC.errors import pyVCdError

        if self._specification:
            self._specification.stop()
            self._networks = {}
            self._specification = None
        else:
            raise pyVCdError, ( "ERROR: Specification is not loaded.", \
                                2 \
                              )

    ## 
    # Queries the status the currently loaded virtual network.
    #
    # @exception pyVCdError Specification is not loaded.
    def status(self):

        from pyVC.errors import pyVCdError

        if self._specification:
            return self._specification.status()
        else:
            raise pyVCdError, ( "ERROR: Specification is not loaded.", \
                                2 \
                              )

    ##
    # Initializes the console server for a VM.
    #
    # @param vmname The name of the VirtualMachine to initialize.
    # @return A very meaningful return code.
    # @exception pyVCdError VM not found / running.
    # @exception pyVCdError Console already in use.
    def initserver(self, vmname):

        from pyVC.errors import pyVCdError

        host = self.host(vmname)

        if host.status != "started":
            raise pyVCdError, ( "ERROR: VM not found / running.", \
                                3 \
                              )
        
        rc = host.console(socket=True)
        if rc == None:
            raise pyVCdError, ( "ERROR: Console already in use.", \
                                4 \
                              )
        else:
            return rc

    ##
    # Starts the serving loop on a VM.
    #
    # @param vmname The name of the VirtualMachine to start.
    def startserver(self, vmname):
        self.host(vmname).serve()

    ##
    # A list of hostnames of Machine objects associated with the pyVCdData object.
    machinenames = property(_get_machinenames)

    ##
    # A list of Machine objects associated with the pyVCdData object.
    machines = property(_get_machines)

    ##
    # A list of names of Virtualmachine objects associated with the pyVCdData object.
    hosts = property(_get_hosts)

#    networks = property(_get_networks)
#    vms = property(_get_vms)
#    helpers = property(_get_helpers)
