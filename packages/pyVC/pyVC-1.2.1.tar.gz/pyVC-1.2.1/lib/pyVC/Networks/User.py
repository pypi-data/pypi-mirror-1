"""
Package containing the object for the User-mode virtual network.
"""
__revision__ = "$Revision$"

from pyVC.Networks import Base

class Network( Base.Network ):
    """This object defines a User-mode Network"""
    __revision__ = "$Revision$"

    errors = ( )

    platforms = ( )

    def __init__ ( self, realmachines, lanname, **keywords ):

        Base.Network.__init__( self, realmachines, lanname, **keywords )
        self.status = None

    def start(self):
        """Starts the User-mode virtual network"""
        pass

    def stop(self):
        """Stops the User-mode virtual network"""
        pass

    def __repr__(self):
        return "User(\"%s\", %s, subnet=\"%s\", dns_servers=\"%s\")" % \
                ( self.lanname, 
                  self.realmachine, \
                  self.dns_servers )

    def qemu(self, host):

        from pyVC.errors import NetworkError

        user_command = ""
        
        if host.macaddrs:
            mac = host.macaddrs.pop(0)
            mac_command = ",macaddr=%s" % (mac)
            host.macaddrs.append(mac)
        else:
            mac_command = ""

        if self.realmachine.qemu_version in ["0.8.0", "0.8.1", "0.8.2"]:
            user_command = "-net nic%s -net user,hostname=%s" % (mac_command, host.vmname)
            return ("", user_command, "")
        elif self.realmachine.qemu_version in ["0.7.0", "0.7.1", "0.7.2"]:
            user_command = "-user-net"
            return ("", user_command, "")
        else:
            raise NetworkError, \
                  ( "ERROR: Unhandled Network type for QEMU version %s." % \
                    (self.realmachine.qemu_version), \
                    2, \
                    self.realmachine.hostname, \
                    self.lanname \
                  )

    def uml(self, host):
        raise NotImplementedError

    def xen(self, host):
        from elementtree.ElementTree import Element, SubElement
        interface = Element('interface', type='user')
        if host.macaddrs:
            mac = host.macaddrs.pop(0)
            SubElement(interface, 'mac', address=str(mac))
            host.macaddrs.append(mac)

        return interface
