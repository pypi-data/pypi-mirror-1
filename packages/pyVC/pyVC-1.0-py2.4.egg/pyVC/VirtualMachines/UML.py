"""This package contains the classes to implement a UML VM"""
__revision__ = "$Revision: 219 $"

from pyVC.VirtualMachines import Base

class VM( Base.VM ):
    """This object defines a UML Virtual Machine"""
    __revision__ = "$Revision: 219 $"

    from pyVC.Networks.Tools import MacGenerator

    macs = MacGenerator('FE:FD:00')

    errors = ( )

    platforms = ( 'Linux' )
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  kernel = "", \
                  kernelargs = "", \
                  initrd = "", \
                  **keywords ):

        Base.VM.__init__( self, \
                          realmachine, \
                          name, \
                          **keywords )

        self.__kernel = kernel
        self.__initrd = initrd
        self.__kernelargs = kernelargs
        self.__pid = None
        self.__interfaces = ["eth%s" % ifid for ifid in range(0, 10)]
        
        if len(self.disks) > 8:
            raise ValueError, \
                  "Error: Too many disks for UML VM, \
                  UML can only access 8 disk images concurrently."

    # Accessors
    
    def _get_kernel(self):
        """Gets the value of self.__kernel"""
        return self.__kernel
    
    def _get_kernelargs(self):
        """Gets the value of self.__kernelargs"""
        return self.__kernelargs
    
    def _get_initrd(self):
        """Gets the value of self.__initrd"""
        return self.__initrd

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
            disk_command += "%s=%s " % (available_disks.pop(0), disk)
            
        # set kernel parameters
        if self.kernel:
            from os.path import isfile

            if not isfile(self.kernel):
                if 'kernels_path' in self.realmachine.config['global'] and \
                   isfile(self.realmachine.config['global']['kernels_path'] + '/' + self.kernel):
                    self.__kernel = self.realmachine.config['global']['kernels_path'] + '/' + self.kernel
                else:
                    raise IOError, "ERROR: Could not open kernel %s" % (self.kernel)

            if self.initrd:
                kernel_command += " initrd=%s" % (self.initrd)
            if self.kernelargs:
                kernel_command += " %s" % (self.kernelargs)

        # network commands
        # pre_vde_network_command is used to invoke vdeq before QEMU
        network_command = ""

        for network in self.networks:
            (tmp_pre_command, interface_command) = network.uml(self)
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

    kernel = property(_get_kernel)
    kernelargs = property(_get_kernelargs)
    initrd = property(_get_initrd)
    interfaces = property(_get_interfaces)
