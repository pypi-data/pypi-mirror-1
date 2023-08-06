# -*- coding: utf-8 -*-
"""
This module contains the tool of quintagroup.pingtool
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    
setup(name='quintagroup.pingtool',
      version=read("quintagroup", "pingtool", "version.txt"),
      description="quintagroup.pingtool is a simple tool to enable pinging of external feed agregators for Plone 3.1.x",
      long_description=read("README.txt") + "\n" + \
                       read("docs", "INSTALL.txt")+ "\n" + \
		       read("docs", "HISTORY.txt"),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='liebster',
      author_email='support@quintagroup.com',
      url='http://quintagroup.com/services/plone-development/products/ping-tool',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
