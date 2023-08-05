"""
Module containing the object for the Multicast virtual network.
"""
__revision__ = "$Revision: 216 $"

from pyVC.Networks import Base

class Network( Base.Network ):
    """
    This object defines a Multicast Network.

    >>> multicast = Network(address="230.0.0.1", port=1102)
    """
    __revision__ = "$Revision: 216 $"

    errors = ( )

    platforms = ( )

    def __init__ ( self, realmachines, lanname, \
                   address = "230.0.0.1", \
                   port = 1102, **keywords ):

        Base.Network.__init__( self, realmachines, lanname, **keywords )

        self.status = None

        self.__address = address
        self.__port = port

    def start(self):
        """
        Starts the Multicast virtual network.

        No initialization is needed for a Multicast network, so this method is a no-op.
        >>> multicast.start()
        """
        pass

    def stop(self):
        """
        Stops the Multicast virtual network.

        No descruction is needed for a Multicast network, so this method is a no-op.
        >>> multicast.stop()
        """
        pass


    def _get_address(self):
        """
        Returns the value of the multicast address associated with the Multicast network.

        >>> self._get_address()
        """
        return self.__address

    def _get_port(self):
        """Returns the value of self.__port"""
        return self.__port

    def __repr__(self):
        return "Multicast(\"%s\", %s, subnet=\"%s\", dns_servers=%s, address=\"%s\", port=\"%s\")" % \
                ( self.lanname, 
                  self.realmachine, 
                  self.subnet,
                  self.dns_servers,
                  self.address,
                  self.port) 

    def qemu(self, host):

        multicast_command = ""
        
        if host.macaddrs:
            mac = host.macaddrs.pop(0)
            mac_command = ",macaddr=%s" % (mac)
            host.macaddrs.append(mac)
        else:
            mac_command = ""
        if self.realmachine.qemu_version in ["0.8.0", "0.8.1", "0.8.2"]:
            multicast_command = "-net nic%s -net socket,mcast=%s:%s" % (mac_command, self.address, self.port)
            return ("", multicast_command)
        else:
            raise ValueError, \
                  "ERROR: Unhandled network type for QEMU version %s" % \
                  (self.realmachine.qemu_version)

    def uml(self, host):

        multicast_command = ""

        mac = host.macaddrs.pop(0)
        multicast_command = "%s=mcast,%s,%s,%s" % (host.interfaces.pop(0), mac, self.address, self.port)
        host.macaddrs.append(mac)

        return (None, multicast_command)

    def xen(self, host):
        raise NotImplementedError

    address = property(_get_address)
    port = property(_get_port)
