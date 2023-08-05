##
# Module containing the Helper object for a network interface.
##

__revision__ = "$Revision: 275 $"

from pyVC.Helpers import Base

##
# This class defines a Helper object for a network interface.
#
# @param realmachine The Machine object where this Helper should be started.
# @param networks A list of Network objects where this Helper should run.
# @param addrs A string containing a comma-separated list of addresses to assign to the network interface.
class Helper( Base.Helper ):

    __revision__ = "$Revision: 275 $"

    ##
    # A tuple containing the critical error conditions for an Interface Helper.
    errors = ( 'nosudo', \
               'no_ifconfig_executable' )

    ##
    # A tuple containing the supported platforms for an Interface Helper.
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

    ##
    # Brings up the network interface.
    # If multiple IP addresses are present in addrs, interface aliases will be created for each subsequent IP beyond the first.
    def start(self):
        
        from atexit import register
        from pyVC.Helpers.Tools import AliasGenerator, cidr2mask

        for network in self._networks:

            alias_generator = AliasGenerator()
            self._interfaces[network.lanname] = []

            mask = ""
            if network.subnet:
                mask = cidr2mask(network.subnet.split('/')[1])
            else:
                mask = "255.255.255.0"

            for addr in self._addrs:

                alias_suffix = alias_generator.next()
                while network.interface(self.realmachine) + alias_suffix in self.realmachine.used_interfaces + \
                                                                            self.realmachine.pyvc_interfaces:
                    alias_suffix = alias_generator.next()
                ifname = network.interface(self.realmachine) + alias_suffix

                pid = self.realmachine.popen( "%s %s %s %s netmask %s" % \
                                              ( self.realmachine.sudo, \
                                                self.realmachine.config['global']['ifconfig_executable'], \
                                                ifname, \
                                                addr, \
                                                mask ) )
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
        
    ##
    # Brings down the network interface.
    def stop(self):
        
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

    ##
    # A string containing a comma-separated list of IP addresses assigned to the network interface.
    addrs = property(_get_addrs)
