#!/usr/bin/python2.4 -i

from pyVC.Networks.VDE1 import Network as VDE1
from pyVC.Disks.Image import Disk as Image
from pyVC.VirtualMachines.QEMU import VM as QEMU
from pyVC.Specifications.VCML import Specification as VCML
from sys import argv

spec = VCML(argv[1])
network = spec.create(QEMU, VDE1, Image)
spec.start()
