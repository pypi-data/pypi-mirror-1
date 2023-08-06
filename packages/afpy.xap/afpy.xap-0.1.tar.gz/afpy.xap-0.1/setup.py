# -*- coding: utf-8 -*-
# Copyright (C)2008 AFPy

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains the tool of afpy.core
"""
import os
from setuptools import setup, find_packages

version = '0.1'

README = os.path.join(os.path.dirname(__file__),
          'afpy', 'xap', 'README.txt')

README = open(README).read() + '\n\n'
CHANGES = open('CHANGES').read() + '\n\n'

long_description = README + CHANGES

setup(name='afpy.xap',
      version=version,
      description="afpy xapian indexer package",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Python Software Foundation License",
        ],
      keywords='afpy xapian',
      author='Tarek Ziade',
      author_email='tarek@ziade.org',
      url='http://afpy.org',
      license='Python',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['afpy'],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
          'setuptools',
          'zopyx.textindexng3',
          'SQLAlchemy',
          'pysqlite',
          #'psycopg2',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
          'afpy_indexer = afpy.xap.run:main']
       },
      )

