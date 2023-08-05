"""Module containing the Disk object for an NFS share.
Inherits from: pyVC.Disks.Base"""
__revision__ = "$Revision: 216 $"

from pyVC.Disks import Base

class Disk ( Base.Disk ):
    """This object defines a Disk object for an NFS share.
    
    disk = Disk(server = "hostname", path = "/path", options = "options")"""
    __revision__ = "$Revision: 216 $"
    
    def __init__(self, server, path, options, **keywords):

        self._server = server
        self._path = path
        self._options = options

    def __str__(self):
        return "%s:%s (%s)" % (server, path, options)

    def __repr__(self):
        return "Disk(server = \"%s\", path = \"%s\", options = \"%s\")" % \
                ( self._server, \
                  self._path, \
                  self._options )
