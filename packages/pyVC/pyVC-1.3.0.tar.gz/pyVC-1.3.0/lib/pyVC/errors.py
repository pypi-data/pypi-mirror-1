##
# Module containing the errors for pyVC.
##

__revision__ = "$Revision: 245 $"

##
# This object defines the base error class for pyVC.
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception, usually a string or integer.
# @param hostname The hostname of the Machine object where this exception occurred.
class pyVCError( Exception ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname ):
        Exception.__init__(self)
        self.value = value
        self.errid = errid
        self.hostname = hostname
        
    def __str__( self ):
        return repr( self.value )

##
# This object defines a Machine error exception.
# 
# <ul>
# <li>errid 'norouting' - Cannot enable routing on architecture.</li>
# <li>errid 'platform' - Platform not supported for this object.</li>
# <li>errid 'nosudo' - sudo not configured correctly.</li>
# <li>errid 'no_executable' - executable not found.</li>
# <li>errid 'notunmod' - module TUN not found.</li>
# <li>errid 'notundev' - tun device does not exist.</li>
# <li>errid 'notunwr' - tun device is not writable.</li>
# <li>errid 'notunuser' - users cannot bring up tun devices.</li>
# <li>errid 'outbridge' - Out of bridge inerfaces.</li>
# <li>errid 'outtap' - Out of tap inerfaces.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
# @param hostname The hostname of the Machine object where this exception occurred.
class MachineError( pyVCError ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname ):
        pyVCError.__init__(self, value, errid, hostname)

##
# This object defines a Network error exception. 
# 
# <ul>
# <li>errid 0 - Cannot exceed maximum number of VMs for this Network type.</li>
# <li>errid 1 - Cannot exceed maximum number of Machines for this Network type.</li>
# <li>errid 2 - Unhandled Network type for QEMU version.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
# @param hostname The hostname of the Machine object where this exception occurred.
# @param networkname The hostname of the Network object where this exception occurred.
class NetworkError( pyVCError ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname, networkname ):
        pyVCError.__init__(self, value, errid, hostname)

        self.networkname = networkname

##
# This object defines a Disk error exception. 
#
# <ul>
# <li>errid 0 - Could not open disk image.</li>
# <li>errid 1 - Could not open disk device.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
# @param hostname The hostname of the Machine object where this exception occurred.
class DiskError( pyVCError ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname ):
        pyVCError.__init__(self, value, errid, hostname)

##
# This object defines a VM error exception. 
#
# <ul>
# <li>errid 0 - Could not open kernel.</li>
# <li>errid 1 - Could not open initrd.</li>
# <li>errid 2 - Too many disks for QEMU VM.</li>
# <li>errid 3 - Too many disks for UML VM.</li>
# <li>errid 4 - Kernel required for UML VM.</li>
# <li>errid 5 - Kernel required for Xen VM.</li>
# <li>errid 6 - Could not connect to Xen hypervisor.</li>
# <li>errid 7 - Could not create domain on Xen hypervisor.</li>
# <li>errid 8 - Could not locate domain on Xen hypervisor.</li>
# <li>errid 9 - Could not shutdown domain on Xen hypervisor.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
# @param hostname The hostname of the Machine object where this exception occurred.
# @param vmname The hostname of the VM object where this exception occurred.
class VMError( pyVCError ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, hostname, vmname ):
        pyVCError.__init__(self, value, errid, hostname)

        self.vmname = vmname

##
# This object defines a Specification error exception.
# hostname is set to "Specification" automatically.
#
# <ul>
# <li>errid 0 - Duplicate IP address.</li>
# <li>errid 1 - Unknown Disk type.</li>
# <li>errid 2 - Unknown Network type.</li>
# <li>errid 3 - Unknown Helper type.</li>
# <li>errid 4 - Too many boot disks.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
class SpecificationError( pyVCError ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid ):
        pyVCError.__init__(self, value, errid, "Specification")

##
# This object defines a VCML error exception.
# hostname is set to "VCML" automatically.
#
# <ul>
# <li>errid 0 - Failed schema validation.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
# @param error_log The error log received from lxml.
class VCMLError( pyVCError ):

    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid, error_log ):
        pyVCError.__init__(self, value, errid, "VCML")

        self.error_log = error_log

##
# This object defines a pyvcd error exception.
# hostname is set to "pyVCd" automatically.
# 
# <ul>
# <li>errid 0 - Machine not found in pyvcd.</li>
# <li>errid 1 - Specification already loaded.</li>
# <li>errid 2 - Specification not loaded.</li>
# <li>errid 3 - VM not found / running.</li>
# <li>errid 4 - Console already in use.</li>
# </ul>
# 
# @param value The 'strerror' for the exception.
# @param errid The unique identifier for the exception.
class pyVCdError( pyVCError ):
    
    __revision__ = "$Revision: 245 $"
    
    def __init__( self, value, errid):
        pyVCError.__init__(self, value, errid, "pyVCd")
