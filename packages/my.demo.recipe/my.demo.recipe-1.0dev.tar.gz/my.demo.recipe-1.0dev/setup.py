# -*- coding: utf-8 -*-
"""
This module contains the tool of my.demo.recipe
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('my', 'demo', 'recipe', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )
entry_point = 'my.demo.recipe:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='my.demo.recipe',
      version=version,
      description="a demo recipe for oscon",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='demo buildout',
      author='Tarek',
      author_email='tarek@ziade.org',
      url='http://ziade.org',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['my', 'my.demo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'my.demo.recipe.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
