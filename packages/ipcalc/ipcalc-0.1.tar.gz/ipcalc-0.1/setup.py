#!/usr/bin/env python

from distutils.core import setup

long_description = '''
This module allows you to perform IP subnet calculations, there is support
for both IPv4 and IPv6 CIDR notation.
'''

setup(name='ipcalc',
      version='0.1',
      description='IP subnet calculator',
      long_description=long_description,
      author='Wijnand Modderman',
      author_email='wijnand@wijnand.name',
      url='http://tehmaze.com/code/python/ipcalc/',
      packages=['ipcalc'],
      package_dir={'ipcalc': 'src/ipcalc/'},
     )
