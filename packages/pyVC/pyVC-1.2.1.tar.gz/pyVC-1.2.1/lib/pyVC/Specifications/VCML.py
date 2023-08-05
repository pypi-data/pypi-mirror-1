"""This package contains the classes to implement a VCML specification"""
__revision__ = "$Revision: 250 $"

from pyVC.Specifications import Base

class Specification( Base.Specification ):
    """This object defines a VCML Cluster"""
    __revision__ = "$Revision: 250 $"
    
    def __init__( self, realmachines, configfile ):

        self.load( configfile )
        
        Base.Specification.__init__(self, realmachines)

    def load( self, configfile ):
        """Load the config file into the dictionary"""
        
        from elementtree.ElementTree import parse as etparse
        from lxml.etree import XMLSchema, parse
        from pyVC import Config
        from pyVC.errors import VCMLError

        config = Config()

        if 'vcml_schema' in config['pyvc']:
            schemafile = parse( config['pyvc']['vcml_schema'] )
            schema = XMLSchema(schemafile)
            parsedfile = parse( configfile )

            rc = None
            try:
                rc = schema(parsedfile)
            except TypeError:
                rc = schema.validate(parsedfile)
            if not rc:
                raise VCMLError, ( "ERROR: Failed schema validation.", \
                                   0, \
                                   """%s""" % schema.error_log, \
                                 )

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


