"""
Package containing the object for the TAP virtual network"""
__revision__ = "$Revision$"

from pyVC.Networks import Base

class Network( Base.Network ):
    """This object defines a TAP Network"""
    __revision__ = "$Revision$"

    errors = ( 'notunmod', \
               'notundev', \
               'notunwr', \
               'no_ifconfig_executable' )

    platforms = ( )

    max_vms = 1

    max_realmachines = 1

    def __init__ ( self, realmachines, lanname, **keywords ):

        Base.Network.__init__( self, realmachines, lanname, **keywords )

        self.__interface = None


    def start(self):
        """Starts the TAP virtual network"""

        from atexit import register

        for realmachine in self.realmachines:
            self.__interface = realmachine.tap()

        self.add_interface(realmachine, self.__interface, 0 )

        self.status = "started"

        register(self.stop)

    def stop(self):
        """Stops the TAP virtual network"""

        for realmachine in self.realmachines:
            try:
                self.del_interface(realmachine)
            except KeyError:
                pass
            except:
                raise

            realmachine.tap(self.__interface)

        self.status = "stopped"

    def __repr__(self):
        return "TAP(\"%s\", subnet=\"%s\", dns_servers=\"%s\")" % \
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
            tap_command = "-net nic%s -net tap,ifname=%s,script=/bin/true" % (mac_command, self.__interface)
            return ("", tap_command)
        else:
            raise ValueError, \
                  "ERROR: Unhandled network type for QEMU version %s" % \
                  (self.realmachine.qemu_version)

    def uml(self, host):

        tap_command = ""

        mac = host.macaddrs.pop(0)
        tap_command = "%s=tuntap,%s,,%s" % (host.interfaces.pop(0), mac, self.__interface)
        host.macaddrs.append(mac)

        return ("", tap_command)

    def xen(self, host):
        raise NotImplementedError
