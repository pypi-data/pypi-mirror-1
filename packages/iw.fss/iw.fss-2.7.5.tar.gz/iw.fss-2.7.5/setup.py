# -*- coding: utf-8 -*-
# Copyright (c) 2008 'Ingeniweb'

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
This module contains the tool of iw.fss
"""
import os
from setuptools import setup, find_packages
from xml.dom import minidom

metadata_file = os.path.join(os.path.dirname(__file__),
                             'iw', 'fss',
                             'profiles', 'default', 'metadata.xml')
metadata = minidom.parse(metadata_file)
version = metadata.getElementsByTagName("version")[0].childNodes[0].nodeValue
version = str(version).strip()

README = os.path.join(os.path.dirname(__file__),
                      'iw', 'fss', 'README.txt')

long_description = open(README).read() + '\n\n'

tests_require = [
        'zope.testing',
    ]

setup(name='iw.fss',
      version=version,
      description="Archetypes storage for storing fields raw values on the file system.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='fss plone',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://svn.plone.org/svn/collective/iw.fss/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw'],
      include_package_data=True,
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "iw.fss.tests.test_fssdocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

