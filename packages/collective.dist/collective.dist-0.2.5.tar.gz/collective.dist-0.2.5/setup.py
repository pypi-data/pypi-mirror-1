# -*- coding: utf-8 -*-
# Copyright (C) 2008 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
This module contains the tool of iw.dist
"""
import os
from setuptools import setup, find_packages

version = '0.2.5'

README = os.path.join(os.path.dirname(__file__),
          'collective', 'dist', 'docs', 'README.txt')
README = open(README).read() + '\n\n'

#CHANGES = open('CHANGES').read() + '\n\n'
long_description = README #+ CHANGES

setup(name='collective.dist',
      version=version,
      description="Distutils commands to upload files to several servers",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='pypi setuptools distutils',
      author='Tarek Ziade',
      author_email='support@ingeniweb.com',
      url='http://svn.plone.org/svn/collective/collective.dist',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "collective.dist.tests.test_distdocs.test_suite",
      install_requires=[
          'setuptools',
          'docutils'
          # -*- Extra requirements: -*-
      ],
      tests_require=['zope.testing'],
      entry_points = {
         "distutils.commands": [
            "mregister = collective.dist.mregister:mregister",
            "mupload = collective.dist.mupload:mupload",
            "check = collective.dist.check:check"]}
      )

