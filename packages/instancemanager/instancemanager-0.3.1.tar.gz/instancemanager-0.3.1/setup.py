#!/usr/bin/env python
import ez_setup
ez_setup.use_setuptools()

import re
import os
import sys
from setuptools import setup
from setuptools import find_packages

setup(name='instancemanager',
      version='0.3.1',
      license='GPL',
      description='Manager for zope instances',
      long_description="""
      Setting up a zope instance, symlinking to all the products,
      extracting product tarballs, copying over a snapshot Data.fs
      from the customer's website, restarting zope, clicking around in
      the quickinstaller: it can all be done by hand.

      Instancemanager is a handy utility program that manages your
      development zope instances and does all this work for you.

      From 0.4 upwards it also includes good support for your
      server-side needs.
      """,
      keywords="zope plone instances",
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://plone.org/products/instance-manager',
      #packages=['src/instancemanager'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      entry_points={
        'console_scripts':[
            'instancemanager = instancemanager.mainprogram:main'
            ]
        }
      )
