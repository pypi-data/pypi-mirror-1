"""
Module containing the Disk object for a Disk Image.
Inherits from: pyVC.Disks.Base
"""
__revision__ = "$Revision: 263 $"

from pyVC.Disks import Base

class Disk( Base.Disk ):
    """
    This object defines a Disk object for a disk image.
    
    disk = Disk(realmachines, path)
    realmachines is a list of Machine objects where this Image is located
    path is the full or abbreviated path to the Image file. 
    """
    __revision__ = "$Revision: 263 $"
    
    def __init__(self, realmachines, path, **keywords):

        from pyVC.errors import DiskError

        Base.Disk.__init__(self, realmachines, path)
        
        for realmachine in realmachines:
            if not realmachine.isfile(self.path):
                if 'images_path' in realmachine.config['global'] and \
                   not realmachine.isfile(realmachine.config['global']['images_path'] + '/' + self.path):
                    raise DiskError, ( "Could not open disk image %s." % (self.path), \
                                       0, \
                                       realmachine.hostname \
                                     )

        self._keywords = keywords

    def __str__(self):
        return self._file

    def qemu(self, disks):
        return "-%s %s" % (disks.pop(0), self.path)

    def uml(self, disks):
        return "%s=%s" % (disks.pop(0), self.path)

    def xen(self, disks):
        from elementtree.ElementTree import Element, SubElement
        disk = Element('disk', type='file')
        SubElement(disk, 'source', file=str(self.path))
        SubElement(disk, 'target', dev=str(disks.pop(0)))
        
        return disk

    def __repr__(self):
        return "Disk(%s, file = \"%s\")" % (self.__realmachines, self.path)
