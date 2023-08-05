#!/usr/bin/python2.4

from optparse import OptionParser, OptionGroup
from sys import argv, exit
from pyVC.Term import Term
from pyVC.errors import *

import Pyro.core

vm = None
object = "pyvcd"

usage = """pyvc-console.py [options] -l
       pyvc-console.py [options] vmname"""
opt = OptionParser(usage=usage)
opt.add_option( '-l', '--list', action='store_true', \
                dest='list', \
                help='list VMs on a cluster' )
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
  vm = args[0]
elif not options.list:
  print "ERROR: either --list or a vmname is required."
  opt.print_help()
  exit(-1)

if options.debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (options.hostname, options.port, object)

pyvcd = Pyro.core.getAttrProxyForURI(uri)
pyvcd._setOneway('startserver')

try:
    hosts = pyvcd.hosts
except PyvcError, e:
    print "## %s ##" % e.hostname
    print e.value
    exit(-1)
except Pyro.errors.ProtocolError, e:
    print "ERROR: Pyro returned \"%s\"." % e
    if debug:
        raise
    else:
        exit(-1)
except Pyro.errors.NoModuleError, e:
    print "ERROR: " + e.args[0]
    exit(-1)


if options.list:
    for vm in hosts:
        print vm
else:
    if vm not in hosts:
        print "ERROR: %s not found" % vm
        exit(-1)

    myterm = Term()

    try:
        (consolehost, consoleport) = pyvcd.initserver(vm)
    except PYVCDError, e:
        print e.value
        exit(-1)

    pyvcd.startserver(vm)

    myterm.connect(host = consolehost, port = consoleport)

