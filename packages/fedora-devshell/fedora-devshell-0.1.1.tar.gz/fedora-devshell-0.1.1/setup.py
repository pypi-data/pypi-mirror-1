#!/usr/bin/env python

from setuptools import setup, find_packages

import devshell.modules as ms
from devshell.base.module import Module
from inspect import isclass
from functools import partial
from devshell.base.util import flip

d = ms.__dict__
modules = filter(partial(flip(issubclass), Module), filter(isclass, d.values()))


setup(name='fedora-devshell',
      version='0.1.1',
      description='Fedora Developer\'s Lunchbox',
      long_description=
'''Fedora Devshell is a collection of tools to integrate the various tasks of a Fedora developer and packager.''',
      author='Yaakov M. Nemoy',
      author_email='devshell@hexago.nl',
      url='https://fedoraproject.org/wiki/Devshell',
      license='GPLv2+',

      packages=find_packages(),
      include_package_data=True,
      install_requires=['ConfigObj>=4.5.3', 'python-dateutil'],
      entry_points = {
        'console_scripts': [
            'devshell = devshell.devshell:main',
            'ports = devshell.ports:main',
            ],
        'devshell.modules': ['%(point)s = %(module)s:%(name)s' %
                             dict(point=x.__name__.lower(),
                                  module=x.__module__,
                                  name=x.__name__) for x in modules],
        },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Shells'],
      )
