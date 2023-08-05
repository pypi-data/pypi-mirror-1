##
# The base package for pyVC, containing all other modules and packages.
#
# This package contains a universal object that is used by all derived classes, Config. 
# Config reads the pyVC configuration file from /etc/pyVC.ini and ~/.pyVC.ini, in that order. 
# All options in the config file are then stored in the Config object.

__revision__ = "$Revision: 273 $"

__all__ = ['Helpers', 'Networks', 'Specifications', 'VirtualMachines', \
           'Machine', 'Disks']

##
# The per-machine system configuration object.
#
# @exception ValueError could not locate ini file. 
# @exception ValueError could not read the INI value.
class Config( dict ):

    __revision__ = "$Revision: 273 $"

    def __init__(self):
        import ConfigParser
        import os
        
        dict.__init__(self)

        configpaths = ['/etc/pyVC.ini', os.path.expanduser('~/.pyVC.ini')]
    
        config = ConfigParser.SafeConfigParser()
        self.configfiles = tuple(config.read(configpaths))

        if config.sections() == []:
            raise ValueError, ('ERROR: could not locate ini file. \n \
Looked in %s. \n \
Try copying and editing the example in etc/pyVC.ini' % (configpaths))
    
        for section in config.sections():
            if not section in self:
                self[section] = {} 
                
            for option in config.options(section):
                try:
                    self[section][option] = config.get(section, \
                                                       option)
                except ConfigParser.InterpolationSyntaxError:
                    raise ValueError, ('ERROR: could not read the INI value for %s. \n \
Please check the files in %s for any errors.' % (option, self.configfiles))
