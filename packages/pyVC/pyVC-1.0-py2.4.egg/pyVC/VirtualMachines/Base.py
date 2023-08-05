"""This package contains the base classes to implement a VM"""
__revision__ = "$Revision: 227 $"

class VM(object):
    """This base object defines a Virtual Machine"""
    __revision__ = "$Revision: 227 $"

    errors = ()

    platforms = ()
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  addrs = None, \
                  macaddr = "", \
                  disks = None, \
                  networks = None, \
                  memory = 32, \
                  vmgroup = 1, \
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
        if addrs:
            self.__addrs = addrs.split(',')
        else:
            self.__addrs = []
        self.__macaddr = macaddr
        self.__status = "stopped"
        
        realmachine.check_errors( self.errors )
        realmachine.check_platform( self.platforms )
        
        networks[0].add_vm(self, self.__addrs)

    def __del__(self):
        self.stop()

    # Accessors
        
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
        return self.__macaddr

    def _get_macaddr(self):
        """Returns the MAC address assigned to a VM"""
        if self.__macaddr:
            return self.__macaddr[0]
        else:
            return ""

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
    networks = property(_get_networks)
    vmname = property(_get_vmname)
    vmgroup = property(_get_vmgroup, _set_vmgroup)
    macaddrs = property(_get_macaddrs)
    macaddr = property(_get_macaddr)
    realmachine = property(_get_realmachine)
    status = property(_get_status, _set_status)
    addr = property(_get_addr)
    addrs = property(_get_addrs)
    
    # Abstract methods

    def start( self ):
        """Abstract method to start a VM"""
        raise NotImplementedError
    
    def stop( self ):
        """Abstract method to stop a VM"""
        raise NotImplementedError
