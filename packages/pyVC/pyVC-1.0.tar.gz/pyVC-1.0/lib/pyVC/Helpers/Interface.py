"""
Package containing the object for an Interface Helper.

This package contains a single object, Helper. It implements the methods to control
and configure a network interface on a real Machine.
"""
__revision__ = "$Revision: 216 $"

from pyVC.Helpers import Base

class Helper( Base.Helper ):
    """
    This object defines a Interface to run on the 'real' machine

    This object can be instantiated as:
        interface = Helper(realmachine, networks, addrs)
        realmachine = Machine
        networks = [Network, ...]
        addrs is a comma separated string of IP addresses
    
    Derives from: pyVC.Helpers.Base
    """
    __revision__ = "$Revision: 216 $"

    errors = ( 'nosudo', \
               'no_ifconfig_executable' )

    platforms = ( )
    
    def __init__(self, realmachine, networks, addrs, **keywords):

        Base.Helper.__init__(self, realmachine, networks, **keywords)

        self._addrs = addrs.split(',')
        self._interfaces = {}

    def _get_addrs(self):
        """
        Returns a list of IP addresses to be assigned to the network interface.
        """

        return self._addrs

    def start(self):
        """
        Brings up the network interface on the real Machine.
        
        If multiple addresses are supplied to the constructor, this function will create Linux IP aliases 
        starting with :0, skipping any used interfaces.
        
        This method also registers self.stop() as an atexit function, to ensure proper cleanup of processes and files
        
        interface.start()
        """
        
        from atexit import register
        from pyVC.Helpers.Tools import AliasGenerator

        for network in self._networks:

            alias_generator = AliasGenerator()
            self._interfaces[network.lanname] = []

            for addr in self._addrs:

                alias_suffix = alias_generator.next()
                while network.interface(self.realmachine) + alias_suffix in self.realmachine.used_interfaces + \
                                                                            self.realmachine.pyvc_interfaces:
                    alias_suffix = alias_generator.next()
                ifname = network.interface(self.realmachine) + alias_suffix

                pid = self.realmachine.popen( "%s %s %s %s" % \
                                              ( self.realmachine.sudo, \
                                                self.realmachine.config['global']['ifconfig_executable'], \
                                                ifname, \
                                                addr ) )
                self.realmachine.wait(pid)

                pid = self.realmachine.popen( "%s %s %s up" % \
                                              ( self.realmachine.sudo, \
                                                self.realmachine.config['global']['ifconfig_executable'], \
                                                network.interface(self.realmachine) ) )
                self.realmachine.wait(pid)

                self.realmachine.add_interface(ifname)
                self._interfaces[network.lanname].append(ifname)
        
        self.status = "started"

        register(self.stop)
        
    def stop(self):
        """
        Brings down the network interface on the real Machine.
        
        This method will perform a no-op if the interface is already down or if self.status != 'started'.
        
        interface.stop()
        """
        
        if self.status == "started":
            for network in self._networks:
                for ifname in self._interfaces[network.lanname]:
                    pid = self.realmachine.popen( "%s %s %s down" % \
                           ( self.realmachine.sudo, \
                             self.realmachine.config['global']['ifconfig_executable'], \
                             ifname ) )
                    self.realmachine.wait(pid)
        
            self.status = "stopped"
        
    def __repr__(self):
        return "Interface(%s, %s, %s)" % (self.realmachine, self.networks, self._addrs)
    
    def __str__(self):
        return "Interface %s on %s" % (self._addrs, self._iface)

    # Properties

    addrs = property(_get_addrs)
