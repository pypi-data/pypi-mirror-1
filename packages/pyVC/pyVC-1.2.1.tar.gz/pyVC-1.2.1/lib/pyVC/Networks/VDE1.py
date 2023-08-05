"""Package containing the object for the VDE1 virtual network"""
__revision__ = "$Revision: 263 $"

from pyVC.Networks import Base

class Network( Base.Network ):
    """This object defines a VDE Network"""
    __revision__ = "$Revision: 263 $"

    errors = ( 'no_vde_switch_executable', \
               'no_vdeq_executable' )

    platforms = ( 'Linux' )

    dhcp_capable = 1
    
    def __init__( self, realmachines, lanname, \
                  hub = False, **keywords ):

        Base.Network.__init__( self, realmachines, lanname, \
                         **keywords)

        self.__hub = hub

    def __str__(self):
        return self.lanname

    def _get_hub(self):
        """Gets the value of self.__hub"""
        return self.__hub

    def qemu(self, host):

        from pyVC.errors import NetworkError

        vde_command = ""
        pre_command = ""

        if host.realmachine.qemu_version in ["0.7.0", "0.7.1", "0.7.2"]:
            if host.macaddr:
                pre_command = "-macaddr %s" % (host.macaddr)
            else:
                pre_command = ""
            vde_command = "-sock /tmp/%s.sock" % (self.lanname)
            
        elif host.realmachine.qemu_version in ["0.8.0", "0.8.1", "0.8.2"]:
            if host.macaddrs:
                mac = host.macaddrs.pop(0)
                host.macaddrs.append(mac)
                vde_command = "-net nic,macaddr=%s -net vde,,sock=/tmp/%s.sock" % (mac, self.lanname)
            else:
                vde_command = "-net nic -net vde,,sock=/tmp/%s.sock" % (self.lanname)

        else:
            raise NetworkError, \
                  ( "ERROR: Unhandled Network type for QEMU version %s." % \
                    (self.realmachine.qemu_version), \
                    2, \
                    self.realmachine.hostname, \
                    self.lanname \
                  )

        return (pre_command, vde_command, "")

    def uml(self, host):

        vde_command = ""

        vde_command = "%s=daemon,%s,,/tmp/%s.sock" % (host.interfaces.pop(0), host.macaddrs.pop(0), self.lanname)

        return ("", vde_command, "")

    def xen(self, host):
        raise NotImplementedError

    def start(self):
        """Starts the VDE1 virtual network"""
        
        from atexit import register
        
        hub_command = ""
        tap_command = ""
        interface = None

        tun_errors = ( 'notunmod', \
                       'notundev', \
                       'notunwr' )
        
        if self.hub:
            hub_command = "-hub"

        for realmachine in self.realmachines:

            realmachine.check_errors(tun_errors)
            interface = realmachine.tap()
            tap_command = "-tap %s" % interface

            try:
                self.interface(realmachine)
            except KeyError:
                self.add_interface(realmachine, \
                                   interface, \
                                   realmachine.popen( "%s -sock /tmp/%s.sock %s %s" % \
                                                      ( realmachine.config['vde1']['vde_switch_executable'], \
                                                        self.lanname, tap_command, hub_command \
                                                      ) \
                                                    )
                                  )

        for realmachine in self.realmachines[1:]:
            print "cable from %s to %s on %s" % (self.realmachine.hostname, realmachine.hostname, self.lanname)
            if self.realmachine.hostname != realmachine.hostname:
                cable = Cable(self, self.realmachine, realmachine)
                self.__cables.append(cable)
                self.__cables.append(cable)
                cable.start()

        self.status = "started"

        register(self.stop)

    def stop(self):
        """Stops the VDE1 virtual network"""

        from signal import SIGTERM
        
        for (realmachine, info) in self.__switches.items():
            if info:
                realmachine.kill(info[0], SIGTERM)
                realmachine.wait(info[0])
                try:
                    self.del_interface(realmachine)
                except KeyError:
                    pass
            realmachine.tap(info[1])

        for cable in self.cables:
            cable.stop()

        self.status = "stopped"

    hub = property(_get_hub)

    def __repr__(self):
        return "Network(\"%s\", %s, subnet=\"%s\", dns_servers=\"%s\", hub=%s)" % (self.lanname, self.realmachines, self.subnet, self.dns_servers, self.hub)

class Cable( Base.Cable ):
    """This object defines a VDE1 Network Cable"""
    __revision__ = "$Revision: 263 $"
    
    def __init__ ( self, network, realmachine1, realmachine2 ):

        Base.Cable.__init__( self, network, realmachine1, realmachine2 )

        self.pid = None

    def start(self):
        """Starts the VDE1 virtual cable"""

        self.pid = self.realmachine1.popen( '%s %s /tmp/%s.sock = %s %s %s /tmp/%s.sock &' % \
               ( self.realmachine1.config['vde1']['dpipe_executable'], \
                 self.realmachine1.config['vde1']['vde_plug_executable'], \
                 self.network.lanname, \
                 self.realmachine1.config['vde1']['vde_rsh_executable'], \
                 self.realmachine2.hostname, \
                 self.realmachine2.config['vde1']['vde_plug_executable'], \
                 self.network.lanname ) \
               )

        self.status = "started"

    def stop(self):
        """Stops the VDE1 virtual cable"""

        from signal import SIGTERM
        
        if self.pid:
            print "killing %s" % (self.pid)
            self.realmachine1.kill(self.pid, SIGTERM)
            self.pid = None
            self.status = "stopped"
