#!/usr/bin/python

from getopt import getopt, GetoptError
from sys import argv, exit
from pyVC.Term import Term

import Pyro.core

host = "localhost"
port = "7766"
vm = None
list = False
object = "pyvcd"
debug = False

def usage ():
    print "%s [-h hostname] [-p port] -v vmname" % (argv[0])
    print "%s [-h hostname] [-p port] -l" % (argv[0])
    exit(-1)

try: 
    optlist, otherlist = getopt(argv[1:], 'p:h:v:ld')
except GetoptError:
    usage()

for opt in optlist:
    if opt[0] == '-h':
        host = str(opt[1])
    if opt[0] == '-p':
        port = str(opt[1])
    if opt[0] == '-v':
        vm = str(opt[1])
    if opt[0] == '-l':
        list = True
    if opt[0] == '-d':
        debug = True

if not vm and not list:
    usage()

if debug:
    Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

Pyro.core.initClient(0)
uri = "PYROLOC://%s:%s/%s" % (host, port, object)

pyvcd = Pyro.core.getAttrProxyForURI(uri)
pyvcd._setOneway('startserver')

try:
    hosts = pyvcd.hosts
except Pyro.errors.ProtocolError, e:
    print "ERROR: Pyro returned \"%s\"." % e
    exit(-1)
except AttributeError:
    print "ERROR: pyvcd needs to be restarted."
    exit(-1)

if list:
    for vm in hosts:
        print vm
else:
    if vm not in hosts:
        print "ERROR: %s not found" % vm
        exit(-1)

    myterm = Term()

    try:
        (consolehost, consoleport) = pyvcd.initserver(vm)
    except RuntimeError, (errno, strerror):
        print strerror
        exit(-1)

    pyvcd.startserver(vm)

    myterm.connect(host = consolehost, port = consoleport)

