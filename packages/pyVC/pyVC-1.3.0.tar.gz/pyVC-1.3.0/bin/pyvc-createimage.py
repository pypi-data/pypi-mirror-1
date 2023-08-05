#!/usr/bin/env python2.4

from subprocess import Popen, PIPE
from getopt import getopt, GetoptError
from os import getuid, waitpid, system, chmod, getpid, remove
from sys import argv, exit
from pyVC import Config

target = "/mnt"

preinstall = """#!/bin/sh
mkdir -p /mnt/etc
cat > /mnt/etc/kernel-img.conf <<EOF
do_symlinks = yes
relative_links = yes
do_bootloader = no
do_bootfloppy = no
do_initrd = yes
EOF
cat > /mnt/etc/fstab <<EOF
# /etc/fstab: static file system information.
#
#<file sys>          <mount point>     <type>   <options>   <dump>   <pass>
/dev/hda1   /   ext3    rw  0   1
/dev/hda2   none    swap    rw  0   0
none    /proc   proc    defaults    0   0
none    /proc/bus/usb   usbdevfs    defaults
EOF
"""

postinstall = """#!/bin/sh
echo %s > /mnt/etc/hostname
cat > /mnt/etc/network/interfaces <<EOF
    auto lo eth0
    iface lo inet loopback
    iface eth0 inet static
      address $IPADDR
      netmask $NETMASK
      broadcast $BROADCAST
      gateway $GATEWAYS
EOF
mkdir /mnt/boot/grub
chroot /mnt update-grub -y
"""

def usage ():
  print argv[0]
  print "options:"
  print "  <-v> verbose"
  print "  <-h> help"
  print "  <-f> filename"
  print "  <-s> size"
  print "  <-S> swap size"
  print "  <-m> mirror site"
  print "  <-k> kernel version"
  print "  <-n> hostname"
  exit(0)

config = Config()
filename = "image.img"
size = "512M"
hostname = ""
swapsize = 128
mirrorsite = "http://ftp.us.debian.org/debian"
kernelversion="2.6.8-2-386"

if (getuid() != "root"):
  print 'WARNING: Not running as root, please have sudo configured as documented'
  sudo_prefix = config['global']['sudo_executable']
else:
  sudo_prefix = ""

try:
    optlist, othrlist = getopt(argv[1:], 'vhf:s:S:m:k:n:')
except GetoptError:
  usage()

for opt in optlist:
  if opt[0] == '-h':
    usage()
  if opt[0] == '-v':
    verbose = bool(1)
  if opt[0] == '-f':
    filename = opt[1]
  if opt[0] == '-s':
    size = opt[1]
  if opt[0] == '-S':
    swapsize = int(opt[1])
  if opt[0] == '-m':
    mirrorsite = opt[1]
  if opt[0] == '-k':
    kernelversion = opt[1]
  if opt[0] == '-n':
    hostname = opt[1]
    
print "### Creating Disk Image ###"
p = Popen(config['qemu']['qemu_img_executable'] + " create -f raw /tmp/%s %s" % (filename, size), shell=True, stdout=PIPE)
sts = waitpid(p.pid, 0)

sizemb = int(p.stdout.readline().replace(" kB", "").rsplit("size=")[1])/1024
swapstart = sizemb-swapsize

print "### Partitioning Disk ###"
#system("%s /sbin/parted -s /tmp/%s mklabel msdos" % (sudo_prefix, filename))
#system("%s /sbin/parted -s /tmp/%s mkpartfs primary ext2 0 %s" % (sudo_prefix, filename, swapstart))
#system("%s /sbin/parted -s /tmp/%s mkpartfs primary linux-swap %s %s" % (sudo_prefix, filename, swapstart, sizemb))

print "### Setting Up Filesystem ###"
p = Popen("%s losetup -f" % (sudo_prefix), shell=True, stdout=PIPE)
sts = waitpid(p.pid, 0)
lodevice = p.stdout.readline().rstrip()

system("%s losetup -o 32256 -f /tmp/%s" % (sudo_prefix, filename))
system("%s mke2fs -q -m 0 -j %s" % (sudo_prefix, lodevice))
system("%s losetup -d %s" % (sudo_prefix, lodevice))

print "### Setting Up Loopback Device ###"
p = Popen("%s losetup -f" % (sudo_prefix), shell=True, stdout=PIPE)
sts = waitpid(p.pid, 0)
lodevice = p.stdout.readline().rstrip()

system("%s losetup -f /tmp/%s" % (sudo_prefix, filename))

print "### Mounting Disk Image Filesystem ###"
system("%s mount -o loop -t ext3 /tmp/%s /mnt" % (sudo_prefix, filename))

print "### Running Preinstall ###"
pre_script = open('/tmp/%s.preinstall' % (getpid()), 'w+')
pre_script.writelines(preinstall)
pre_script.flush()
chmod(pre_script.name, 0755)
system("%s /bin/sh %s" % (sudo_prefix, pre_script.name))
remove(pre_script.name)
del pre_script

system("%s debootstrap --arch i386 --include=module-init-tools,ssh,cramfsprogs,dash,initrd-tools,kernel-image-%s,grub --exclude=lilo sarge /mnt %s" % (sudo_prefix, kernelversion, mirrorsite))

print "### Running Postinstall ###"
post_script = open('/tmp/%s.postinstall' % (getpid()), 'w+')
post_script.writelines(postinstall)
post_script.flush()
chmod(post_script.name, 0755)
system("%s /bin/sh %s" % (sudo_prefix, post_script.name))
remove(post_script.name)
del post_script

#print "### Installing GRUB ###"
#device_map = open('/mnt/boot/grub/device.map' % (getpid()), 'w+')
#device_map.writeline("(hd0) %s" % lodevice)
#device_map.flush()
#system("%s /mnt/sbin/grub-install --device-map=%s --root-directory=/mnt %s" % (sudo_prefix, device_map.name, lodevice))
#remove(device_map.name)
#del device_map

print "### Cleaning Up ###"
system("%s losetup -d %s" % (sudo_prefix, lodevice))
system("%s umount /mnt" % (sudo_prefix))
