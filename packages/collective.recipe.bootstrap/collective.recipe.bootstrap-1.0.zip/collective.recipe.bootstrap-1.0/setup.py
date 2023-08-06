# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.bootstrap
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0'

long_description = (
    read('README.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    read('CHANGES.txt')
    )
entry_point = 'collective.recipe.bootstrap:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='collective.recipe.bootstrap',
      version=version,
      description="This recipe makes it easy to keep your buildout's bootstrap.py file up to date.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='buildout',
      author='Alex Clark',
      author_email='aclark@aclark.net',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.recipe.bootstrap.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
