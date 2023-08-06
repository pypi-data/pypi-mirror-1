# -*- coding: utf-8 -*-
"""
This module contains the tool of topp.recipes.cfgtemplate
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1.0'

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
    read('topp', 'recipes', 'cfgtemplate', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )
entry_point = 'topp.recipes.cfgtemplate:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='topp.recipes.cfgtemplate',
      version=version,
      description="Provides template substitution for other recipe configurations in the same buildout.cfg file.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='buildout',
      author='Rob Miller',
      author_email='robm@openplans.org',
      url='http://topp.openplans.org/',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['topp', 'topp.recipes'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'topp.recipes.cfgtemplate.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
