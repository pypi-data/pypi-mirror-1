#!/usr/bin/env python2.4 -i

from pyVC.Machine import Machine
from pyVC.Networks.Multicast import Network as Multicast
from pyVC.VirtualMachines.QEMU import VM as QEMU
from pyVC.Disks.Image import Disk as Image

localhost = Machine()
lan1 = Multicast([localhost], "lan1")
root = Image([localhost], imagefile = "/Users/zach/pyvc/images/image.img")
qemu1 = QEMU(localhost, "qemu1", networks = [lan1], disks = [root], macaddr=[QEMU.macs.next()])
qemu2 = QEMU(localhost, "qemu2", networks = [lan1], disks = [root], macaddr=[QEMU.macs.next()])

lan1.start()
qemu1.start()
qemu2.start()
