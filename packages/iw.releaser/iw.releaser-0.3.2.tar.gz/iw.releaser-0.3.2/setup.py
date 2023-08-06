# -*- coding: utf-8 -*-
# Copyright (C)2007 'Ingeniweb'

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
This module contains the tool of iw.releaser
"""
import os
from setuptools import setup, find_packages

version = '0.3.2'

README = os.path.join(os.path.dirname(__file__),
                      'iw', 'releaser', 'docs', 'README.txt')

long_description = open(README).read() + '\n\n'

setup(name='iw.releaser',
      version=version,
      description="Setuptools extension to release an egg",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='egg setuptools extension',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='https://ingeniweb.svn.sourceforge.net/svnroot/ingeniweb/iw.releaser',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw'],
      include_package_data=True,
      zip_safe=False,
      # uncomment this to be able to run tests with setup.py
      #test_suite = "iw.releaser.tests.test_releaserdocs.test_suite",
      install_requires=[
          'setuptools',
          'zc.buildout',
          # -*- Extra requirements: -*-
          'iw.dist',
      ],
      tests_require=['zope.testing'],
      entry_points = {
        "distutils.commands": [
            "release = iw.releaser.commands:release",
            "build_mo = iw.releaser.commands:build_mo"],
        "console_scripts": [
            "project_release = iw.releaser.project:make_release",
            "project_deploy = iw.releaser.project:deploy_release",
            "project_diff = iw.releaser.project:diff_releases"
            ]
        },
      )

