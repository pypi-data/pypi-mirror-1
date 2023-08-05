#!/usr/bin/env python2.4 -i

from pyVC.Machine import Machine
from pyVC.Networks.VDE1 import Network as VDE1
from pyVC.VirtualMachines.QEMU import VM as QEMU
from pyVC.Disks.Image import Disk as Image

localhost = Machine()
lan1 = VDE1([localhost], "lan1")
root = Image([localhost], imagefile = "/sandbox/image.img")
qemu1 = QEMU(localhost, "qemu1", networks = [lan1], disks = [root])

lan1.start()
qemu1.start()
qemu1.console()
