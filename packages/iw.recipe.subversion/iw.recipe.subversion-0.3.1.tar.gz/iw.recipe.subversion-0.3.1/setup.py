# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

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
This module contains the tool of iw.recipe.subversion
"""
import os
from setuptools import setup, find_packages

version = '0.3.1'

README = os.path.join(os.path.dirname(__file__),
                      'iw',
                      'recipe',
                      'subversion', 'README.txt')

long_description = open(README).read() + '\n\n'

entry_point = 'iw.recipe.subversion:Recipe'

entry_points = {"zc.buildout": ["default = %s" % entry_point],}

tests_require=['zope.testing',
              ]

setup(name='iw.recipe.subversion',
      version=version,
      description="ZC buildout recipe to checkout a dir from a svn repository and archive it in a folder",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/iw-recipes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw'],
      include_package_data=True,
      zip_safe=False,
      test_suite = "iw.recipe.subversion.tests.test_subversiondocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'zc.buildout',
      ],
      entry_points=entry_points,
      )
