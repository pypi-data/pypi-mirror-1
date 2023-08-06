# -*- coding: utf-8 -*-
"""
This module contains the tool of mailtoplone.base
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2.7'

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
    read('mailtoplone', 'base', 'README.rst')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='mailtoplone.base',
      version=version,
      description="basic package for mailtoplone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Hans-Peter Locher',
      author_email='hans-peter.locher@inquant.de',
      url='https://svn.plone.org/svn/collective/mailtoplone/mailtoplone.base',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mailtoplone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'icalendar',
          'python-dateutil',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
