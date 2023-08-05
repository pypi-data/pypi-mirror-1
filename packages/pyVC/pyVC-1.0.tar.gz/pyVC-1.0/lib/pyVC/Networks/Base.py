"""
Package containing the base object for the Network.

This package two objects, Network, which all other Network objects derive from; and Cable,
which all other Cable objects derive from.  In this module, Network and Cable should not be 
instantiated, and the non-shared methods will raise NotImplementedError when executed. 

Each Network contains 2 class tuples, errors and platforms.
errors defines the list of errors that cause this Network to fail.
platforms lists the OS platforms that this Network is functional on, as defined by uname(1).
"""
__revision__ = "$Revision$"


class Network(object):
    """
    This object defines the base class for a Network object.
    """
    __revision__ = 1

    errors = ()

    platforms = ()
    
    max_vms = None

    max_realmachines = None

    dhcp_capable = 0

    def __init__( self, 
                  realmachines, 
                  lanname, 
                  subnet = None,
                  dns_servers = None,
                  **keywords ):

        self.__keywords = keywords

        self.__vms = {}
        self.__status = "stopped"

        self.__lanname = lanname
        self.__subnet = subnet
        self.__realmachines = realmachines
        self.__dns_servers = dns_servers
        self.__helpers = []
        self.__switches = {}
        self.__cables = []

        if self.max_realmachines and len(realmachines) > self.max_realmachines:
            raise ValueError, \
        ( "ERROR: %s only supports a maximum of %s realmachines" % \
          ( type(self),
            self.max_realmachines )
        )


        for realmachine in realmachines:

            realmachine.check_errors( self.errors )
            realmachine.check_platform( self.platforms )

            realmachine.add_network( self )

    def __del__(self):
        self.stop()

    def interface(self, realmachine):
        """
        Returns an interface associated with a Machine.

        >>> self.interface(realmachine)
        realmachine = Machine
        """

        if realmachine in self.__switches:
            return self.__switches[realmachine][1]
        else:
            raise KeyError, \
        ( "ERROR: Can't find interface for %s on %s" % \
          ( realmachine.hostname,
            self.lanname )
        )

    def add_interface(self, realmachine, interface, pid = 0): 
        """
        Adds an interface and optionally a PID to the internal list of interfaces on the network.

        >>> network.add_interface(realmachine, interface, pid)
        """

        if realmachine not in self.__switches:
            self.__switches[realmachine] = (pid, interface)
        else:
            if self.__switches[realmachine][0] != pid or \
               self.__switches[realmachine][1] != interface:
                raise ValueError, \
            ( "ERROR: %s already has an interface on %s" % \
              ( realmachine.hostname,
                self.lanname )
            )
            else:
                pass

    def del_interface(self, realmachine):
        """
        Removes an interface previously associated with the network.

        >>> network.del_interface(realmachine)
        """

        if realmachine in self.__switches:
            del self.__switches[realmachine]
        else:
            raise KeyError, \
        ( "ERROR: Can't find interface for %s on %s" % \
          ( realmachine.hostname,
            self.lanname )
        )
        
    def pid(self, realmachine):
        """
        Returns a pid associated with a real Machine.
        
        >>> self.pid(realmachine)
        realmachine = Machine
        """

        if realmachine in self.__switches:
            return self.__switches[realmachine][0]
        
    def _get_cables(self):
        """
        Returns a list of cables associated with the Network.
        
        >>> self._get_cables()
        """

        return self.__cables
        
    def add_vm( self, vm, ips ):
        """
        Associates a VM to IP address mapping with the Network.
        
        >>> self.add_ip(vm, ips)
        vm = VM
        ip is a list of strings containing a single IP address, in the form xxx.xxx.xxx.xxx.
        """

        from pyVC.VirtualMachines.Base import VM

        if issubclass( type( vm ), VM ):
            if vm not in self.__vms:
                if self.max_vms:
                    if len(self.vms) <= self.max_vms:
                        self.__vms[vm] = ips
                    else:
                        raise RuntimeError, \
                    ( 'ERROR: Cannot exceed maximum number of VMs for this Network type.' )
                else:
                    self.__vms[vm] = ips
            else:
                self.__vms[vm] += ips
        else:
            raise TypeError, \
        ( 'Got %s for first argument to add_ip, expected subclass of %s' % \
          ( type( vm ), VM ) \
        )


    def add_helper(self, helper):
        """
        Associates a Helper with the Network.
        
        >>> self.add_helper(helper)
        helper = Helper
        """

        from pyVC.Helpers.Base import Helper

        if issubclass( type( helper ), Helper ):
            if helper not in self.__helpers:
                self.__helpers.append(helper)
        else:
            raise TypeError, \
        ( 'Got %s for first argument to add_helper, expected subclass of %s' % \
          ( type( helper ), Helper ) \
        )

    def add_realmachine( self, realmachine ):
        """
        Associates a real Machine with the Network.
        
        >>> self.add_realmachine(realmachine)
        realmachine = Machine
        """

        if realmachine not in self.__realmachines:
            if self.max_realmachines:
                if len(self.realmachines) <= self.max_realmachines:
                    self.__realmachines.append(realmachine)
                else:
                    raise RuntimeError, \
                    ( "ERROR: %s only supports a maximum of %s realmachines" % \
                      ( type(self),
                        self.max_realmachines )
                    )
            else:
                self.__realmachines.append(realmachine)

    def ips( self, vm ):
        """
        Returns a list of IPs corresponding to a VM.
        
        >>> self.ips(vm)
        vm = VM
        """

        from pyVC.VirtualMachines.Base import VM

        if issubclass( type( vm ), VM ):
            if vm in self.__vms:
                return self.__vms[vm]
            else:
                raise AttributeError
        else:
            raise TypeError, \
        ( 'Got %s for first argument to ip, expected subclass of %s' % \
          ( type( vm ), IP ) \
        )

    def _get_vms ( self ):
        """
        Returns a list of VMs associated with the Network.
        
        >>> self._get_vms()
        """
        
        return self.__vms.keys()
    
    def _get_realmachine( self ):
        """
        Returns the primary real Machine associated with the Network.

        >>> self._get_realmachine()
        """
        
        return self.__realmachines[0]
        
    def _get_realmachines( self ):
        """
        Returns a list of real Machines associated with the Network.

        >>> self._get_realmachines()
        """
        
        return self.__realmachines
        
    def _get_lanname( self ):
        """
        Returns the name of the Network.

        >>> self._get_lanname()
        """
        
        return self.__lanname
    
    def _get_subnet(self):
        """
        Returns the subnet of the Network.

        >>> self._get_subnet()
        """
        
        return self.__subnet
      
    def _get_helpers(self):
        """
        Returns a list of the Helpers associated with the Network.

        >>> self._get_helpers()
        """

        return self.__helpers

    def _get_dns_servers(self):
        """
        Returns a list of the DNS Servers associated with the Network.

        >>> self._get_dns_servers()
        """

        return self.__dns_servers

    def _get_status( self ):
        """
        Returns the status of the Network.

        >>> self._get_status()
        """
        
        return self.__status

    def _set_status( self, status ):
        """
        Sets the status of the Network.

        >>> self._set_status(status)
        """
        
        if status == 'stopped' or \
           status == 'started' or \
           status == None:
            self.__status = status

    vms = property(_get_vms)
    realmachine = property(_get_realmachine)
    realmachines = property(_get_realmachines)
    lanname = property(_get_lanname)
    subnet = property(_get_subnet)
    helpers = property(_get_helpers)
    dns_servers = property(_get_dns_servers)
    status = property(_get_status, _set_status)
    cables = property(_get_cables)

    # Abstract methods

    def start( self ):
        """
        Abstract method to start the Network object.

        >>> self.start()
        """
        
        raise NotImplementedError
         
    def stop( self ):
        """
        Abstract method to stop the Network object.
        
        >>> self.stop()
        """
        
        raise NotImplementedError
    
