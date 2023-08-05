"""
Package containing the object for the Bridge virtual network"""
__revision__ = "$Revision$"

from pyVC.Networks import Base

class Network( Base.Network ):
    """This object defines a Bridge Network"""
    __revision__ = "$Revision$"

    errors = ( 'notunmod', \
               'notundev', \
               'notunwr', \
               'no_ifconfig_executable' )

    platforms = ( )

    max_realmachines = 1

    def __init__ ( self, realmachines, lanname, devices, **keywords ):

        Base.Network.__init__( self, realmachines, lanname, **keywords )

        self.__interface = None
        self.__devices = devices.split(',')

    def _get_devices(self):
        """
        Returns the device associated with the bridge.
        """

        return self.__devices

    def start(self):
        """Starts the Bridge virtual network"""

        from atexit import register

        for realmachine in self.realmachines:
            self.__interface = realmachine.bridge()
            realmachine.wait(realmachine.popen("%s addbr %s" % (realmachine.config['bridge']['brctl_executable'], self.__interface)))
            realmachine.wait(realmachine.popen("%s stp %s off" % (realmachine.config['bridge']['brctl_executable'], self.__interface)))
            realmachine.wait(realmachine.popen("%s setfd %s 0" % (realmachine.config['bridge']['brctl_executable'], self.__interface)))
            for device in self.devices:
                realmachine.wait(realmachine.popen("%s addif %s %s" % (realmachine.config['bridge']['brctl_executable'], self.__interface, device)))
                realmachine.wait(realmachine.popen("%s %s 0.0.0.0 up" % (realmachine.config['global']['ifconfig_executable'], device)))

        self.add_interface(realmachine, self.__interface, 0 )

        self.status = "started"

        register(self.stop)

    def stop(self):
        """Stops the Bridge virtual network"""

        for realmachine in self.realmachines:

            for device in self.devices:
                realmachine.wait(realmachine.popen("%s delif %s %s" % (realmachine.config['bridge']['brctl_executable'], self.__interface, device)))
            realmachine.wait(realmachine.popen("%s delbr %s" % (realmachine.config['bridge']['brctl_executable'], self.__interface)))

            try:
                self.del_interface(realmachine)
            except KeyError:
                pass

            realmachine.bridge(self.__interface)

        self.status = "stopped"

    def __repr__(self):
        return "Bridge(\"%s\", subnet=\"%s\", dns_servers=\"%s\")" % \
                ( self.lanname, 
                  self.realmachine, 
                  self.dns_servers)

    def qemu(self, host):

        from pyVC.errors import NetworkError

        tap_device = host.realmachine.tap()
        self.add_interface(host, tap_device, 0)

        post_command = "%s addif %s %s" % (host.realmachine.config['bridge']['brctl_executable'], self.__interface, tap_device)

        tap_command = ""
        
        if host.macaddrs:
            mac = host.macaddrs.pop(0)
            mac_command = ",macaddr=%s" % (mac)
            host.macaddrs.append(mac)
        else:
            mac_command = ""
        if self.realmachine.qemu_version in ["0.8.0", "0.8.1", "0.8.2"]:
            tap_command = "-net nic%s -net tap,ifname=%s,script=/bin/true" % (mac_command, tap_device)
            return ("", tap_command, post_command)
        else:
            raise NetworkError, \
                  ( "ERROR: Unhandled Network type for QEMU version %s." % \
                    (self.realmachine.qemu_version), \
                    2, \
                    self.realmachine.hostname, \
                    self.lanname \
                  )

    def uml(self, host):

        tap_device = host.realmachine.tap()
        self.add_interface(host, tap_device, 0)

        post_command = "%s addif %s %s" % (host.realmachine.config['bridge']['brctl_executable'], self.__interface, tap_device)

        tap_command = ""

        mac = host.macaddrs.pop(0)
        tap_command = "%s=tuntap,%s,,%s" % (host.interfaces.pop(0), mac, self.tap_device)
        host.macaddrs.append(mac)

        return ("", tap_command, post_command)

    def xen(self, host):
        from elementtree.ElementTree import Element, SubElement
        interface = Element('interface', type='bridge')
        SubElement(interface, 'source', dev=str(self.__interface))
        if host.macaddrs:
            mac = host.macaddrs.pop(0)
            SubElement(interface, 'mac', address=str(mac))
            host.macaddrs.append(mac)

        return interface

    devices = property(_get_devices)
