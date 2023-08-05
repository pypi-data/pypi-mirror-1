"""
Module containing the Disk object for a Physical Disk
Inherits from: pyVC.Disks.Base
"""
__revision__ = "$Revision: 263 $"

from pyVC.Disks import Base

class Disk( Base.Disk ):
    """
    This object defines a Disk object for a physical disk.
    
    disk = Disk(realmachines, path)
    realmachines is a list of Machine objects where this physical disk is valid.
    path is the full or abbreviated path to the physical device.
    """
    __revision__ = "$Revision: 263 $"
    
    def __init__(self, realmachines, path, **keywords):

        Base.Disk.__init__(self, realmachines, path)

        from pyVC.errors import DiskError
        
        for realmachine in realmachines:
            if not realmachine.exists(self.path):
                raise DiskError, ( "ERROR: Could not open disk device %s." % (self.path), \
                                   1, \
                                   realmachine.hostname \
                                 )

        self._keywords = keywords

    def __str__(self):
        return self.path

    def qemu(self, disks):
        return "-%s %s" % (disks.pop(0), self.path)

    def uml(self, disks):
        return "%s=%s" % (disks.pop(0), self.path)

    def xen(self, disks):
        from elementtree.ElementTree import Element, SubElement
        disk = Element('disk', type='block')
        SubElement(disk, 'driver', name='phy')
        SubElement(disk, 'source', dev=str(self.path))
        SubElement(disk, 'target', dev=str(disks.pop(0)))

        return disk

    def __repr__(self):
        return "Disk(%s, device = \"%s\")" % (self.__realmachines, self.path)
