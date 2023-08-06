# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.1a1'

setup(name='wsapi4plone.client',
      version=version,
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      description="""An XML-RPC client specially created for interfacing with a Plone site using the Web Services API for Plone (wsapi4plone).""",
      long_description=open("README.txt").read() + "\n" + open("CHANGES.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Framework :: Plone",
                   "Framework :: Zope2",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.4",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Intended Audience :: Developers",
                   "Development Status :: 3 - Alpha",
                   ],
      keywords='wsapi, api, xmlrpc, weblion',
      url='https://weblion.psu.edu/trac/weblion/wiki/WebServicesApiPlone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wsapi4plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'httplib2',
                        ],
      entry_points="""
      # -*- Entry points: -*-
      """,)
