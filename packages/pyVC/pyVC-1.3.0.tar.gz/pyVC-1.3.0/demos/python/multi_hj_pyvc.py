#!/usr/bin/python2.4 -i

from getopt import getopt, GetoptError
from sys import argv, exit

from pyVC.Networks.VDE1 import Network as VDE1
from pyVC.VirtualMachines.QEMU import VM as QEMU
from pyVC.Disks.Image import Disk as Image
from pyVC.Helpers.DHCP import Helper as DHCP
from pyVC.Helpers.Interface import Helper as Interface
from pyVC.Helpers.Router import Helper as Router

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

# create 2 networks and attach them to all real machines
lan1 = pyvcd.add_network("vde1", pyvcd.machinenames, "lan1")
lan2 = pyvcd.add_network("vde1", pyvcd.machinenames, "lan2")

pyvcd.network(lan1.lanname).start()
pyvcd.network(lan2.lanname).start()

# create disk image
root = Image([localhost], path = "/sandbox/image.img")

# create 2 virtual machines
qemu1 = pyvcd.add_vm("qemu", pyvcd.machinenames[0], "qemu1", networks = [pyvcd.network(lan1], disks = [root])
qemu2 = pyvcd.add_vm("qemu", pyvcd.machinenames[-1], "qemu2", networks = [lan1,lan2], disks = [root])

# create helpers
dhcp = pyvcd.helper("dhcp", pyvcd.machinenames[0], [lan1])
router = pyvcd.helper("router", pyvcd.machinenames[0], [lan1])
interface1 = pyvcd.helper("interface", pyvcd.machinenames[0], [lan1], "192.168.1.1")
interface2 = pyvcd.helper("interface", pyvcd.machinenames[0], [lan2], "192.168.2.1")

interface1.start()
interface2.start()

dhcp.start()
router.start()

qemu1.start()
qemu2.start()




