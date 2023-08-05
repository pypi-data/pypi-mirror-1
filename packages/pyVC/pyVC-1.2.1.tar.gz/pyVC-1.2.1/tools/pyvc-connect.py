#!/usr/bin/python2.4 -i

from getopt import getopt, GetoptError
from sys import argv, exit

import Pyro.core

host = "localhost"
port = "7766"
object = "pyvcd"

def usage ():
    print "%s [-h hostname] [-p port]" % (argv[0])
    exit(-1)

try: 
    optlist, otherlist = getopt(argv[1:], 'p:h:')
except GetoptError:
    usage()

for opt in optlist:
    if opt[0] == '-h':
        host = str(opt[1])
    if opt[0] == '-p':
        port = str(opt[1])

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (host, port, object)
pyvcd = Pyro.core.getAttrProxyForURI(uri)

print pyvcd.machines
