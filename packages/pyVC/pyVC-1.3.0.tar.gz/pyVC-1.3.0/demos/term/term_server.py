#!/usr/bin/python2.4

from pyVC.Term import Term
from sys import argv

t = Term(argv[1])
t.start()

print t.socket()
t.serve()
