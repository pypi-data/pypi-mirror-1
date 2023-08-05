from ez_setup import use_setuptools
from os import curdir

use_setuptools(to_dir=curdir + "/eggs")

from glob import glob
from setuptools import setup

PACKAGE = 'pyVC'
VERSION = '1.2.1'
SUMMARY = "A set of Python tools for virtual cluster computing",
DESCRIPTION = """\
pyVC is a free, open-source system that facilitates in the creation, desctuction, and control of Virtual Machines and Virtual Networks. The 'VC' in the name stands for 'Virtual Clusters', which is what the system was originally designed for. However, you can use pyVC for anything from a single VM running on a single machine to dozens of VMs running on dozens of real machines.

pyVC consists of 3 distinct parts:

  * a programmatic interface (in Python) for control over every component used in the creation of a Virtual Cluster.
  * a built-in XML specification language for description of your Virtual Cluster. This language is called VCML.
  * a set of client programs and a daemon to control the Virtual Cluster. 

pyVC is designed to be highly extensible, and once the core framework was written and finalized, the support for the various tools was completed in a matter of days, not hours. Each component of the virtual system is a separate Python object with a consistent object-oriented interface. This allows the virtual network to be controlled with the provided tools, or with pure Python code. 

Currently, pyVC supports QEMU, UML, and Xen virtualization systems, with more to come. Networking is provided by VDE1, Linux TAP and Bridge interfaces, and the user-mode and multicast network stacks provided by UML, Xen, and QEMU. An interface to a DHCP server is also provided, along with the ability to control host interfaces and configure basic IPtables NAT for the virtual network. pyVC also supports virtual networks that span multiple 'real' machines, so you can test your system on a single system before using it on a larger cluster. Since all of the network configuration information is stored in an XML specification (but could easily be stored in other formats, provided a new parser was written), switching your network between network types and virtualization types is as simple as editing the specification.
"""

setup(
        name = PACKAGE,
        version = VERSION,
        license = "BSD",
        platforms = "POSIX",
        keywords = "virtualization qemu uml vde xen vcml xml pyro cluster hpc",
        description = SUMMARY,
        long_description = DESCRIPTION.strip(),
        classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Emulators'],
        url = "http://www.cs.mtsu.edu/pyvc",
        download_url = "http://cheeseshop.python.org/pypi/pyVC",
        author = 'Zach Lowry',
        author_email = 'zach@cs.mtsu.edu',
        zip_safe = True,
	install_requires = ['elementtree>=1.2.6', 'lxml>=1.2.1', 'Pyro>=3.6'],
        dependency_links = ["http://libvirt.org/"],
        packages = ['pyVC', \
                    'pyVC.Disks', \
                    'pyVC.Helpers', \
                    'pyVC.Networks', \
                    'pyVC.VirtualMachines',\
                    'pyVC.Specifications'\
                   ],
        package_dir = {'': 'lib'},
        package_data = {'pyVC': ['vcml.xsd']},
        scripts = ['bin/pyvc-console.py', \
                   'bin/pyvc-createimage.py', \
                   'bin/pyvc-start.py', \
                   'bin/pyvc-stop.py', \
                   'bin/pyvcd.py', \
                   'bin/pyvc-trace.py' \
                  ],
        data_files = [('/etc', ['etc/pyVC.ini']), \
                      ('/usr/share/pyvc/demos/python', glob('demos/python/*.py')), \
                      ('/usr/share/pyvc/demos/single', glob('demos/single/*.xml')), \
                      ('/usr/share/pyvc/demos/multi', glob('demos/multi/*.xml')),
                      ('/usr/share/pyvc', ['lib/pyVC/vcml.xsd']) \
                     ]
     )
