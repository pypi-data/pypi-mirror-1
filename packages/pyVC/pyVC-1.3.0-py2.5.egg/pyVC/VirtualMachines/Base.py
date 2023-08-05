##
# Module containing the base object for a VirtualMachine.
##

__revision__ = "$Revision: 296 $"

##
# This class defines the base object for a VirtualMachine.
#
# @param realmachine A Machine object where the VM will live.
# @param name The name of the VM.
# @param addrs A string containing a comma-separated list of IP addresses assigned to the VM.
# @param macaddrs A list of strings containing MAC addresses for the VM's network interfaces.
# @param disks A list of Disk objects to be used by this VM.
# @param bootdisk A Disk object for this VM to boot from.
# @param networks A list of Network objects to connect this VM to.
# @param memory A string containing the amount of RAM, in megabytes, to allocate to this VM.
# @param kernel A string containing the path on the Machine's filesystem to the kernel image for this VM.
# @param initrd A string containing the path on the Machine's filesystem to the initrd image for this VM.
# @param kernelargs A string containing the kernel arguments to pass this VM.
# @param root A string containing the path to the root device on the VM's filesystem.
class VM(object):
    """This base object defines a Virtual Machine"""
    __revision__ = "$Revision: 296 $"

    errors = ()

    platforms = ()
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  addrs = None, \
                  macaddrs = None, \
                  disks = None, \
                  bootdisk = None, \
                  networks = None, \
                  memory = "32", \
                  vmgroup = 1, \
                  kernel = "", \
                  kernelargs = "", \
                  initrd = "", \
                  root = "", \
                  **keywords ):

        self.__keywords = keywords

        if networks:
            self.__networks = networks
        else:
            self.__networks = []
            
        if disks:
            self.__disks = disks
        else:
            self.__disks = []

        self.__name = name
        self.__realmachine = realmachine
        self.__memory = memory
        self.__vmgroup = vmgroup
        self.__kernel = kernel
        self.__initrd = initrd
        self.__kernelargs = kernelargs
        self.__root = root
        self.__bootdisk = bootdisk

        if addrs:
            self.__addrs = addrs.split(',')
        else:
            self.__addrs = []

        self.__macaddrs = macaddrs
        self.__status = "stopped"
        
        realmachine.check_errors( self.errors )
        realmachine.check_platform( self.platforms )

        from pyVC.errors import VMError

        if self.kernel:
            if not self.realmachine.isfile(self.kernel):
                if 'kernels_path' in self.realmachine.config['global'] and self.realmachine.isfile(self.realmachine.config['global']['kernels_path'] + '/' + self.kernel):
                    self.__kernel = self.realmachine.config['global']['kernels_path'] + '/' + self.kernel
                else:
                    raise VMError, ( "ERROR: Could not open kernel %s" % (self.kernel), \
                                     0, \
                                     self.realmachine.hostname, \
                                     self.vmname \
                                   )
        
        if self.initrd:
            if not self.realmachine.isfile(self.initrd):
                if 'kernels_path' in self.realmachine.config['global'] and self.realmachine.isfile(self.realmachine.config['global']['kernels_path'] + '/' + self.initrd):
                    self.__initrd = self.realmachine.config['global']['kernels_path'] + '/' + self.initrd
                else:
                    raise VMError, ( "ERROR: Could not open initrd %s" % (self.initrd), \
                                     1, \
                                     self.realmachine.hostname, \
                                     self.vmname \
                                   )

        if networks:
            networks[0].add_vm(self, self.__addrs)

    def __del__(self):
        self.stop()

    # Accessors
        
    def _get_bootdisk(self):
        """Returns a the boot disk assigned to a VM"""
        return self.__bootdisk
    
    def _get_disks(self):
        """Returns a list of disks allocated to a VM"""
        return self.__disks
    
    def _get_networks(self):
        """Returns a list of networks allocated to a VM"""
        return self.__networks

    def _get_addr(self):
        """Returns the value of self.__addr"""
        return self.__addrs[0]

    def _get_addrs(self):
        """Returns the value of self.__addr"""
        return self.__addrs

    def _get_vmname(self):
        """Returns the name assigned to a VM"""
        return self.__name
    
    def _get_macaddrs(self):
        """Returns the MAC addresses assigned to a VM"""
        return self.__macaddrs

    def _get_root(self):
        """Returns the root assigned to a VM"""
        return self.__root

    def _set_root(self, root):
        """Sets the root assigned to a VM"""
        self.__root = root

    def _set_macaddrs(self, macaddrs):
        """Sets the MAC addresses assigned to a VM"""
        self.__macaddrs = macaddrs

    def _get_macaddr(self):
        """Returns the MAC address assigned to a VM"""
        if self.__macaddrs:
            return self.__macaddrs[0]
        else:
            return None

    def _get_realmachine(self):
        """Returns the MAC address assigned to a VM"""
        return self.__realmachine

    def _get_memory(self):
        """Returns the amount of memory allocated to a VM"""
        return self.__memory
    
    def _set_memory(self, memory):
        """Sets the amount of memory allocated to a VM"""
        self.__memory = memory
        
    def _get_vmgroup(self):
        """Returns the vmgroup assigned to a VM"""
        return self.__vmgroup

    def _get_kernel(self):
        """Gets the value of self.__kernel"""
        return self.__kernel

    def _get_kernelargs(self):
        """Gets the value of self.__kernelargs"""
        return self.__kernelargs

    def _get_initrd(self):
        """Gets the value of self.__initrd"""
        return self.__initrd
    
    def _set_vmgroup(self, vmgroup):
        """Sets the vmgroup assigned to a VM"""
        self.__vmgroup = vmgroup

    def _get_status( self ):
        """Returns the status of a VM"""
        return self.__status

    def _set_status( self, status ):
        """Sets the status of a VM"""

        if status == 'stopped' or \
           status == 'started' or \
           status == None:
            self.__status = status

    # Properties
    
    memory = property(_get_memory, _set_memory)
    disks = property(_get_disks)
    bootdisk = property(_get_bootdisk)
    networks = property(_get_networks)
    vmname = property(_get_vmname)
    vmgroup = property(_get_vmgroup, _set_vmgroup)
    macaddrs = property(_get_macaddrs, _set_macaddrs)
    macaddr = property(_get_macaddr)
    realmachine = property(_get_realmachine)
    status = property(_get_status, _set_status)
    addr = property(_get_addr)
    addrs = property(_get_addrs)
    kernel = property(_get_kernel)
    kernelargs = property(_get_kernelargs)
    initrd = property(_get_initrd)
    root = property(_get_root, _set_root)
    
    # Abstract methods

    def start( self ):
        """Abstract method to start a VM"""
        raise NotImplementedError
    
    def stop( self ):
        """Abstract method to stop a VM"""
        raise NotImplementedError
