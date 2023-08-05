#!/usr/bin/python2.4 -i

from pyVC.Helpers.IP import Helper as IP
from pyVC.Machine import Machine
from pyVC.Networks.Passthrough import Network as Passthrough

m = Machine()
n = Passthrough([m], "lan1", iface="lo")
ip = IP(m, [n], 'lo', '127.1.1.1, 127.2.2.2')
