#!/usr/bin/python2.4 -i

from pyVC.Term import Term
from sys import argv

t = Term(argv[1])
t.start()
t.connect()
