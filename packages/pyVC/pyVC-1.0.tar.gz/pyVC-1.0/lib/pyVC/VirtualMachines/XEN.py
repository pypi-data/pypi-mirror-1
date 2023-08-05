"""This package contains the classes to implement a Xen VM"""
__revision__ = "$Revision: 216 $"

from pyVC.VirtualMachines import Base

class VM( Base.VM ):
    """This object defines a Xen Virtual Machine"""
    __revision__ = "$Revision: 216 $"
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  macaddr = "", \
                  memory = 0, \
                  networks = None, \
                  disks = None, \
                  vmgroup = 1, \
                  **keywords ):
        Base.VM.__init__( self, \
                          realmachine, \
                          name, \
                          macaddr, \
                          disks, \
                          networks, \
                          memory, \
                          vmgroup, \
                          **keywords )
