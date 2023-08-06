# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.z2testrunner
"""
import os
from setuptools import setup, find_packages

version = '0.2'

README = os.path.join(os.path.dirname(__file__),
                      'collective',
                      'recipe',
                      'z2testrunner', 'README.txt')

long_description = open(README).read() + '\n\n'

entry_points = {'zc.buildout':
                ['default = collective.recipe.z2testrunner:Recipe']}

setup(name='collective.recipe.z2testrunner',
      version=version,
      description="zc.buildout recipe for generating zope2-based test runner",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://svn.plone.org/svn/collective/buildout/collective.recipe.z2testrunner',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['setuptools',
                        'zope.testing',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      entry_points=entry_points,
      )
