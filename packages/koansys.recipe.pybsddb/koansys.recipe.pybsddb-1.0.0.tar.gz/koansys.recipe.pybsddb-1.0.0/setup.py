# -*- coding: utf-8 -*-
"""
This module contains the tool of koansys.recipe.pybsddb
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0.0'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('koansys', 'recipe', 'pybsddb', 'README.txt')
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
entry_point = 'koansys.recipe.pybsddb:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

name='koansys.recipe.pybsddb'

setup(name=name,
      version=version,
      description="A recipe to build pybsddb",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        ],
      keywords='recipe buildout bdb',
      author='Koansys, LLC',
      author_email='reed@koansys.com',
      url='http://koansys.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['koansys', 'koansys.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'koansys.recipe.pybsddb.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
