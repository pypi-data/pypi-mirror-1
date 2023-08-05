"""This package contains the classes to implement a QEMU VM"""
__revision__ = "$Revision: 262 $"

from pyVC.VirtualMachines import Base

class VM( Base.VM ):
    """This object defines a QEMU Virtual Machine"""
    __revision__ = "$Revision: 262 $"

    from pyVC.Networks.Tools import MacGenerator

    macs = MacGenerator('52:54:00')

    errors = ( 'no_qemu_executable', \
               'no_qemu_lib_path' )

    platforms = ( )
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  graphic = False, \
                  snapshot = True, \
                  **keywords ):

        Base.VM.__init__( self, \
                          realmachine, \
                          name, \
                          **keywords )

        self.__graphic = graphic
        self.__snapshot = snapshot
        self.__pid = None

        from pyVC.errors import VMError
        
        if len(self.disks) > 4:
            raise VMError, \
                  ( "Error: Too many disks for QEMU VM, \
                    QEMU can only access 4 disk images concurrently.", \
                    2, \
                    self.realmachine.hostname, \
                    self.vmname \
                  )

    # Accessors
    
    def _get_graphic(self):
        """Gets the value of self.__graphic"""
        return self.__graphic
    
    def _set_graphic(self, graphic):
        """Sets the value of self.__graphic"""
        self.__graphic = graphic

    def _get_snapshot(self):
        """Gets the value of self.__snapshot"""
        return self.__snapshot

    def _set_snapshot(self, snapshot):
        """Sets the value of self.__snapshot"""
        self.__snapshot = snapshot
        
    # Control
        
    def start( self ):
        """Starts a QEMU VM"""
        from pyVC.Networks import VDE1
        from atexit import register
        
        graphic_command = ""
        snapshot_command = ""
        disk_command = ""
        network_command = ""
        kernel_command = ""
        
        # set graphic flag
        if not self.graphic:
            graphic_command = "-nographic"
        
        # set snapshot flag
        if self.snapshot:
            snapshot_command = "-snapshot"
            
        # attach all requested disks
        available_disks = ['hda', 'hdb', 'hdc', 'hdd']
        for disk in self.disks[:3]:
            disk_command += disk.qemu(available_disks)
            
        # set kernel parameters
        if self.kernel:

            kernel_command = "-kernel %s" % (self.kernel)
            if self.initrd:
                kernel_command += " -initrd %s" % (self.initrd)
            if self.kernelargs:
                kernel_command += " -append '%s" % (self.kernelargs)
		if self.root:
                    kernel_command += " root=%s'" % (self.root)
                else:
                    kernel_command += "'"

        else:
            kernel_command = "-boot c"

        # network commands
        # pre_vde_network_command is used to invoke vdeq before QEMU
        pre_vde_network_command = ""
        network_command = ""
        pre_command = ""
        post_command = ""

        if self.networks:
            for network in self.networks:
                (tmp_pre_command, interface_command, post_command) = network.qemu(self)
                network_command += interface_command + ' '

                if not tmp_pre_command in pre_command:
                    pre_command.append("%s " % (tmp_pre_command))

                if isinstance( network, VDE1.Network ) and \
                   not pre_vde_network_command:
                    pre_vde_network_command = self.realmachine.config['vde1']['vdeq_executable']
            if self.realmachine.qemu_version in ["0.7.0", "0.7.1", "0.7.2"]:
                network_command += " -nics %s %s" % (len(self.networks), pre_command)
        else:
            if self.realmachine.qemu_version in ["0.7.0", "0.7.1", "0.7.2"]:
                pass
            else:
                network_command = "-net none"

        if not self.__pid:
            
            print('%s %s %s -serial stdio -localtime %s -L %s %s %s -m %s %s' % \
                                      (pre_vde_network_command, \
                                       self.realmachine.config['qemu']['qemu_executable'], \
                                       network_command, \
                                       kernel_command, \
                                       self.realmachine.config['qemu']['qemu_lib_path'], \
                                       snapshot_command, \
                                       graphic_command, \
                                       self.memory, \
                                       disk_command)
                                      )       

            self.__pid = self.realmachine.term('%s %s %s -serial stdio -localtime %s -L %s %s %s -m %s %s' % \
                                      (pre_vde_network_command, \
                                       self.realmachine.config['qemu']['qemu_executable'], \
                                       network_command, \
                                       kernel_command, \
                                       self.realmachine.config['qemu']['qemu_lib_path'], \
                                       snapshot_command, \
                                       graphic_command, \
                                       self.memory, \
                                       disk_command)
                                      )

            pid = self.realmachine.popen(post_command)
            self.realmachine.wait(pid)

            self.status = "started"

            register(self.stop)
    
    def stop(self):
        """Stops a QEMU VM"""

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
        return "VM(\"%s\", %s, addrs=\"%s\", macaddr=\"%s\", kernel=\"%s\", kernelargs=\"%s\", initrd=\"%s\", graphic=%s, snapshot=%s, memory=%s, networks=%s, disks=%s, vmgroup=%s)" % \
                (self.vmname,
                 self.realmachine,
                 self.addrs,
                 self.macaddr,
                 self.kernel,
                 self.kernelargs,
                 self.initrd,
                 self.graphic,
                 self.snapshot,
                 self.memory,
                 self.networks,
                 self.disks,
                 self.vmgroup)

    # Properties

    graphic = property(_get_graphic, _set_graphic)
    snapshot = property(_get_snapshot, _set_snapshot)
