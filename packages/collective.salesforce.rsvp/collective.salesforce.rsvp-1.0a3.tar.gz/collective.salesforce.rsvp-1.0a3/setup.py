# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.omelette
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0a3'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('docs', 'HISTORY.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='collective.salesforce.rsvp',
      version=version,
      description="RSVP/Event registration system integrating the Plone content management system with \
      the Salesforce.com customer relationship management system.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        ],
      keywords='Zope CMF Plone Salesforce.com CRM registration',
      author='Andrew Burkhalter',
      author_email='andrewb@onenw.org',
      url='http://groups.google.com/group/plonesf',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.salesforce'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'beatbox>=0.9,<=1.0dev',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
