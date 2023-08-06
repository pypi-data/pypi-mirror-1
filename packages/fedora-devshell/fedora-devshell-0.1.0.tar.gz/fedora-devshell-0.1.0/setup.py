#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='fedora-devshell',
      version='0.1.0',
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
            ]
        },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
#         'Operating System :: POSIX :: Fedora',
#         'Operating System :: POSIX :: CentOS',
#         'Operating System :: POSIX :: Red Hat',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Shells'],
      )
