#!/usr/bin/python2.4

from getopt import getopt, GetoptError
from sys import argv, exit
from pyVC.Term import Term

host = "127.0.0.1"
port = "22"

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

t = Term()
t.connect(host = host, port = port)
