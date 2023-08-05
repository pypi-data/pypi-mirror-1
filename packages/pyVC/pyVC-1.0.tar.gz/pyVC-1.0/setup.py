from setuptools import setup
from glob import glob

PACKAGE = 'pyVC'
VERSION = '1.0'
SUMMARY = "A set of Python tools for virtual cluster computing",
DESCRIPTION = """\
pyVC is a free, open-source system that facilitates in the creation, desctuction, and control of Virtual Machines and Virtual Networks. The 'VC' in the name stands for 'Virtual Clusters', which is what the system was originally designed for. However, you can use pyVC for anything from a single VM running on a single machine to dozens of VMs running on dozens of real machines.

pyVC consists of 3 distinct parts:

        * a programmatic interface (in Python) for control over every component used in the creation of a Virtual Cluster.
        * a built-in XML specification language for description of your Virtual Cluster. This language is called VCML.
        * a set of client programs to control the Virtual Cluster. 
"""

setup(
        name = PACKAGE,
        version = VERSION,
        license = "BSD",
        platforms = "POSIX",
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
        author = 'Zach Lowry',
        author_email = 'zach@cs.mtsu.edu',
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
                   'bin/pyvc-status.py', \
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
