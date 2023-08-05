"""This package contains the classes to implement a XEN VM"""
__revision__ = "$Revision: 259 $"

from pyVC.VirtualMachines import Base

class VM( Base.VM ):
    """This object defines a XEN Virtual Machine"""
    __revision__ = "$Revision: 259 $"

    from pyVC.Networks.Tools import MacGenerator

    macs = MacGenerator('00:16:3E')

    errors = ( )

    platforms = ( 'Linux' )
    
    def __init__( self, \
                  realmachine, \
                  name, \
                  kernel = None, \
                  graphic = False, \
                  **keywords ):

        Base.VM.__init__( self, \
                          realmachine, \
                          name, \
                          kernel = kernel, \
                          **keywords )

        self.__graphic = graphic
        self.__domid = None
        self.__pty = None

        if not self.kernel:
            raise VMError, \
                  ( "Error: Kernel required for Xen VM", \
                    5, \
                    self.realmachine.hostname, \
                    self.vmname \
                  )

        if not self.root:
            self.root = "/dev/xvda1"
        
    # Accessors
    
    def _get_domid(self):
        """Gets the value of self.__domid"""
        return self.__domid
    
    def _get_pty(self):
        """Gets the value of self.__pty"""
        return self.__pty
    
    def _get_graphic(self):
        """Gets the value of self.__graphic"""
        return self.__graphic
    
    def _set_graphic(self, graphic):
        """Sets the value of self.__graphic"""
        self.__graphic = graphic

    # Control
        
    def start( self ):
        """Starts a XEN VM"""
        import libvirt
        import string
        from elementtree.ElementTree import Element, SubElement, tostring, fromstring
        from atexit import register
        from pyVC.errors import VMError

        try:
	    #conn = libvirt.open(self.realmachine.hostname)
	    conn = libvirt.open(None)
        except libvirt.libvirtError, e:
            raise VMError, ( "ERROR: Could not connect to Xen hypervisor.", \
                             6, \
                             self.realmachine.hostname, \
                             self.vmname \
                           )

        dom_xml = Element('domain', type='xen')

        SubElement(dom_xml, 'name').text = str(self.vmname)

        os = SubElement(dom_xml, 'os')
        SubElement(os, 'type').text = 'linux'
        SubElement(os, 'kernel').text = str(self.kernel)
        SubElement(os, 'root').text = str(self.root)
        if self.initrd:
            SubElement(os, 'initrd').text = str(self.initrd)
        if self.kernelargs:
            SubElement(os, 'cmdline').text = str(self.kernelargs)

        SubElement(dom_xml, 'memory').text = str(int(self.memory) * 1024)
        SubElement(dom_xml, 'vcpu').text = "1"

        devices = SubElement(dom_xml, 'devices')
        available_disks = ["xvd%s" % (id) for id in string.ascii_lowercase]
        for disk in self.disks:
            devices.append(disk.xen(available_disks))

        for network in self.networks:
            devices.append(network.xen(self))
        
        if not self.__domid:
            
            print tostring(dom_xml)
            try:
                domain = conn.createLinux(tostring(dom_xml), 0)
                self.__domid = domain.ID()
            except libvirt.libvirtError:
                raise VMError, ( "ERROR: Could not create domain on Xen hypervisor", \
                                 7, \
                                 self.realmachine.hostname, \
                                 self.vmname, \
                               )

            new_dom_xml = fromstring(domain.XMLDesc(0))

            self.__pty = new_dom_xml.find('devices').find('console').attrib['tty']
                 
            self.status = "started"

            register(self.stop)
    
    def stop(self):
        """Stops a XEN VM"""

        import libvirt
        from signal import SIGTERM
        from pyVC.errors import VMError
        
        if self.status == "started":
            try:
                #conn = libvirt.open(self.realmachine.hostname)
                conn = libvirt.open(None)
            except libvirt.libvirtError, e:
                raise VMError, ( "ERROR: Could not connect to Xen hypervisor.", \
                                 6, \
                                 self.realmachine.hostname, \
                                 self.vmname \
                               )

            try:
                vm = conn.lookupByName(self.vmname)
            except libvirt.libvirtError:
                raise VMError, ( "ERROR: Could not locate domain on Xen hypervisor.", \
                                 8, \
                                 self.realmachine.hostname, \
                                 self.vmname \
                               )
           
            rc = vm.shutdown()
            if rc != 0:
                raise VMError, ( "ERROR: Could not shutdown domain on Xen hypervisor.", \
                                 9, \
                                 self.realmachine.hostname, \
                                 self.vmname \
                               )
    
            self.status = "stopped"

    def console(self, socket=False):
        """Provides a console for a VM"""
        
        if self.pty:
            if socket:
                return (self.realmachine.hostname, self.realmachine.term_socket(pty=self.pty))
            else:
                self.realmachine.term_connect(pty=self.pty)

    def serve(self):
        """Starts the serving loop for the VM"""
        if self.pty:
            self.realmachine.term_serve(pty=self.pty)

    def __str__( self ):
        return self.vmname

    def __repr__(self):
        return "VM(\"%s\", %s, addrs=\"%s\", macaddr=\"%s\", kernel=\"%s\", kernelargs=\"%s\", initrd=\"%s\", graphic=%s, memory=%s, networks=%s, disks=%s, vmgroup=%s)" % \
                (self.vmname,
                 self.realmachine,
                 self.addrs,
                 self.macaddr,
                 self.kernel,
                 self.kernelargs,
                 self.initrd,
                 self.graphic,
                 self.memory,
                 self.networks,
                 self.disks,
                 self.vmgroup)

    # Properties

    graphic = property(_get_graphic, _set_graphic)
    pty = property(_get_pty)
    domid = property(_get_domid)
