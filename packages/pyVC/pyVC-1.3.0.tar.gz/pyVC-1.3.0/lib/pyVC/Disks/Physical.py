"""
Module containing the Disk object for a Physical Disk
Inherits from: pyVC.Disks.Base
"""
__revision__ = "$Revision: 296 $"

from pyVC.Disks import Base

##
# This class defines a Disk object for a physical disk device..
#
# @realmachines A list of Machine objects this disk should exist on.
# @param path The path to the disk device.
class Disk( Base.Disk ):

    __revision__ = "$Revision: 296 $"
    
    def __init__(self, realmachines, path, **keywords):

        Base.Disk.__init__(self, realmachines, path, **keywords)

        from pyVC.errors import DiskError
        
        for realmachine in realmachines:
            if not realmachine.exists(self.path):
                raise DiskError, ( "ERROR: Could not open disk device %s." % (self.path), \
                                   1, \
                                   realmachine.hostname \
                                 )

    def __str__(self):
        return self.path

    ##
    # Function that returns the proper parameters to access this disk for a QEMU VM.
    #
    # @param disks The list of available disks on the VM.
    # @returns A string containing the parameters for the VM.
    def qemu(self, disks):
        return "-%s %s" % (disks.pop(0), self.path)

    ##
    # Function that returns the proper parameters to access this disk for a UML VM.
    #
    # @param disks The list of available disks on the VM.
    # @returns A string containing the parameters for the VM.
    def uml(self, disks):
        return "%s=%s" % (disks.pop(0), self.path)

    ##
    # Function that returns the proper parameters to access this disk for a Xen VM.
    #
    # @param disks The list of available disks on the VM.
    # @returns A XML ElementTree containing the parameters for the VM.
    def xen(self, disks):
        from lxml.etree import Element, SubElement
        disk = Element('disk', type='block')
        SubElement(disk, 'driver', name='phy')
        SubElement(disk, 'source', dev=str(self.path))
        SubElement(disk, 'target', dev=str(disks.pop(0)))

        return disk

    def __repr__(self):
        return "Disk(%s, device = \"%s\")" % (self.__realmachines, self.path)
