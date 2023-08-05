##
# Module containing the Disk object for a Disk Image.
##

__revision__ = "$Revision: 296 $"

from pyVC.Disks import Base

##
# This class defines a Disk object for a disk image.
#
# @realmachines A list of Machine objects this disk should exist on.
# @param path The path to the disk image.
class Disk( Base.Disk ):

    __revision__ = "$Revision: 296 $"
    
    def __init__(self, realmachines, path, **keywords):

        from pyVC.errors import DiskError

        Base.Disk.__init__(self, realmachines, path, **keywords)
        
        for realmachine in realmachines:
            if not realmachine.isfile(self.path):
                if 'images_path' in realmachine.config['global'] and \
                   not realmachine.isfile(realmachine.config['global']['images_path'] + '/' + self.path):
                    raise DiskError, ( "Could not open disk image %s." % (self.path), \
                                       0, \
                                       realmachine.hostname \
                                     )

    def __str__(self):
        return self._file

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
        disk = Element('disk', type='file')
        SubElement(disk, 'source', file=str(self.path))
        SubElement(disk, 'target', dev=str(disks.pop(0)))
        
        return disk

    def __repr__(self):
        return "Disk(%s, file = \"%s\")" % (self.__realmachines, self.path)
