"""This package contains the classes to implement a UML VM"""
__revision__ = "$Revision: 263 $"

from pyVC.VirtualMachines import Base

class VM( Base.VM ):
    """This object defines a UML Virtual Machine"""
    __revision__ = "$Revision: 263 $"

    from pyVC.Networks.Tools import MacGenerator

    macs = MacGenerator('FE:FD:00')

    errors = ( )

    platforms = ( 'Linux' )
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  kernel = None, \
                  **keywords ):

        Base.VM.__init__( self, \
                          realmachine, \
                          name, \
                          kernel = kernel, \
                          **keywords )

        self.__pid = None
        self.__interfaces = ["eth%s" % ifid for ifid in range(0, 10)]
        
        if len(self.disks) > 8:
            raise VMError, \
                  ( "Error: Too many disks for UML VM, \
                    UML can only access 8 disk images concurrently.", \
                    3, \
                    self.realmachine.hostname, \
                    self.vmname \
                  )

        if not self.kernel:
            raise VMError, \
                  ( "Error: Kernel required for UML VM", \
                    4, \
                    self.realmachine.hostname, \
                    self.vmname \
                  )

    # Accessors
    
    def _get_interfaces(self):
        """
        Returns the available interfaces on the VM.
        """
        return self.__interfaces

    # Control
        
    def start( self ):
        """Starts a UML VM"""
        from atexit import register
        
        disk_command = ""
        network_command = ""
        kernel_command = ""
        
        # attach all requested disks
        available_disks = ["ubd%s" % (id) for id in range(0, 8)]
        for disk in self.disks[:7]:
            disk_command += disk.uml(available_disks)
            
        # set kernel parameters
        if self.kernel:

            if self.initrd:
                kernel_command += " initrd=%s" % (self.initrd)
            if self.kernelargs:
                kernel_command += " %s" % (self.kernelargs)
                if self.root:
                    kernel_command += "root=%s " % self.root

        # network commands
        # pre_vde_network_command is used to invoke vdeq before QEMU
        network_command = ""
        pre_command = ""
        post_command = ""

        for network in self.networks:
            (pre_command, interface_command, post_command) = network.uml(self)
            network_command += "%s " % (interface_command)

        if not self.__pid:
            
            print('%s %s %s mem=%sM umid=%s %s' % \
                                      (self.kernel, \
                                       kernel_command, \
                                       network_command, \
                                       self.memory, \
                                       self.vmname, \
                                       disk_command)
                                      )       

            self.__pid = self.realmachine.term('%s %s %s mem=%sM umid=%s %s' % \
                                      (self.kernel, \
                                       kernel_command, \
                                       network_command, \
                                       self.memory, \
                                       self.vmname, \
                                       disk_command)
                                      )       

            pid = self.realmachine.popen(post_command)
            self.realmachine.wait(pid)

            self.status = "started"

            register(self.stop)
    
    def stop(self):
        """Stops a UML VM"""

        from signal import SIGTERM
        
        if self.__pid:
            self.realmachine.kill(self.__pid, SIGTERM)
            self.realmachine.wait(self.__pid)
            self.__pid = None
            self.status = "stopped"

    def console(self, socket = False):
        """Provides a console for a VM"""

        if self.__pid:
            if socket:
                return (self.realmachine.hostname, self.realmachine.term_socket(self.__pid))
            else:
                self.realmachine.term_connect(self.__pid)

    def serve(self):
        """Starts the serving loop for the VM"""
        if self.__pid:
            self.realmachine.term_serve(self.__pid)

    def __str__( self ):
        return self.vmname

    def __repr__(self):
        return "VM(\"%s\", %s, addrs=\"%s\", macaddr=\"%s\", kernel=\"%s\", kernelargs=\"%s\", initrd=\"%s\", memory=%s, networks=%s, disks=%s, vmgroup=%s)" % \
                (self.vmname,
                 self.realmachine,
                 self.addrs,
                 self.macaddr,
                 self.kernel,
                 self.kernelargs,
                 self.initrd,
                 self.memory,
                 self.networks,
                 self.disks,
                 self.vmgroup)

    # Properties

    interfaces = property(_get_interfaces)
