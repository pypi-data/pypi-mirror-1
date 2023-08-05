"""This package contains the base classes to implement a \
virtual cluster specification"""
__revision__ = "$Revision: 219 $"

class Specification( dict ):
    """This object defines a VCML Cluster"""
    __revision__ = "$Revision: 219 $"
    
    def __init__( self, realmachines ):
        """Initialize a VCML Cluster object"""

        dict.__init__(self)
        self.__cluster = None
        self.__realmachines = realmachines
        self.__disks = {}
        self.__files = []
        
        self._fix_addresses()
        self.__check()
        
    def _fix_addresses( self ):
        """Build indexes into the config"""
        for network, networkparams in self['NETWORKS'].items():
            for hostparams in networkparams['HOSTS'].values():
                if not hostparams.has_key( 'addrs' ):
                    hostparams['addrs'] = self.create_ip(network)
                for ifparams in hostparams['INTERFACES'].values():
                    if not ifparams.has_key( 'addrs' ):
                        ifparams['addrs'] = self.create_ip(ifparams['network'])
        
    def __check( self ):
        """Check a configuration"""

        addresses = []

        for lanname in self['NETWORKS'].keys():
            addresses += [i['addrs'] \
                           for i in \
                           [hostparams['INTERFACES'] \
                             for hostparams in self['NETWORKS'][lanname]['HOSTS'].values()\
                           ] if 'addrs' in i]
            addresses += [hostparams['addrs'] \
                           for hostparams in self['NETWORKS'][lanname]['HOSTS'].values() \
                           if 'addrs' in hostparams]

            if 'addrs' in self['NETWORKS'][lanname]:
                addresses += [self['NETWORKS'][lanname]['addrs']]

            if 'realhosts' in self['NETWORKS'][lanname]:
                if self['NETWORKS'][lanname]['realhosts'] in ['localhost', '127.0.0.1']:
                    del self['NETWORKS']['realhosts']

        for address in addresses:
            if addresses.count( address ) > 1:
                raise ValueError, 'ERROR: Duplicate IP %s detected' % \
                                    ( address )

    def create(self):
        """Returns the object tree for the specification"""
        
        from copy import deepcopy

        cluster = {}

        # check for the existence of all needed realmachines
        for lanargs in self['NETWORKS'].values():
            if 'realhosts' in lanargs:
                for realhostname in lanargs['realhosts'].split(','):
                    if realhostname in self.__realmachines.keys():
                        if not self.__realmachines[realhostname]:
                            raise LookupError, "ERROR: %s not found in pyvcd realmachines" % (lanargs['realhosts'])
                    else:
                        raise LookupError, "ERROR: %s not found in pyvcd realmachines" % (lanargs['realhosts'])
            for hostargs in lanargs['HOSTS'].values():
                if 'realhost' in hostargs:
                    if hostargs['realhost'] in self.__realmachines.keys():
                        if not self.__realmachines[hostargs['realhost']]:
                            raise LookupError, "ERROR: %s not found in pyvcd realmachines" % (hostargs['realhost'])
                    else:
                        raise LookupError, "ERROR: %s not found in pyvcd realmachines" % (hostargs['realhost'])

        # create disk objects
        for diskname, diskargs in self['DISKS'].items():

            if diskargs['type'] == 'image':
                from pyVC.Disks.Image import Disk
            elif diskargs['type'] == 'nfs':
                from pyVC.Disks.NFS import Disk
            elif diskargs['type'] == 'physical':
                from pyVC.Disks.Physical import Disk
            else:
                raise ValueError,  "ERROR: unsupported disk type %s" % (diskargs['type'])

            realmachines = [self.__realmachines.values()[0]]
            self.__disks[diskname] = Disk(realmachines, **diskargs)

        # create all networks
        for lanname, lanargs in self['NETWORKS'].items():
            
            if lanargs['type'] == 'vde1':
                from pyVC.Networks.VDE1 import Network
            elif lanargs['type'] == 'multicast':
                from pyVC.Networks.Multicast import Network
            elif lanargs['type'] == 'user':
                from pyVC.Networks.User import Network
            elif lanargs['type'] == 'tap':
                from pyVC.Networks.TAP import Network
            else:
                raise ValueError,  "ERROR: unsupported network type %s" % (lanargs['type'])

            tmpla = deepcopy(lanargs)
            del tmpla['HOSTS']
            
            if 'realhosts' in tmpla:
                realmachines = [realmachine for realmachine in self.__realmachines.values() if realmachine.hostname in tmpla['realhosts'].split(',')]
                del tmpla['realhosts']
            else:
                realmachines = [self.__realmachines.values()[0]]

            for tmplanname, tmplanargs in self['NETWORKS'].items():
                for hostname, hostargs in tmplanargs['HOSTS'].items():
                    for ifargs in hostargs['INTERFACES'].values():
                        if lanname == ifargs['network']:
                            if 'realhost' in hostargs:
                                realmachines.append(self.__realmachines[hostargs['realhost']])
                            elif 'realhost' not in hostargs and \
                                 'realhosts' in tmplanargs:
                                realmachines.append(self.__realmachines[tmplanargs['realhosts'].split(',')[0]])

            for helper in self['HELPERS']:
                helpername, helperargs = helper.items()[0]



            network = Network( realmachines, \
                               lanname, \
                               **tmpla )
            cluster[lanname] = network

        # create all hosts for the network
        for lanname, lanargs in self['NETWORKS'].items():
            for hostname, hostargs in lanargs['HOSTS'].items():

                network = cluster[lanname]
                
                if hostargs['type'] == 'qemu':
                    from pyVC.VirtualMachines.QEMU import VM
                elif hostargs['type'] == 'uml':
                    from pyVC.VirtualMachines.UML import VM
                elif hostargs['type'] == 'xen':
                    from pyVC.VirtualMachines.Xen import VM
                else:
                    raise ValueError,  "ERROR: unsupported VM type %s" % (hostargs['type'])

                networks = [network]
                disks = []
                
                # add other networks for additional interfaces
                for ifargs in hostargs['INTERFACES'].values():
                    networks.append(cluster[ifargs['network']])

                # add disks
                for diskargs in hostargs['DISKS'].values():
                    disks.append(self.__disks[diskargs['name']])
                    
                tmpha = deepcopy(hostargs)
                del tmpha['INTERFACES']
                del tmpha['DISKS']

                if 'realhost' in hostargs or \
                   'realhosts' not in lanargs:
                    realmachine = self.__realmachines[hostargs.get('realhost')]
                elif 'realhosts' in lanargs:
                    realmachine = self.__realmachines[lanargs['realhosts'].split(',')[0]]

                vm = VM( realmachine, \
                     hostname, \
                     networks=networks, \
                     disks=disks, \
                     macaddr=[VM.macs.next() for i in hostargs['INTERFACES']] + [VM.macs.next()], \
                     **tmpha)

                # add vm's IPs and realmachines to the network
                network.add_realmachine(self.__realmachines[hostargs.get('realhost')])
                for ifargs in hostargs['INTERFACES'].values():
                    cluster[ifargs['network']].add_vm(vm, hostargs['addrs'].split(','))
                    cluster[ifargs['network']].add_realmachine(self.__realmachines[hostargs.get('realhost')])
                    
        # create all interface helpers
        for helper in self['HELPERS']:
            helpername, helperargs = helper.items()[0]
            if helpername == 'interface':
                from pyVC.Helpers.Interface import Helper as Interface

                tmpha = deepcopy(helperargs)

                networks = [cluster[netname] for netname in tmpha.get('networks').split(',')]

                if 'realhost' in tmpha:
                    realmachine = self.realmachines[tmpha['realhost']]
                    del tmpha['realhost']
                else:
                    realmachine = networks[0].realmachine

                del tmpha['networks']

                Interface(realmachine, networks, **tmpha)

        # next create all routers
        for helper in self['HELPERS']:
            helpername, helperargs = helper.items()[0]
            if helpername == 'router':
                from pyVC.Helpers.Router import Helper as Router

                tmpha = deepcopy(helperargs)
                
                networks = [cluster[netname] for netname in tmpha.get('networks').split(',')]

                if 'realhost' in tmpha:
                    realmachine = self.realmachines[tmpha['realhost']]
                    del tmpha['realhost']
                else:
                    realmachine = network.realmachine

                del tmpha['networks']
                
                Router(realmachine, networks, **tmpha)
                    
        # finally create DHCP helpers
        for helper in self['HELPERS']:
            helpername, helperargs = helper.items()[0]
            if helpername == 'dhcp':
                from pyVC.Helpers.DHCP import Helper as DHCP

                tmpha = deepcopy(helperargs)

                networks = [cluster[netname] for netname in tmpha.get('networks').split(',')]

                if 'realhost' in tmpha:
                    realmachine = self.realmachines[tmpha['realhost']]
                    del tmpha['realhost']
                else:
                    realmachine = networks[0].realmachine

                del tmpha['networks']
               
                server = DHCP(realmachine, networks, **tmpha)
             
        self.__cluster = cluster.values()
        return self.__cluster
    
    def start(self):
        """Starts the virtual cluster in the specification"""

        from pyVC.Helpers import Interface, Router, DHCP
        
        started_vms = []
        
        for network in self.__cluster:
            network.start()

        for network in self.__cluster:
            for host in network.vms:
                if host not in  started_vms:
                    host.start()     
                    started_vms.append(host)
            for helper in network.helpers:
                if isinstance(helper, Interface.Helper) and helper.status != 'started':
                    helper.start()
            for helper in network.helpers:
                if isinstance(helper, Router.Helper) and helper.status != 'started':
                    helper.start()

        for network in self.__cluster:
            for helper in network.helpers:
                if isinstance(helper, DHCP.Helper) and helper.status != 'started':
                    helper.start()

    def status(self):
        """Returns the status of a specified cluster"""
        return_string = ""
        for network in self.__cluster:
            (networkstatus, hosts) = network.status()
            return_string += "%s: %s\n" % (network, networkstatus)
            for hostname, hoststatus in hosts:
                return_string += "  %s: %s\n" % (hostname, hoststatus)
        return return_string
    
    def stop(self):
        """Stops the virtual cluster in the specification"""
        for network in self.__cluster:
            for host in network.vms:
                host.stop()        
            for helper in network.helpers:
                helper.stop()
        
        for network in self.__cluster:
            network.stop()
            
    def _get_cluster(self):
        """Returns the cluster object"""
        return self.__cluster

    def _get_realmachines(self):
        """Returns the value of self.__realmachines"""
        return self.__realmachines

    def add_realmachine(self, newmachine):
        """Adds a system to self.__realmachines"""

        self.__realmachines[newmachine.hostname] = newmachine

    def remove_realmachine(self, machinename):
        """Removes a system from self.__realmachines"""

        if machinename in self.__realmachines.keys():
            self.__realmachines[machinename] = False

    cluster = property(_get_cluster)
    realmachines = property(_get_realmachines)

    # Abstract methods

    def load(self):
        """Loads the configuration into the internal dictionary"""
        raise NotImplementedError

    def create_ip(self, lan):
        """Creates a valid IP inside LAN"""
        raise NotImplementedError
