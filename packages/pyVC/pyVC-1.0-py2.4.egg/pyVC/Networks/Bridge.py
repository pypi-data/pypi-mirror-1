"""
Package containing the object for the Bridge virtual network"""
__revision__ = "$Revision$"

from pyVC.Networks import TAP

class Network( Base.TAP ):
    """This object defines a Bridge Network"""
    __revision__ = "$Revision$"

    errors = ( 'notunmod', \
               'notundev', \
               'notunwr' )

    platforms = ( )

    dhcp_capable = 1

    def __init__ ( self, realmachines, lanname, **keywords ):

        Base.Network.__init__( self, realmachines, lanname, **keywords )

    def start(self):
        """Starts the Bridge virtual network"""

    def stop(self):
        """Stops the Bridge virtual network"""

    def __repr__(self):
        return "Bridge(\"%s\", %s, subnet=\"%s\", dns_servers=\"%s\")" % \
                ( self.lanname, 
                  self.realmachine, 
                  self.dns_servers)

    def qemu(self, host):

        tap_command = ""
        
        if host.macaddrs:
            mac = host.macaddrs.pop(0)
            mac_command = ",macaddr=%s" % (mac)
            host.macaddrs.append(mac)
        else:
            mac_command = ""
        if self.realmachine.qemu_version in ["0.8.0", "0.8.1", "0.8.2"]:
            iface = host.realmachine.tap()
            tap_command = "-net nic%s -net tap,ifname=%s,script=/bin/true" % (mac_command, iface)
            return ("", tap_command)
        else:
            raise ValueError, \
                  "ERROR: Unhandled network type for QEMU version %s" % \
                  (self.realmachine.qemu_version)

    def uml(self, host):


        tap_command = ""

        iface = host.realmachine.tap()
        tap_command = "%s=tuntap,%s,,%s" % (host.interfaces.pop(0), host.macaddrs.pop(0), iface)

        return (None, tap_command)

    def xen(self, host):
        raise NotImplementedError
