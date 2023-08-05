"""
Package containing the Helper object for an IP router.

This package contains a single object, Helper. It implements the methods to control 
and configure an IP router on a real Machine.

This Helper is currently only compatible with Linux hosts, because we don't know 
how to enable IP forwarding or do NAT on other OSs. 
"""
__revision__ = "$Revision: 227 $"

from pyVC.Helpers import Base

class Helper( Base.Helper ):
    """
    This object defines a Helper object for an IP router

    This object can be instantiated as:
        router = Helper(realmachine, networks, subnet = "192.168.1.0/24")
        realmachine = Machine
        networks = [Network, ...]
        subnet is a CIDR format subnet, in the form xxx.xxx.xxx.xxx/xx. 

    Derives from: pyVC.Helpers.Base
    """
    __revision__ = "$Revision: 227 $"
    
    init = {}

    errors = ( 'nosudo', \
               'no_iptables_executable' )

    platforms = ( 'Linux' )
    
    def __init__(self, realmachine, networks, subnet = None, **keywords):

        Base.Helper.__init__(self, realmachine, networks, **keywords)

        self._subnet = subnet

    def start(self):
        """
        Starts the IP Router on the real Machine.

        This method uses a shared class dictionary, named init, to ensure that enabling IP forwarding 
        is only performed once on a real Machine. 

        This method also registers self.stop() as an atexit function, to ensure proper cleanup of processes and files.

        router.start()
        """
        
        from atexit import register
        from pyVC.Machine import MachineError

        if not True in self.init:
            pid = self.realmachine.popen( "%s %s -t nat -F" % \
                   ( self.realmachine.sudo, \
                     self.realmachine.config['global']['iptables_executable'] ) )
            self.realmachine.wait(pid)
            if self.realmachine.platform == 'Linux':
                pid = self.realmachine.popen( '%s sh -c \\\"echo 1 > /proc/sys/net/ipv4/ip_forward\\\"' % \
                                              self.realmachine.sudo )
                self.realmachine.wait(pid)
            else:
                raise MachineError, ( 'ERROR: cannot enable routing on architecture %s' % \
                                      (self.realmachine.platform),
                                      'norouting',
                                      self.realmachine ) 
            self.init[True] = None
            
        if self._subnet:
            pid = self.realmachine.popen( "%s %s -t nat -A POSTROUTING -s %s -j MASQUERADE" % \
                   ( self.realmachine.sudo, \
                     self.realmachine.config['global']['iptables_executable'], \
                     self._subnet ) \
                   )
            self.realmachine.wait(pid)
        
            self.status = "started"

        else:
            self.status = "error"

        register(self.stop)
        
    def stop(self):
        """
        Stops the IP router on the real Machine.

        This will only disable the NAT rules and not disable IP forwarding.

        router.stop()
        """
        
        pid = self.realmachine.popen( "%s %s -t nat -F" % \
                  ( self.realmachine.sudo , \
                    self.realmachine.config['global']['iptables_executable'] ) \
                  )
        self.realmachine.wait(pid)
                                      
        self.status = "stopped"

    def __repr__(self):
        return "Router(%s, %s, %s)" % (self.realmachine, self.networks, self._subnet)
        
    def __str__(self):
        return "Router for %s" % (self._subnet)
