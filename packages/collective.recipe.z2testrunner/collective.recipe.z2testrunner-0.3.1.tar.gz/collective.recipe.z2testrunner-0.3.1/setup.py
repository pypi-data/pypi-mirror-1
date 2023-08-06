# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.z2testrunner
"""
import os
from setuptools import setup, find_packages

version = '0.3.1'

PATH = os.path.join(os.path.dirname(__file__),
                      'collective',
                      'recipe',
                      'z2testrunner',)
README = os.path.join(PATH, 'README.txt')
CHANGES = os.path.join(PATH, 'CHANGES.txt')

long_description = open(README).read() + '\n\n' + open(CHANGES).read() + '\n\n'

entry_points = {'zc.buildout':
                ['default = collective.recipe.z2testrunner:Recipe']}

setup(name='collective.recipe.z2testrunner',
      version=version,
      description="zc.buildout recipe for generating zope2-based test runner",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Environment :: Console",
        "Framework :: Zope2",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent ",
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
                        'zc.buildout',
                        'zc.recipe.egg',
                        # -*- Extra requirements: -*-
                        ],
      entry_points=entry_points,
      )
