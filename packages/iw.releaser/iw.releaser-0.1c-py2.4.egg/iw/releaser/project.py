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
import os
import re
import sys

import base

extract_path = re.compile(r'^(htt(?:p|ps)://)(.*?)/?$')

def make_release(version=None):
    """this is called when a release is made over a buildout"""
    
    # first, let's check we are in the buildout folder
    dir = os.getcwd()
    if 'buildout.cfg' not in os.listdir(dir):
        base.ReleaseError('You are not in a buildout folder')

    # next, let's create a branch for the release
    # after we asked the user what is the version to release
    if version is None:
        version = raw_input('What version you are releasing ? ')

    # were are we ?
    url = base.get_svn_url()

    # let's get the releases base folder
    extracted = extract_path.findall(url)
    protocol = extracted[0][0]
    path = extracted[0][1].split('/')
    path[-1] = 'releases' 
    releases = '%s%s' % (protocol, '/'.join(path))
    
    # creates it if not found
    base.svn_mkdir(releases)

    # and the current version
    release = '%s/%s' % (releases, version)

    # if exists, let's drop it
    base.svn_remove(release)

    # now let's create the branch
    base.svn_copy(url, release, 'creating %s release for project' % version)

def deploy_release(svn_path):
    """deploy a release in-place"""
    # let's get the buildout
    base.svn_checkout(svn_path, '.')

    # now we can run bootstrap.py
    sys.argv = sys.argv[:-1]
    __import__('bootstrap') 

    # then bin/buildout -v
    if base.check_command(os.path.join('bin', 'buildout -v')):
        base.ReleaseError('Something went wrong in deployement') 

