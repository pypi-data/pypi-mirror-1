# -*- coding: utf-8 -*-
"""
This module contains the tool of plone.recipe.haproxy
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0b2'

long_description = (
    read('README.txt')
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )
entry_point = 'plone.recipe.haproxy:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='plone.recipe.haproxy',
      version=version,
      description="Buildout recipe to install haproxy",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='buildout haproxy proxy loadbalancer',
      author='Helge Tesdal',
      author_email='tesdal@jarn.com',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'plone.recipe.haproxy.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
