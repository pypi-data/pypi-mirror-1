#!/usr/bin/python2.4 -i

from pyVC.Machine import Machine
from pyVC.Networks.VDE1 import Network as VDE1
from pyVC.VirtualMachines.QEMU import VM as QEMU
from pyVC.Disks.Image import Disk as Image

# create machine object on localhost
localhost = Machine()

# create 2 virtual networks
lan1 = VDE1([localhost], "lan1")

# create disk image
root = Image([localhost], imagefile = "/sandbox/image.img")

# create 2 virtual machines
qemu1 = QEMU(localhost, "qemu1", networks = [lan1], disks = [root])
qemu2 = QEMU(localhost, "qemu2", networks = [lan1], disks = [root])

lan1.start()

qemu1.start()
qemu2.start()
