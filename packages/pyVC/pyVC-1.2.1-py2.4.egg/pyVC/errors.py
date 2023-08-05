"""
Module containing the errors for pyVC.

MachineError is an exception that is raised when the Machiine's configuration doesn't match what you're trying to do, i.e. running a VM on an unsupported platform, running TAP w/out kernel support.
"""

__revision__ = "$Revision: 245 $"

class PyvcError( Exception ):
    """
    This object defines the base error class for pyVC.
    All errors in pyVC should include the 'realmachine' hostname, 
    so we can easily track down where the error occurred. 

    This object can be instantiated as:
        error = PyvcError(value, errid, hostname)
        value is an string describing the error
        errid is a string containing a short summary of the error
        hostname is the hostname of the Machine containing the error
    """

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname ):
        Exception.__init__(self)
        self.value = value
        self.errid = errid
        self.hostname = hostname
        
    def __str__( self ):
        return repr( self.value )

class MachineError( PyvcError ):
    """
    This object defines a Machine error exception.

    Errid 'norouting' - Cannot enable routing on architecture.
    Errid 'platform' - Platform not supported for this object.
    Errid 'nosudo' - sudo not configured correctly.
    Errid 'no_executable' - executable not found.
    Errid 'notunmod' - module TUN not found.
    Errid 'notundev' - /dev/net/tun is not writable.
    Errid 'notunwr' - /dev/net/tun is not writable.
    Errid 'outbridge' - Out of bridge inerfaces.
    Errid 'outtap' - Out of tap inerfaces.
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname ):
        PyvcError.__init__(self, value, errid, hostname)

class NetworkError( PyvcError ):
    """
    This object defines a Network error exception. 

    Errid 0 - Cannot exceed maximum number of VMs for this Network type.
    Errid 1 - Cannot exceed maximum number of Machines for this Network type.
    Errid 2 - Unhandled Network type for QEMU version.
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname, networkname ):
        PyvcError.__init__(self, value, errid, hostname)

        self.networkname = networkname

class DiskError( PyvcError ):
    """
    This object defines a Disk error exception. 

    Errid 0 - Could not open disk image.
    Errid 1 - Could not open disk device.
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname ):
        PyvcError.__init__(self, value, errid, hostname)

class VMError( PyvcError ):
    """
    This object defines a VM error exception. 

    Errid 0 - Could not open kernel.
    Errid 1 - Could not open initrd.
    Errid 2 - Too many disks for QEMU VM.
    Errid 3 - Too many disks for UML VM.
    Errid 4 - Kernel required for UML VM.
    Errid 5 - Kernel required for Xen VM.
    Errid 6 - Could not connect to Xen hypervisor.
    Errid 7 - Could not create domain on Xen hypervisor.
    Errid 8 - Could not locate domain on Xen hypervisor.
    Errid 9 - Could not shutdown domain on Xen hypervisor.
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname, vmname ):
        PyvcError.__init__(self, value, errid, hostname)

        self.vmname = vmname

class SpecificationError( PyvcError ):
    """
    This object defines a Specification error exception.

    Errid 0 - Duplicate IP address.
    Errid 1 - Unknown Disk type.
    Errid 2 - Unknown Network type.
    Errid 3 - Unknown Helper type.
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid ):
        PyvcError.__init__(self, value, errid, "Specification")

class VCMLError( PyvcError ):
    """
    This object defines a VCML error exception.

    Errid 0 - Failed schema validation.
    
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, error_log ):
        PyvcError.__init__(self, value, errid, "VCML")

        self.error_log = error_log

class PYVCDError( PyvcError ):
    """
    This object defines a pyvcd error exception.

    Errid 0 - Machine not found in pyvcd.
    Errid 1 - Specification already loaded.
    Errid 2 - Specification not loaded.
    Errid 3 - VM not found / running.
    Errid 4 - Console already in use.
    
    """
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid):
        PyvcError.__init__(self, value, errid, "pyvcd")
