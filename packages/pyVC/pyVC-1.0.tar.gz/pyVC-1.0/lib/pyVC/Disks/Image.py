"""
Module containing the Disk object for a Disk Image.
Inherits from: pyVC.Disks.Base
"""
__revision__ = "$Revision: 218 $"

from pyVC.Disks import Base

class Disk( Base.Disk ):
    """
    This object defines a Disk object for a disk image.
    
    disk = Disk(realmachines, imagefile)
    realmachines is a list of Machine objects where this Image is located
    imagefile is the full or abbreviated path to the Image file. 
    """
    __revision__ = "$Revision: 218 $"
    
    def __init__(self, realmachines, imagefile = "", **keywords):

        Base.Disk.__init__(self, realmachines)
        
        for realmachine in realmachines:
            if not realmachine.isfile(imagefile):
                if 'images_path' in realmachine.config['global'] and \
                   realmachine.isfile(realmachine.config['global']['images_path'] + '/' + imagefile):
                    self._file = realmachine.config['global']['images_path'] + '/' + imagefile
                else:
                    raise IOError, "Could not opendisk image %s" % (imagefile)
            else:
                self._file = imagefile

        self._keywords = keywords

    def __str__(self):
        return self._file

    def __repr__(self):
        return "Disk(%s, imagefile = \"%s\")" % (self.__realmachines, self._file)
