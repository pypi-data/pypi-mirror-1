"""
Module containing the Machine object for a real Machine.

This module contains a pair of objects, Machine and MachineError. Machine implements the methods to 
control and configure a real Machine. The real Machine object handles all process interaction for the 
Machine and contains configuration information for the Machine. MachineError is an exception that is 
raised when the Machiine's configuration doesn't match what you're trying to do, i.e. running a VM on 
an unsupported platform, running TAP w/out kernel support.
"""

__revision__ = "$Revision: 260 $"

class Machine( object ):
    """
    This object defines a real Machine.
    
    This object can be instantiated as:
        machine = Machine(hostname)
        hostname is the hostname you wish to use, if your hostname is incorrectly set.
    """
    __revision__ = "$Revision: 260 $"
    
    def __init__( self, hostname = None ):
    
        from subprocess import Popen, PIPE
        from os import uname, geteuid
        from pyVC import Config
        from socket import gethostname
        import re
    
        self.config = Config()
    
        self.__networks = []
        self.__avail_interfaces = []
        self.__avail_bridges = []
        self.__used_interfaces = []   
        self.__pyvc_interfaces = []
        self.__test_results = {}
        self.__processes = {}

        self.__hostname = hostname and hostname or gethostname().split( '.', 1 )[0]
        self.__platform = uname()[0]
        self.__version = uname()[2]
        self.objectID = None
    
        # figure out if we need to use sudo
        if geteuid() != 0 and 'sudo_executable' in self.config['global']:
            self.__sudo = self.config['global']['sudo_executable']
        else:
            self.__sudo = ''

        # check for error conditions
        self.refresh()

        # find used interfaces
        if 'ifconfig_executable' in self.config['global']:
            process = Popen( '%s -s' % ( \
                             self.config['global']['ifconfig_executable'] ), \
                             stdout=PIPE, shell = True )
                
            output = process.stdout.readlines()
            process.wait()

            for line in output:
                ifname = re.match( "^[a-z]+(?:\d+(?::\d+)?)?", line )
                if ifname:
                    self.__used_interfaces.append(ifname.group())

        # add all unused taps to interfaces
        for number in range( 0, 16 ):
            current_tap = "tap%s" % number
            if current_tap not in self.__used_interfaces:
                self.__avail_interfaces.append( current_tap )

        # add all unused bridges to interfaces
        for number in range( 0,16 ):
            current_bridge = "pyvcbr%s" % number
            if current_bridge not in self.__used_interfaces:
                self.__avail_bridges.append( current_bridge )

    def check_platform( self, platforms ):
        """
        Raises a MachineError if this machine's platform is not in platforms.

        >>> machine.check_platform(['Linux'])
        >>>
        """

        from pyVC.errors import MachineError

        if platforms:
            if self.platform not in platforms:
                raise MachineError, ( 'ERROR: Platform %s not supported for this object.' % (self.platform), 
                                      'platform',
                                      self.hostname )

    def check_errors( self, errors ):
        """
        Raises a MachineError if this machine contains any of the errors in errors.

        >>> machine.check_errors(['nosudo'])
        """

        for error in errors:
            if error in self.__test_results.keys():
                self._handle_error(error)

    def _handle_error( self, error ):
        """
        Raises the correct exception for error. 

        >>> self._handle_error('nosudo')
        """

        from pyVC.errors import MachineError

        if error == 'nosudo':
            raise MachineError, ( 'ERROR: sudo not configured correctly. \n \
Make sure sudo can operate commands as root without asking for a password', 'nosudo', self.hostname )
        elif error == 'no_dhcpd_executable':
            raise MachineError, ( 'ERROR: dhcpd not found. \n \
Please install dhcpd as root or modify the path in pyVC.ini', 'no_dhcpd_executable', self.hostname )
        elif error == 'no_ifconfig_executable':
            raise MachineError, ( 'ERROR: ifconfig not found. \n \
Please install ifconfig as root or modify the path in pyVC.ini' \
                                               'no_ifconfig_executable', self.hostname )
        elif error == 'no_iptables_executable':
            raise MachineError, ( 'ERROR: iptables not found. \n \
Please install iptables as root or modify the path in pyVC.ini',
                                               'no_iptables_executable', self.hostname )
        elif error == 'no_vde_switch_executable':
            raise MachineError, ( 'ERROR: vde_switch not found. \n \
Please vde_switch dhcpd as root or modify the path in pyVC.ini',
                                  'no_vde_switch_executable',
                                  self.hostname )
        elif error == 'notunmod':
            raise MachineError, ( 'ERROR: module tun not found. \n \
Run "modprobe tun" as root.', 'notunmod', self.hostname)
        elif error == 'notundev':
            raise MachineError, ( 'ERROR: /dev/net/tun not found. \n \
Run "cd /dev; sh MAKEDEV tun" as root.', 'notundev', self.hostname )
        elif error == 'notunwr':
            raise MachineError, ( 'ERROR: /dev/net/tun not writable. \n \
Run "chmod 666 /dev/net/tun" as root.', 'notun', self.hostname )
        elif error == 'no_qemu_executable':
            raise MachineError, ( 'ERROR: qemu not found. \n \
Please install qemu as root or modify the path in pyVC.ini',
                                  'no_qemu_executable',
                                  self.hostname )
        elif error == 'no_vdeq_executable':
            raise MachineError, ( 'ERROR: vdeq not found. \n \
Please install vdeq as root or modify the path in pyVC.ini',
                                  'no_vdeq_executable',
                                  self.hostname )
        if error == 'no_qemu_lib_path':
            raise MachineError, ( 'ERROR: qemu libs not found. \n \
Please install qemu libs as root or modify the path in pyVC.ini',
                                  'no_qemu_lib_path',
                                  self.hostname )

    def refresh( self ):
        """
        Updates the list of error conditions associated with the real Machine.

        >>> machine.refresh()
        """
        
        from subprocess import Popen, PIPE
        from os import geteuid

        self.__test_results = {}
        
        if self.platform == 'Linux':
            process = Popen( self.config['global']['lsmod_executable'], \
                             stdout = PIPE, shell = True )
            modules = process.stdout.readlines()
            modules_joined = "".join( modules )
            process.wait()

            if not 'tun'  in modules_joined:
                self.__test_results['notunmod'] = True
    
            if Popen( 'test -e /dev/net/tun', \
                      shell = True ).wait():
                self.__test_results['notundev'] = True
        
            if Popen( 'test -w /dev/net/tun', \
                      shell = True ).wait():
                self.__test_results['notunwr'] = True
    
        for category in self.config:
            for item in self.config[category]:
                if 'executable' in item:
                    if Popen( 'test -x %s' % ( self.config[category][item] ), shell = True ).wait():
                        self.__test_results['no_%s' % (item)] = True
                elif 'path' in item:
                    if Popen( 'test -d %s' % ( self.config[category][item] ), shell = True ).wait():
                        self.__test_results['no_%s' % (item)] = True

        euid = geteuid()
                    
        if self.platform == 'Linux':
            process = Popen( self.config['global']['lsmod_executable'], \
                             stdout = PIPE, shell = True )
            modules = process.stdout.readlines()
            modules_joined = "".join( modules )
            process.wait()

            if not 'tun'  in modules_joined:
                self.__test_results['notunmod'] = True
    
            if Popen( 'test -e /dev/net/tun', \
                      shell = True ).wait():
                self.__test_results['notundev'] = True
        
            if Popen( 'test -w /dev/net/tun', \
                      shell = True ).wait():
                self.__test_results['notunwr'] = True

        if 'sudo_executable' in self.config['global'] and euid != 0:
            process = Popen('%s -S id -u' % (self.config['global']['sudo_executable']), \
                            shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            process.stdin.write('\n')
            sudo_test = process.stdout.readline().strip()
            process.wait()

            if sudo_test != '0':
                self.__test_results['nosudo'] = True
        elif euid != 0:
            self.__test_results['nosudo'] = True
            
        return True
    
                    
    def add_network( self, newnet ):
        """
        Associates a Network object with the real Machine.

        NOTE: This is used by Network objects to add themselves to the Machine, and is not generally used.

        >>> machine.add_network(Network)
        """
        
        from pyVC.Networks.Base import Network
        
        if issubclass( type( newnet ), Network ):
            self.__networks.append( newnet )
        else:
            raise TypeError, "ERROR: Got %s for first argument to add_network,\
                              expected subclass of %s" % \
                              ( type( newnet ), Network )
                                    
    def add_interface ( self, newif ):
        """
        Associates a network Interface with the real Machine.

        NOTE: This is used by Network objects to add themselves to the Machine, and is not generally used.

        >>> machine.add_interface('tap0')
        """
        
        if not newif in self.__pyvc_interfaces and \
           not newif in self.__used_interfaces:
            self.__pyvc_interfaces.append(newif)
                
    def remove_interface( self, oldif ):
        """
        Unassociates a network Interface with the real Machine.

        NOTE: This is used by Network objects to add themselves to the Machine, and is not generally used.

        >>> machine.remove_interface('tap0')
        """
        
        if oldif in self.__pyvc_interfaces:
            self.__pyvc_interfaces.remove(oldif)

    def bridge( self, bridge = None ):
        """
        Returns a string containing an available bridge interface from the available interfaces.

        >>> machine.bridge()
        "pyvcbr0"
        """

        from pyVC.errors import MachineError

        if not bridge:
            try:
                iface = self.__avail_bridges.pop(0)
            except IndexError:
                raise MachineError, ( 'ERROR: Out of bridge interfaces. \n', 'outbridge', self.__hostname )
            #self.__pyvc_interfaces.append(iface)
            return iface
        else:
            self.__avail_bridges.insert(0, bridge)
            if bridge in self.__pyvc_interfaces:
                self.__pyvc_interfaces.remove(bridge)

    def tap( self, tap = None ):
        """
        Returns a string containing an available TAP interface from the available interfaces.

        >>> machine.tap()
        "tap0"
        """

        from pyVC.errors import MachineError

        if not tap:
            try:
                iface = self.__avail_interfaces.pop(0)
            except IndexError:
                raise MachineError, ( 'ERROR: out of tap interfaces. \n', 'outtap', self.__hostname )
            #self.__pyvc_interfaces.append(iface)
            return iface
        else:
            self.__avail_interfaces.insert(0, tap)
            if tap in self.__pyvc_interfaces:
                self.__pyvc_interfaces.remove(tap)
   
    def term( self, command ):
        """
        Executes a command inside a Term object on the machine and returns the process PID. 

        This PID is used as a key for future operations on this Term object. 

        >>> machine.term(command)
        command is the command to execute
        """

        from pyVC.Term import Term

        process = Term( command )

        self.__processes[process.pid] = process

        return process.pid

    def term_connect( self, pid = None, pty = None ):
        """
        Opens a connection to a term object specified by a PID. 

        This method configures the local terminal to have direct access to the process inside the Term object.

        >>> machine.term_connect(pid)
        pid is the PID of the Term object returned by term()
        """

        from pyVC.Term import Term

        if not pid and not pty:
            raise ValueError, "ERROR: No pid or pty specified"
        if pid and pty:
            raise ValueError, "ERROR: No pid and pty specified"
        elif pid: 
            if pid in self.__processes and \
               isinstance(self.__processes[pid], Term):
                self.__processes[pid].connect()
            else:
                raise ValueError, "ERROR: No process corresponding to pid %d on %s" % (pid, self.hostname)
        elif pty:
            term = Term(pty=pty)
            term.connect()

    def term_socket( self, pid=None, pty=None ):
        """
        Opens a connection socket for a Term object.

        This opens up the socket to be connected to remotely for access to the process inside the Term object.

        Returns the port number that the socket is listening on. 
        
        >>> machine.term_socket(pid)
        pid is the PID of the Term object returned by term()
        """

        from pyVC.Term import Term

        if not pid and not pty:
            raise ValueError, "ERROR: No pid or pty specified"
        if pid and pty:
            raise ValueError, "ERROR: No pid and pty specified"
        elif pid:
            if pid in self.__processes and \
               isinstance(self.__processes[pid], Term):
                return self.__processes[pid].socket()
            else:
                raise ValueError, "ERROR: No process corresponding to pid %d on %s" % (pid, self.hostname)
        elif pty:
            self.__processes[pty] = Term(pty=pty)
            return self.__processes[pty].socket()
            

    def term_serve( self, pid = None, pty = None ):
        """
        Enter connection serving loop for a Term object.

        This method enters the polling loop for the previously opened socket. 
        
        This method will not return until the connection has ended, and is usually used as a one-way call from Pyro. 

        >>> machine.term_serve(pid)
        pid is the PID of the Term object returned by term()
        """

        from pyVC.Term import Term

        if not pid and not pty:
            raise ValueError, "ERROR: No pid or pty specified"
        if pid and pty:
            raise ValueError, "ERROR: No pid and pty specified"
        elif pid:
            if pid in self.__processes and \
               isinstance(self.__processes[pid], Term):
                self.__processes[pid].serve()
            else:
                raise ValueError, "ERROR: No process corresponding to pid %d on %s" % (pid, self.hostname)
        elif pty:
            if pty in self.__processes and \
               isinstance(self.__processes[pty], Term):
                self.__processes[pty].serve()

    def popen( self, command ):
        """
        Executes a command on the Machine and returns the PID of the command.

        This PID is used as a key for future operations on this Term object. 

        >>> machine.popen(command)
        command is the command to execute
        """

        from subprocess import Popen, PIPE

        process = Popen( command, 
                         shell=True,
                         stdin = PIPE, 
                         stdout = PIPE, 
                         stderr = PIPE )

        self.__processes[process.pid] = process
        
        return process.pid

    def wait( self, pid ):
        """
        Waits for a process to finish on the Machine.

        >>> machine.wait(pid)
        pid is the PID of the Term object returned by popen()
        """

        if pid in self.__processes:
            try:
                self.__processes[pid].wait()
            except OSError, (errno, strerror):
                if errno == 10:
                    pass
                else:
                    raise
        else:
            raise ValueError, "ERROR: No process corresponding to pid %d on %s" % (pid, self.hostname)

    def kill( self, pid, signal ):
        """
        Kills a process on the Machine.
        
        >>> machine.kill(pid, signal)
        pid is the PID of the Term object returned by popen()
        signal is a signal ID or integer 
        """

        if pid in self.__processes:
            try:
                self.__processes[pid].kill(signal)
            except AttributeError:
                from os import kill
                try:
                    kill( pid, signal )
                except OSError, (errno, strerror):
                    if errno == 3:
                        pass
                    else:
                        raise
        else:
            raise ValueError, "ERROR: No process corresponding to pid %d on %s" % (pid, self.hostname)

    def isfile( self, filename ):
        """
        Checks for the existence of a file on the Machine.

        >>> machine.isfile(filename)
        filename is the path to the file on the Machine to check
        """

        from os.path import isfile

        return isfile(filename)

    def exists( self, path ):
        """
        Checks for the existence of a path on the Machine.

        >>> machine.exists(path)
        path is a path to a device / file / link on teh filesystem
        """

        from os.path import exists

        return exists(path)

    def _get_hostname ( self ):
        """
       Returns a string containing the hostname corresponding to the real Machine.

       >>> self._get_hostname()
       "localhost"
       """
        
        return self.__hostname
    
    def _get_version (self):
        """
        Returns a string containing the version of the real Machine, as returned by uname -r.

        >>> self._get_version()
        "2.6.15-27-386"
        """
        
        return self.__version
    
    def _get_platform (self):
        """
        Returns a string containing the operating system of the real Machine, as returned by uname -o.

        >>> self._get_platform()
        "Linux"
        """
        
        return self.__platform
    
    def _get_sudo( self ):
        """
        Returns a string containing the command used for sudo on the real Machine.

        >>> self._get_sudo()
        "/usr/bin/sudo"
        """
        
        return self.__sudo
    
    def _get_qemu_version( self ):
        """
        Returns the version of qemu installed at config['qemu']['qemu_executable'].

        >>> self._get_qemu_version()
        "0.8.0"
        """
        
        from subprocess import Popen, PIPE
        from pyVC import Config
        
        config = Config()
        
        if 'qemu_executable' in config['qemu']:
            process = Popen(config['qemu']['qemu_executable'], shell = True, \
                            stdout = PIPE, stderr = PIPE)
            output = process.stdout.readline(). \
                         split(' ')[4].rstrip(',')
            process.wait()
        else:
            output = "not installed"

        return output

    def _get_networks ( self ):
        """
        Returns a list of the Networks running on the real Machine.

        >>> self._get_networks()
        """
        
        return self.__networks
    
    def _get_used_interfaces( self ):
        """
        Returns a list of existing used interfaces on the real Machine.

        >>> self._get_used_interfaces()
        """
        
        return self.__used_interfaces
    
    def _get_pyvc_interfaces( self ):
        """
        Returns a list of interfaces used by pyVC on the real Machine.

        >>> self._get_pyvc_interfaces()
        """
        
        return self.__pyvc_interfaces
 
    def __str__( self ):
        return self._get_hostname()

    def __repr__( self ):
        return "Machine(\"%s\")" % self.__hostname

    # Properties

    hostname = property(_get_hostname)
    platform = property(_get_platform)
    version = property(_get_version)
    sudo = property(_get_sudo)
    qemu_version = property(_get_qemu_version)
    networks = property(_get_networks)
    used_interfaces = property(_get_used_interfaces)
    pyvc_interfaces = property(_get_pyvc_interfaces)
