"""Module containing the Disk object for a Disk Image.
Inherits from: pyVC.Disks.Base"""
__revision__ = "$Revision: 218 $"

from pyVC.Disks import Base

class Disk( Base.Disk ):
    """This object defines a Disk object for a physical disk device.
    
    disk = Disk(device = "/dev/hdc1")"""
    __revision__ = "$Revision: 218 $"
    
    def __init__(self, device = "", **keywords):

        self._device = device
        self._keywords = keywords

    def __str__(self):
        return self._device

    def __repr__(self):
        return "Disk(device = \"%s\")" % (self._device)
