# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

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
This module contains the tool of iw.recipe.cmd
"""
import os
from setuptools import setup, find_packages

version = '0.2'

README = os.path.join(os.path.dirname(__file__), 
              'iw',
              'recipe',
              'cmd', 'docs', 'README.txt')

long_description = open(README).read() + '\n\n'

name = 'iw.recipe.cmd'

tests_require=['zope.testing',
              ]

setup(name=name,
      version=version,
      description="ZC Buildout recipe to execute a commande line",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/iw-recipes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw', 'iw.recipe'],
      include_package_data=True,
      zip_safe=False,
      test_suite = "iw.recipe.cmd.tests.test_cmddocs.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          'zc.buildout',
      ],
      entry_points = {"zc.buildout": [
                            "default = %s:Cmd" % name,
                            "sh = %s:Cmd" % name,
                            "py = %s:Python" % name,
                          ]
                       }
      )
