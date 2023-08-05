#!/usr/bin/env python

from setuptools import setup

setup(name='cisco_decrypt',
      version='0.8.3',
      description='decrypt Cisco Type 7 passwords',
      author='David Michael Pennington',
      author_email='mike /|at|\ pennington.net',
      license='GPL',
      keywords='Decrypt IOS Type 7 password',
      url='http://www.pennington.net/py/cisco_decrypt/',
      entry_points = "",
      packages= ['cisco_decrypt'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Information Technology',
          'Intended Audience :: Telecommunications Industry',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Communications',
          'Topic :: Internet',
          'Topic :: System :: Networking',
          'Topic :: System :: Networking :: Monitoring',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
     )

