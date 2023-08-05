#!/usr/bin/python

from getopt import getopt, GetoptError
from sys import argv, exit

import Pyro.core

host = "localhost"
port = "7766"
object = "pyvcd"
debug = False

def usage ():
    print "%s [-h hostname] [-p port]" % (argv[0])
    exit(-1)

try: 
    optlist, otherlist = getopt(argv[1:], 'p:h:d')
except GetoptError:
    usage()

for opt in optlist:
    if opt[0] == '-h':
        host = str(opt[1])
    if opt[0] == '-p':
        port = str(opt[1])
    if opt[0] == '-d':
        debug = True

if debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (host, port, object)
pyvcd = Pyro.core.getAttrProxyForURI(uri)

try:
    status = pyvcd.status()
except Pyro.errors.ProtocolError, e:
    print "ERROR: Pyro returned \"%s\"." % e
    exit(-1)
except AttributeError:
    print "ERROR: pyvcd needs to be restarted."
    exit(-1)

print status
