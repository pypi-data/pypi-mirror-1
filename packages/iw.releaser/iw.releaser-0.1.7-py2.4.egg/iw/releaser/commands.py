# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

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
""" releaser
"""
from setuptools import Command

from base import yes_no_input
from packet import get_version
from packet import raise_version
from packet import check_tests
from packet import increment_changes
from packet import create_branches
from packet import pypi_upload

import sys

class release(Command):
    """Releaser"""

    description = "Releases an egg"
    user_options = [
            ('testing', 't', 'run tests before anything'),
            ('release','r', 'release package'),
            ('upload', 'u', 'upload package'),
            ('version=', None, 'new version number'),
            ('auto', 'a', 'automatic mode'),
        ]

    def initialize_options(self):
        """init options"""
        self.testing = False
        self.release = False
        self.upload = False
        self.version = ''
        self.auto = False

    def finalize_options(self):
        """finalize options"""
        if self.auto and not self.version:
            print 'You must specify a version in auto mode'
            sys.argv.append('-h')
            __import__('setup')
            sys.exit(-1)

    def run(self):
        """runner"""
        make_package_release(auto=self.auto,
                             testing=self.testing,
                             release=self.release,
                             upload=self.upload,
                             new_version=self.version)

def make_package_release(auto=False,
                         testing=False,
                         release=False,
                         upload=False,
                         new_version=''):
    """release process"""
    version = get_version()
    print 'This package is version %s' % version

    # tests
    if not auto:
        if not testing:
            testing = yes_no_input(('Do you want to run tests before '
                                 'releasing ?'), default='y')
        if testing:
            check_tests()
    else:
        check_tests()

    # releasing
    if not auto:
        if not release:
            release = yes_no_input('Do you want to create the release ?')
    else:
        release = True

    if release:
        if not auto:
            if not new_version:
                new_version = raw_input('Enter a version : ')
            raise_version(new_version)
        else:
            if not new_version:
                new_version = str(float(version)+.1)
            print 'Raising the version...'
            raise_version(new_version)

        print 'Commiting changes...'
        increment_changes()
        print 'Creating branches...'
        create_branches()
    else:
        new_version = version

    if not auto:
        if not upload:
            upload = yes_no_input(('Do you want to upload the package '
                                   'to various package servers ?'))
        if upload:
            pypi_upload()
    else:
        pypi_upload()

    print '%s released' % new_version


