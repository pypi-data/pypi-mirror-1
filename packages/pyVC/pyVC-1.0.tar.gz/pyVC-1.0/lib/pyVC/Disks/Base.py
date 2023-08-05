"""
Module containing the base object for a Disk.
"""
__revision__ = "$Revision$"

class Disk:
    """
    This object defines a Disk object for a disk image.
    
    >>> disk = Disk(realmachines)
    realmachines is a list of Machine objects where this disk is valid.
    """
    __revision__ = "$Revision$"
    
    def __init__(self, realmachines, imagefile = "", **keywords):

        self.__realmachines = realmachines
