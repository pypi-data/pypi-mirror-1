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
    
    def __init__(self, realmachines, path, **keywords):

        self.__realmachines = realmachines
        self.__path = path

    def _get_path(self):
        """Returns the path associated with a virtual disk."""

        return self.__path

    path = property(_get_path)
