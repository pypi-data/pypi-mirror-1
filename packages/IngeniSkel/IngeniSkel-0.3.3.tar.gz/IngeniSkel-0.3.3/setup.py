# -*- coding: utf-8 -*-
## Copyright (C)2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Setup definitions
"""
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import sys, os

version = '0.3.3'

setup(name='IngeniSkel',
      version=version,
      description="A collection of skeletons for quickstarting projects with Ingeniweb products.",
      long_description="""
A collection of skeletons for quickstarting Ingeniweb Zope projects.
""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope command-line skeleton project',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/IngeniSkel',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      test_suite = "tests.test_ingeniskeldocs.test_suite",
      install_requires=[
        "ZopeSkel",
        "Sphinx",
        "zc.buildout",
        "lovely.buildouthttp",
        "buildout.dumppickedversions"
      ],
      entry_points="""
      [paste.paster_create_template]
      iw_plone_project = ingeniskel:IWPloneProject
      """,
      )

