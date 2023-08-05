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

from packet import get_version
from packet import raise_version
from packet import check_tests
from packet import increment_changes
from packet import create_branches
from packet import pypi_upload

class PacketReleaser(Command):
    """Releaser"""
 
    description = "Releases an egg"
    user_options = []

    def initialize_options(self):
        """init options"""
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        """runner"""
        make_package_release()
 
def make_package_release(auto=False):
    """release process"""
    version = get_version()
    print 'This package is version %s' % version
    
    # tests
    if not auto:
        testing = raw_input(('Do you want to run tests before '
                             'releasing ? '))
        if testing.strip().lower() in ('y', 'yes'):
            check_tests()
    else:
        check_tests()

    # releasing
    if not auto:
        release = raw_input('Do you want to create the release ? ')
        release = release.strip().lower() in ('y', 'yes')
    else:
        release = True

    if release:
        if not auto:
            new_version = raw_input('Enter a version : ')
            raise_version(new_version)
        else:
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
        testing = raw_input(('Do you want to upload the package to various '
                             'package servers ? '))
        if testing.strip().lower() in ('y', 'yes'):
            pypi_upload()
    else:
        pypi_upload()

    print '%s released' % new_version


