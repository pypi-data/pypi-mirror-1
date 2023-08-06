# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.ant
"""

import os
from setuptools import setup, find_packages

version = '1.0'
name = "collective.recipe.ant"

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (read('collective', 'recipe', 'ant', 'docs', 'README.txt') + '\n' +
          read('CHANGES.txt')
          + '\n' +
          'Contributors\n'
          '***********************\n'
          + '\n' +
          read('CONTRIBUTORS.txt')
          + '\n' +
          'Download\n'
          '***********************\n')

entry_point = '%s:Recipe' % name
entry_points = {"zc.buildout": ["default = %s" % entry_point]}
tests_require = ['zope.testing', 'zc.buildout']

setup(name=name,
      version=version,
      description="zc.buildout recipe for building ant (java) projects",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
       'Framework :: Buildout',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Programming Language :: Python',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='Kai Lautaportti',
      author_email='kai.lautaportti@hexagonit.fi',
      url='http://svn.plone.org/svn/collective/buildout/collective.recipe.ant/',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require = tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = '%s.tests.test_docs.test_suite' % name,
      entry_points=entry_points,
      )
