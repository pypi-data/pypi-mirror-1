#!/usr/bin/python2.4

from getopt import getopt, GetoptError
from sys import argv, exit
from pyVC.Machine import MachineError

import Pyro.core

host = "localhost"
port = "7766"
object = "pyvcd"
config = None
debug = False

def usage ():
    print "%s [-h hostname] [-p port] -c configfile" % (argv[0])
    exit(-1)

try: 
    optlist, otherlist = getopt(argv[1:], 'p:h:c:d')
except GetoptError:
    usage()

for opt in optlist:
    if opt[0] == '-h':
        host = str(opt[1])
    if opt[0] == '-p':
        port = str(opt[1])
    if opt[0] == '-c':
        config = str(opt[1])
    if opt[0] == '-d':
        debug = True

if not config:
    print "ERROR: -c option must be supplied."
    usage()

if debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (host, port, object)
pyvcd = Pyro.core.getAttrProxyForURI(uri)

try:
    pyvcd.start(config)
except MachineError, e:
    print "## %s ##" % e.hostname
    print e.value
except ValueError, e:
    print "## XML Error ##"
    print e[0]
except Pyro.errors.ProtocolError, e:
    print "ERROR: Pyro returned \"%s\"." % e
except AttributeError:
    print "ERROR: pyvcd needs to be restarted."
