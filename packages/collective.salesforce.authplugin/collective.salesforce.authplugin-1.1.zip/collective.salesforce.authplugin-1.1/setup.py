# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.omelette
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1'

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

setup(name='collective.salesforce.authplugin',
      version=version,
      description="Using the architecture of Zope's Pluggable Authentication Service and PlonePAS, Salesforce \
        Auth Plugin provides the infrastructure to manage site users as arbitrary objects within a \
        Plone portal.",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='Zope CMF Plone Salesforce.com CRM PAS authentication',
      author='Plone/Salesforce Integration Group',
      author_email='plonesf@googlegroups.com',
      url='http://groups.google.com/group/plonesf',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.salesforce'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'beatbox>=16.0dev',
          'Products.salesforcebaseconnector>=1.2b1',
      ],
      )
