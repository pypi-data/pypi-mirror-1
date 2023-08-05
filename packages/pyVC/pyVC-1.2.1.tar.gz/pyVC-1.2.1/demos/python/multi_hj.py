#!/usr/bin/python2.4 -i

from pyVC.Machine import Machine
from pyVC.Networks.VDE1 import Network as VDE1
from pyVC.VirtualMachines.QEMU import VM as QEMU
from pyVC.Disks.Image import Disk as Image
from pyVC.Helpers.DHCP import Helper as DHCP
from pyVC.Helpers.Interface import Helper as Interface
from pyVC.Helpers.Router import Helper as Router

# create machine object on localhost
localhost = Machine()

# create 2 virtual networks
lan1 = VDE1([localhost], "lan1")
lan2 = VDE1([localhost], "lan2")

# create disk image
root = Image([localhost], path = "/sandbox/image.img")

# create 2 virtual machines
qemu1 = QEMU(localhost, "qemu1", networks = [lan1], disks = [root])
qemu2 = QEMU(localhost, "qemu2", networks = [lan1,lan2], disks = [root])

# create helpers
dhcp = DHCP(localhost, [lan1])
router = Router(localhost, [lan1])
interface1 = Interface(localhost, [lan1], "192.168.1.1")
interface2 = Interface(localhost, [lan2], "192.168.2.1")

interface1.start()
interface2.start()

dhcp.start()
router.start()

lan1.start()
lan2.start()

qemu1.start()
qemu2.start()
