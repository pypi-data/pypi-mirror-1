#!/usr/bin/python2.4

from optparse import OptionParser, OptionGroup
from sys import argv, exit
from pyVC.errors import *

import Pyro.core

object = "pyvcd"

opt = OptionParser()
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

if options.debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (options.hostname, options.port, object)
pyvcd = Pyro.core.getAttrProxyForURI(uri)

rc = "success"
try:
    rc = pyvcd.stop()
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

if rc:
    print rc
