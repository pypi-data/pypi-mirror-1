# -*- coding: utf-8 -*-
"""
This module contains the tool of spats
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('spats', 'README.txt')
    + '\n' +
    'Detailed Overview\n'
    '**********************\n'
    + '\n' +
    read('spats', 'docs', 'overview.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' + 
    read('CONTRIBUTORS.txt')
    + '\n' + 
   'Download\n'
    '********\n'
    )

setup(name='spats',
      version=version,
      description="Spats or Simple PAge Template Server is an attempt to make a simple little Page Template Server that can be used by everyone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        ],
      keywords='server template tal',
      author='Sidnei da Silva',
      author_email='sidnei at enfoldsystems dot com',
      url='http://enfoldsystems.com/',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'SimpleTAL',
                        # -*- Extra requirements: -*-
                        ],
      )
