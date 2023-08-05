# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.linktally
"""
import os
from setuptools import setup, find_packages
from collective.recipe import linktally

version = linktally.VERSION

README = os.path.join(linktally.__path__[0],
                      'docs', 'README.txt')

long_description = open(README).read() + '\n\n'

entry_point = ''
entry_points = { 'zc.buildout':
                 ['default = collective.recipe.linktally:Recipe'],
                 }

setup(name='collective.recipe.linktally',
      version=version,
      description="zc.buildout recipe for setting up linktally",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='buildout linktally',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='https://svn.plone.org/svn/collective/buildout/collective.recipe.linktally/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zope.testing',
                        'zc.buildout',
                        'plone.recipe.distros',
                        'zc.recipe.egg',
                        ],
      entry_points=entry_points,
      )
