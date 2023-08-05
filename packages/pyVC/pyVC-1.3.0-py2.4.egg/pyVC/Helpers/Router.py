##
# Module containing the Helper object for a network router.
##

__revision__ = "$Revision: 277 $"

from pyVC.Helpers import Base

##
# This class defines a Helper object for a network router..
#
# @param realmachine The Machine object where this Helper should be started.
# @param networks A list of Network objects where this Helper should run.
# @keyparam subnet A string containing a CIDR-notation subnet for the network segment to route for.
class Helper( Base.Helper ):

    __revision__ = "$Revision: 277 $"
    
    init = {}

    ##
    # A tuple containing the critical error conditions for a Router Helper.
    errors = ( 'nosudo', \
               'no_iptables_executable' )

    ##
    # A tuple containing the supported platforms for a Router Helper.
    platforms = ( 'Linux' )
    
    def __init__(self, realmachine, networks, **keywords):

        Base.Helper.__init__(self, realmachine, networks, **keywords)

    ##
    # Starts the router.
    #
    # @exception Cannot enable routing.
    def start(self):
        
        from atexit import register
        from pyVC.errors import MachineError

        if True not in self.init:
            pid = self.realmachine.popen( "%s %s -t nat -F" % \
                   ( self.realmachine.sudo, \
                     self.realmachine.config['global']['iptables_executable'] ) )
            self.realmachine.wait(pid)
            if self.realmachine.platform == 'Linux':
                print( '%s sh -c \"echo 1 > /proc/sys/net/ipv4/ip_forward\"' % \
                       self.realmachine.sudo )
                pid = self.realmachine.popen( '%s sh -c \"echo 1 > /proc/sys/net/ipv4/ip_forward\"' % \
                                              self.realmachine.sudo )
                self.realmachine.wait(pid)
            else:
                raise MachineError, ( "ERROR: Cannot enable routing on architecture %s." % \
                                      (self.realmachine.platform),
                                      'norouting',
                                      self.realmachine.hostname ) 
            self.init[True] = None
            
        for network in self.networks:
            if network.subnet:
                print( "%s %s -t nat -A POSTROUTING -s %s -j MASQUERADE" % \
                       ( self.realmachine.sudo, \
                         self.realmachine.config['global']['iptables_executable'], \
                         network.subnet ) \
                       )
                pid = self.realmachine.popen( "%s %s -t nat -A POSTROUTING -s %s -j MASQUERADE" % \
                       ( self.realmachine.sudo, \
                         self.realmachine.config['global']['iptables_executable'], \
                         network.subnet ) \
                       )
                self.realmachine.wait(pid)
        
        self.status = "started"

        register(self.stop)
        
    ##
    # Stops the router.
    def stop(self):
        
        pid = self.realmachine.popen( "%s %s -t nat -F" % \
                  ( self.realmachine.sudo , \
                    self.realmachine.config['global']['iptables_executable'] ) \
                  )
        self.realmachine.wait(pid)
                                      
        self.status = "stopped"

    def _get_subnet(self):

        return self._subnet

    def __repr__(self):
        return "Router(%s, %s, %s)" % (self.realmachine, self.networks, self._subnet)
        
    def __str__(self):
        return "Router for %s" % (self._subnet)

    ##
    # A string containing a CIDR-notation subnet for the network segment to route for.
    subnet = property(_get_subnet)
