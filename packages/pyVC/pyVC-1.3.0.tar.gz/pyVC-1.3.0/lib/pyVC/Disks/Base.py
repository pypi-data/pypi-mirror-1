##
# Module containing the base object for a Disk.
##
__revision__ = "$Revision$"

##
# This class defines the base object for a Disk.
#
# @realmachines A list of Machine objects this disk should exist on.
# @param path The path to the disk.
class Disk:

    __revision__ = "$Revision$"
    
    def __init__(self, realmachines, path, **keywords):

        self.__realmachines = realmachines
        self.__path = path

    def _get_path(self):

        return self.__path

    ##
    # The path to the disk.
    path = property(_get_path)
