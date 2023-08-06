# -*- coding: utf-8 -*-
"""
This module contains the tool of iw.recipe.cmd
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('iw', 'recipe', 'cmd', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )
entry_point = 'iw.recipe.cmd'
entry_points = {"zc.buildout": [
                            "default = %s:Cmd" % entry_point,
                            "sh = %s:Cmd" % entry_point,
                            "py = %s:Python" % entry_point,
                          ]
                       }


tests_require=['zope.testing', 'zc.buildout']

setup(name='iw.recipe.cmd',
      version=version,
      description="ZC Buildout recipe to execute a commande line",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='buildout recipe',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/iw-recipes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw', 'iw.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'iw.recipe.cmd.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
