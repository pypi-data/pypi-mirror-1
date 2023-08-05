#!/usr/bin/python

from optparse import OptionParser, OptionGroup
from sys import argv, exit
from pyVC.errors import *

import Pyro.core

object = "pyvcd"
config = None

usage="usage: pyvc-start.py [options] configfile"
opt = OptionParser(usage=usage)
opt.add_option( '-H', '--hostname', action='store', \
                dest='hostname', type='string', default='localhost', \
                help='pyvcd hostname or IP to connect to' )
opt.add_option( '-p', '--port', action='store', \
                dest='port', type='string', default='7766', \
                help='pyvcd port number to connect to' )
opt.add_option( '-D', '--debug', action='store_true', \
                dest='debug', \
                help='enable debug options' )
(options, args) = opt.parse_args()

if len(args) > 0:
  config = args[0]

if not config:
    print "ERROR: no configuration file specified."
    opt.print_help()
    exit(-1)

if options.debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (options.hostname, options.port, object)
pyvcd = Pyro.core.getAttrProxyForURI(uri)

try:
    pyvcd.start(config)
except VCMLError, e:
    print "## VCML Error ##"
    print e.value
    print e.error_log
    exit(-1)
except VMError, e:
    print "## %s ##" % e.hostname
    print e.value, e.vmname
    exit(-1)
except NetworkError, e:
    print "## %s ##" % e.hostname
    print e.value, e.networkname
    exit(-1)
except PyvcError, e:
    print "## %s ##" % e.hostname
    print e.value
    exit(-1)
except Pyro.errors.ProtocolError, e:
    print "ERROR: Pyro returned \"%s\"." % e
    if options.debug:
        raise
    else:
        exit(-1)
except Pyro.errors.NoModuleError, e:
    print "ERROR: " + e.args[0]
    exit(-1)