class Cable( object ):
    """
    This object defines the base class for a Cable object.
    """
    __revision__ = "$Revision$"
    
    def __init__ ( self, network, realmachine1, realmachine2 ):

        self.__realmachine1 = realmachine1
        self.__realmachine2 = realmachine2
        self.__network = None
        self.__status = "stopped"
        
        if issubclass( type( network ), Network ):
            self.__network = network
        else:
            raise TypeError, \
        ( 'Got %s for first argument of Cable constructor, expected subclass of %s' % \
          ( type( netork ), Network ) \
        )

    def _get_realmachine1(self):
        """
        Returns the local real Machine associated with this Cable.
        """
        
        return self.__realmachine1
    
    def _get_realmachine2(self):
        """
        Returns the remote real Machine associated with this Cable.
        """
        
        return self.__realmachine2

    def _get_network(self):
        """
        Returns the Network associated with this Cable.
        """
        
        return self.__network

    def _get_status( self ):
        """
        Returns the status of the Cable.

        >>> self._get_status()
        """
        
        return self.__status

    def _set_status( self, status ):
        """
        Sets the status of the Cable.

        >>> self._set_status(status)
        """
        
        self.__status = status


    # Properties

    realmachine1 = property(_get_realmachine1)
    realmachine2 = property(_get_realmachine2)
    network = property(_get_network)
    status = property(_get_status, _set_status)
        
    # Abstract methods
        
    def start( self ):
        """
        Abstract method to start the Cable object.
        """
        
        raise NotImplementedError
    
    def stop( self ):
        """
        Abstract method to stop the Cable object.
        """
        
        raise NotImplementedError
