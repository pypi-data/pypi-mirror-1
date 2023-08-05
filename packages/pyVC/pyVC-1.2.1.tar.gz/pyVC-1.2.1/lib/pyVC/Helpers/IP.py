"""Package containing the object for the IP helper"""
__revision__ = 0.1

from pyVC.Helpers import Base

class Helper( Base.Helper ):
    """This object defines a IP to run on the 'real' machine"""
    __revision__ = 0.1

    errors = ( 'nosudo', \
               'no_ifconfig_executable' )
    
    def __init__(self, realmachine, iface = None, addr = None, **keywords):

        Base.Helper.__init__(self, realmachine, **keywords)

        realmachine.test( Helper.errors )
        
        self.__addr = addr
        self.__iface = iface

    def __del__(self):
        self.stop()

    def _get_addr(self):
        """Returns self.__addr"""

        return self.__addr

    def _get_iface(self):
        """Returns self.__iface"""

        return self.__iface

    def start(self):
        """Starts the interface"""
        
        from atexit import register

        for network in self.__networks:
            pid = self.realmachine.popen( "%s %s %s %s" % \
                   ( self.realmachine.sudo, \
                     self.realmachine.config['global']['ifconfig_executable'], \
                     network.interface, \
                     self.__addr ) )
            self.realmachine.wait(pid)
        
        self.status = "started"

        register(self.stop)
        
    def stop(self):
        """Stops the interface"""
        
        if self.status == "started":
            for network in self.__networks:
                pid = self.realmachine.popen( "%s %s %s down" % \
                       ( self.realmachine.sudo, \
                         self.realmachine.config['global']['ifconfig_executable'], \
                         network.interface ) )
                self.realmachine.wait(pid)
        
            self.status = "stopped"
        
    def __repr__(self):
        return "IP(%s, %s, %s, %s)" % (self.realmachine, self.networks, self.__iface, self.__addr)
    
    def __str__(self):
        return "IP %s on %s" % (self.__addr, self.__iface)

    addr = property(_get_addr)
    iface = property(_get_iface)
