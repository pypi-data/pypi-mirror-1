# -*- coding: utf-8 -*-
"""
This module contains the tool of rcom.recipe.seleniumenv
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
    read('rcom', 'recipe', 'seleniumenv', 'README.txt')
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
entry_point = 'rcom.recipe.seleniumenv:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='rcom.recipe.seleniumenv',
      version=version,
      description="A recipe for setting a ready-to-use selenium RC environment",
      long_description=long_description,
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='selenium rc testing plone ajax recipe',
      author='Santiago Suarez Ordonez',
      author_email='santiycr@rcom.com.ar',
      url='www.rcom.com.ar',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rcom', 'rcom.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'hexagonit.recipe.download',
                        'zc.recipe.egg'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'rcom.recipe.seleniumenv.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
