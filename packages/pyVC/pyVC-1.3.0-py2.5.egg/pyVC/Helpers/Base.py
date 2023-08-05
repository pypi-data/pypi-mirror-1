##
# Package containing the base object for a Helper.
##

__revision__ = "$Revision: 276 $"

##
# This class defines the base object for a Helper.
#
# @param realmachine The Machine object where this Helper should be started.
# @param networks A list of Network objects where this Helper should run.
class Helper(object):

    __revision__ = "$Revision: 276 $"

    ##
    # A tuple containing the critical error conditions for a Helper.
    errors = ()
    
    ##
    # A tuple containing the supported platforms for a Helper.
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
        
        return self._status

    def _set_status(self, status = ""):

        if status == 'stopped' or \
           status == 'started' or \
           status == None:
            self._status = status

    def _get_realmachine(self):

        return self._realmachine

    def _get_networks(self):

        return self._networks

    # Properties

    ##
    # A string containing the status of the Helper.
    status = property(_get_status, _set_status)

    ##
    # The Machine object where this Helper was started.
    realmachine = property(_get_realmachine)

    ##
    # A list of Network objects where this Helper runs.
    networks = property(_get_networks)

    # Abstract methods
    
    def start(self):
        
        raise NotImplementedError
        
    def stop(self):
        
        raise NotImplementedError
