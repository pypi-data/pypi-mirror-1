"""This package contains the classes to implement a VCML specification"""
__revision__ = "$Revision: 227 $"

from pyVC.Specifications import Base

class Specification( Base.Specification ):
    """This object defines a VCML Cluster"""
    __revision__ = "$Revision: 227 $"
    
    def __init__( self, realmachines, configfile ):

        self.load( configfile )
        
        Base.Specification.__init__(self, realmachines)

    def load( self, configfile ):
        """Load the config file into the dictionary"""
        
        from elementtree.ElementTree import parse as etparse
        from lxml.etree import XMLSchema, parse
        from pyVC import Config

        config = Config()

        if 'vcml_schema' in config['pyvc']:
            schemafile = parse( config['pyvc']['vcml_schema'] )
            schema = XMLSchema(schemafile)
            parsedfile = parse( configfile ).getroot()

            if not schema(parsedfile):
                raise ValueError, """%s""" % schema.error_log

        parsedfile = etparse( configfile ).getroot()

        self['NETWORKS'] = {}

        for network in parsedfile.findall( 'network' ):
            if 'name' in network.attrib:
                self['NETWORKS'][network.attrib['name']] = network.attrib
                self['NETWORKS'][network.attrib['name']]['HOSTS'] = {}
                for host in network.findall( 'host' ):
                    if 'name' in host.attrib:
                        self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                        [host.attrib['name']] = host.attrib
                        self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                        [host.attrib['name']]['INTERFACES'] = {}
                        self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                        [host.attrib['name']]['DISKS'] = {}
                        interfaceid = 1
                        diskid = 0
                        for interface in host.findall( 'interface' ):
                            self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                            [host.attrib['name']]['INTERFACES']\
                                            [interfaceid] = interface.attrib
                            interfaceid += 1
                        for disk in host.findall( 'disk' ):
                            self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                            [host.attrib['name']]['DISKS']\
                                            [diskid] = disk.attrib
                            diskid += 1
                        del self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                             [host.attrib['name']]['name']
                del self['NETWORKS'][network.attrib['name']]['name']

        self['HELPERS'] = []
        if parsedfile.find('helpers'):
            for helper in parsedfile.find('helpers').getchildren():
                self['HELPERS'].append({helper.tag: helper.attrib})
        self['DISKS'] = {}
        for disk in parsedfile.findall('disk'):
            if 'name' in disk.attrib and disk.attrib['name'] not in self['DISKS'].keys():
                self['DISKS'][disk.attrib['name']] = disk.attrib
                del self['DISKS'][disk.attrib['name']]['name']

    def create_ip( self, lan ):
        """Creates a valid IP inside LAN"""
        
        addresses = []

        # get all of the currently used IPs in a lan
        for interface in [hostparams['INTERFACES'] for hostparams in self['NETWORKS'][lan]['HOSTS'].values()]:
            if 'addrs' in interface:
                addresses += interface['addrs'].split(',')
                
        for hostparams in self['NETWORKS'][lan]['HOSTS'].values():
            if 'addrs' in hostparams:
                addresses += hostparams['addrs'].split(',')

        if 'addrs' in self['NETWORKS'][lan]:
            addresses += self['NETWORKS'][lan]['addrs'].split(',')

        addresses.sort()

        # a compilcated algorithm to pick the next IP
        if ( len( addresses ) > 1 and \
             int(addresses[-1].split('.')[3]) > \
             int(addresses[-2].split('.')[3])+1):
            highestaddr = addresses[-2].split('.')
        elif len(addresses) == 1:
            highestaddr = addresses[-1].split('.')
        else:
            highestaddr = None

        if highestaddr:
            addrstring = "%s.%s.%s.%s" % \
            ( highestaddr[0], \
              highestaddr[1], \
              highestaddr[2], \
              int( highestaddr[3] )+1 \
            )
        else:
            addrstring = "0.0.0.0"

        return addrstring

