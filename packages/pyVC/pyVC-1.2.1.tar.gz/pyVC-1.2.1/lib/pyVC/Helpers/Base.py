"""
Package containing the base object for a Helper.

This package contains a single object, Helper, which all other Helper objects derive from.
In this module, Helper should not be instantiated, and the non-shared methods will raise
NotImplementedError when executed. 

Each Helper contains 2 class tuples, errors and platforms.
errors defines the list of errors that cause this Helper to fail.
platforms lists the OS platforms that this Helper is functional on, as defined by uname(1).
"""

__revision__ = "$Revision: 216 $"

class Helper(object):
    """
    This object defines the base class for a Helper object.
    """
    __revision__ = "$Revision: 216 $"

    errors = ()
    
    platforms = ()
    
    def __init__(self, realmachine, networks):
        self._status = "stopped"
        self._realmachine = realmachine
        self._networks = networks

        realmachine.check_errors(self.errors)
        realmachine.check_platform(self.platforms)

        for network in networks:
            network.add_helper(self)

    def __del__(self):
        self.stop()

    def _get_status(self):
        """
        Returns the status of a Helper object.
        """ 
        
        return self._status

    def _set_status(self, status = ""):
        """
        Sets the status of a Helper object with the value in status.

        status should be one of ('stopped', 'started').
        """

        if status == 'stopped' or \
           status == 'started' or \
           status == None:
            self._status = status

    def _get_realmachine(self):
        """
        Returns the real Machine object associated with this Helper.
        """

        return self._realmachine

    def _get_networks(self):
        """
        Returns a list of Network objects associated with this Helper.
        """

        return self._networks

    # Properties

    status = property(_get_status, _set_status)
    realmachine = property(_get_realmachine)
    networks = property(_get_networks)

    # Abstract methods
    
    def start(self):
        """
        Abstract method to start the Helper object.
        """
        
        raise NotImplementedError
        
    def stop(self):
        """
        Abstract method to stop the Helper opject.
        """
        
        raise NotImplementedError
