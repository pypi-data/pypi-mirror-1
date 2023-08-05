"""
Module containing the Helper object for a DHCP Helper.

This package contains a single object, Helper. It implements the methods to control 
and configure a DHCP server process on a real Machine.
"""
__revision__ = "$Revision: 227 $"

from pyVC.Helpers import Base

class Helper( Base.Helper ):
    """
    This object defines a Helper object for a DHCP Server.

    This object can be instantiated as:
        dhcp = Helper(realmachine, networks)
        realmachine = Machine
        networks = [Network, ...]

    Derives from: pyVC.Helpers.Base
    """
    __revision__ = "$Revision: 227 $"

    errors = ( 'nosudo', \
               'no_dhcpd_executable' )

    platforms = ( )
    
    def __init__(self, realmachine, networks, **keywords):

        Base.Helper.__init__(self, realmachine, networks, **keywords)

        self.__fd = None
        self.__pid = None

    def start(self):
        """
        Starts the DHCP Server process on the real Machine.
        
        This method will perform a no-op if the server is already started or if self._pid is already defined. 
        
        This method also registers self.stop() as an atexit function, to ensure proper cleanup of processes and files.
        
        >>> dhcp.start()
        """
        
        from atexit import register
        from tempfile import NamedTemporaryFile

        if not self.__pid:
            interfaces = [network.interface(self.realmachine) for network in self.networks]

            self.__fd = NamedTemporaryFile()

            self.create_dhcpd_conf(self.__fd)

            print('%s %s -q -f -cf %s %s' % \
                                          (self.realmachine.sudo, \
                                           self.realmachine.config['global']['dhcpd_executable'], \
                                           self.__fd.name, " ".join(interfaces)\
                                          ) )
            self.__pid = self.realmachine.popen('%s %s -q -f -cf %s %s' % \
                                          (self.realmachine.sudo, \
                                           self.realmachine.config['global']['dhcpd_executable'], \
                                           self.__fd.name, " ".join(interfaces)\
                                          ) )
            self.status = "started"

            register(self.stop)
        
    def stop(self):
        """
        Stops the DHCP Server process on the real Machine.
        
        This method will perform a no-op if the server is not started or if self._pid is not defined.
        
        >>> dhcp.stop()
        """

        if self.__pid:
            pid = self.realmachine.popen('%s kill %s' % (self.realmachine.sudo, self.__pid))
            self.realmachine.wait(pid)
            self.realmachine.wait(self.__pid)
            
            self.status = "stopped"
            self.__pid = None
        
    def create_dhcpd_conf( self, dhcpfile ):
        """
        Creates dhcpd.conf files for the DHCP Server Helper object.
        
        dhcp.create_dhcpd_conf(dhcpfile)
        dhcpfile should be an open and writable file-like object.

        >>> dhcp.create_dhcpd_conf(file)
        """

        from pyVC.Helpers import Router
        from pyVC.Helpers import Interface

        def cidr2mask( cidr ):
            """
            Converts a CIDR subnet (/24) to a mask (255.255.255.0).
            """
            one32 = 0xffffffffL
            if ( cidr == "0" ):
                return "0.0.0.0"
            bits = int( cidr )
            n = ( ( one32 << ( 32 - bits ) ) & one32 )
            d3 = "%u" % ( n % 256 )
            n = int( n / 256 )
            d2 = "%u" % ( n % 256 )
            n = int( n / 256 )
            d1 = "%u" % ( n % 256 )
            n = int( n / 256 )
            d0 = "%u" % n
            return "%s.%s.%s.%s" % ( d0, d1, d2, d3 )

        
        for network in self.networks:        
            if network.subnet:
                ( networkaddress, cidrmask ) = network.subnet.split( '/' )
                netmask = cidr2mask( cidrmask )
                dhcpfile.write( "subnet %s netmask %s {\n" % \
                                ( networkaddress, \
                                  netmask ) \
                              )

            if network.dns_servers:
                dhcpfile.write( "  option domain-name-servers %s;\n" % \
                                network.dns_servers )

            for helper in network.helpers:
                if isinstance( helper, Router.Helper ):
                    router = helper
                    for helper in network.helpers:
                        if isinstance( helper, Interface.Helper ) and helper.realmachine == router.realmachine:
                            dhcpfile.write( "  option routers %s;\n" % (','.join(helper.addrs)) )

            dhcpfile.write( "  use-host-decl-names on;\n" )
        
            for vm in network.vms:
                dhcpfile.write( "  host %s {\n" % vm )
                if vm.macaddr:
                    dhcpfile.write( "   hardware ethernet %s;\n" % \
                                    vm.macaddrs[vm.networks.index(network)] )
                dhcpfile.write( "   fixed-address %s;\n" % \
                                network.ips(vm)[0] )
                dhcpfile.write( "   option host-name \"%s\";\n" % \
                                vm )
                dhcpfile.write( "  }\n" )
                            
            dhcpfile.write( "}\n" )

        dhcpfile.flush()

    def __repr__(self):
        return "DHCP(%s, %s)" % (self.realmachine, self.networks)
    
    def __str__(self):
        return "DHCP Server on %s" % (self.realmachine.used_interfaces)
