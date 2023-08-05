#!/usr/bin/env python

import sys, os
from distutils.core import setup


long_desc = """DAXFi is a Python package that helps configure several
different kinds of firewalls in a consistent way.

The rules can be described with XML files, XML strings, or generated
directly by the code.

It comes with a Python package, useful to build other applications
aimed to manipulate different firewalls in a homogeneous way and
includes some useful example programs.
"""

classifiers = """\
Development Status :: 4 - Beta
Development Status :: 5 - Production/Stable
Environment :: Console
Environment :: No Input/Output (Daemon)
Environment :: Other Environment
Intended Audience :: Developers
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: English
Operating System :: POSIX
Operating System :: POSIX :: BSD
Operating System :: POSIX :: Linux
Operating System :: POSIX :: Other
Operating System :: POSIX :: SunOS/Solaris
Operating System :: Unix
Programming Language :: Python
Programming Language :: C
Topic :: Security
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Networking :: Firewalls
Topic :: System :: Systems Administration
"""

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key('classifiers'):
            del kwargs['classifiers']
        if kwargs.has_key('download_url'):
            del kwargs['download_url']
        if sys.version_info < (2, 2) and kwargs.has_key('keywords'):
            del kwargs['keywords']
        _setup(**kwargs)


setup(name = 'DAXFi',
      version = '1.1',
      description = 'configure different kinds of firewalls in a consistent way.',
      long_description = long_desc,
      author = 'Davide Alberani',
      author_email = 'da@erlug.linux.it',
      maintainer = 'Davide Alberani',
      maintainer_email = 'da@erlug.linux.it',
      url = 'http://daxfi.sourceforge.net/',
      download_url = 'http://sf.net/project/showfiles.php?group_id=28520',
      license = 'GPL',
      platforms = 'any',
      classifiers = filter(None, classifiers.split("\n")),
      keywords = ['firewall', 'management', 'dynamic', 'configuration', 'linux',
                    'bsd', 'unix', 'iptables', 'ipchains', 'ipfilter',
                    'ipfwadm'],
      package_dir = {'': 'modules'},
      packages = ['daxfi', 'daxfi.firewalls', 'daxfi.firewalls.ipchains',
                    'daxfi.firewalls.ipfilter', 'daxfi.firewalls.iptables',
                    'daxfi.firewalls.ipfwadm'],
      scripts = ['daxfid', 'daxfictl', 'daxfidump', 'daxfixmlfile'])


print ''
print 'Remember that you have to manually copy the etc/daxfid/ directory; i.e.:'
print '\tcp -a etc/daxfid/ /etc/'
print ''

