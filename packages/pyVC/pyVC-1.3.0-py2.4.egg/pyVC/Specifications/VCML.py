##
# Module containing the Specification object for a VCML specification.
##

__revision__ = "$Revision: 282 $"

from pyVC.Specifications import Base

##
# This class defines a Specification object for a VCML specification.
#
# @param realmachines A list of Machine objects to be used in the specification.
# @param configfile A string containing the path to a XML file containing the VCML specification.
class Specification( Base.Specification ):

    __revision__ = "$Revision: 282 $"
    
    def __init__( self, realmachines, configfile ):

        self.load( configfile )
        
        Base.Specification.__init__(self, realmachines)

    def load( self, configfile ):
        """Load the config file into the dictionary"""
        
        from lxml.etree import XMLSchema, parse, XML
        from pkg_resources import resource_string
        from pyVC import Config
        from pyVC.errors import VCMLError

        config = Config()
        schematext = resource_string('pyVC', 'vcml.xsd')

        if 'vcml_schema' in config['pyvc']:
            schemafile = XML( schematext )
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

        parsedfile = parse( configfile ).getroot()

        self['NETWORKS'] = {}

        for network in parsedfile.findall( 'network' ):
            if 'name' in network.attrib:
                self['NETWORKS'][network.attrib['name']] = dict(network.attrib)
                self['NETWORKS'][network.attrib['name']]['HOSTS'] = {}
                for host in network.findall( 'host' ):
                    if 'name' in host.attrib:
                        self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                        [host.attrib['name']] = dict(host.attrib)
                        self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                        [host.attrib['name']]['INTERFACES'] = {}
                        self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                        [host.attrib['name']]['DISKS'] = {}
                        interfaceid = 1
                        diskid = 0
                        for interface in host.findall( 'interface' ):
                            self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                            [host.attrib['name']]['INTERFACES']\
                                            [interfaceid] = dict(interface.attrib)
                            interfaceid += 1
                        for disk in host.findall( 'disk' ):
                            self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                            [host.attrib['name']]['DISKS']\
                                            [diskid] = dict(disk.attrib)
                            diskid += 1
                        del self['NETWORKS'][network.attrib['name']]['HOSTS']\
                                             [host.attrib['name']]['name']
                del self['NETWORKS'][network.attrib['name']]['name']

        self['HELPERS'] = []
        if parsedfile.find('helpers'):
            for helper in parsedfile.find('helpers').getchildren():
                self['HELPERS'].append({helper.tag: dict(helper.attrib)})
        self['DISKS'] = {}
        for disk in parsedfile.findall('disk'):
            if 'name' in disk.attrib and disk.attrib['name'] not in self['DISKS'].keys():
                self['DISKS'][disk.attrib['name']] = dict(disk.attrib)
                del self['DISKS'][disk.attrib['name']]['name']


