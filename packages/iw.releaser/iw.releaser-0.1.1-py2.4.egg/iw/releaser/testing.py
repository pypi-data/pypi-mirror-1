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

import os, shutil
import zc.buildout.tests
import zc.buildout.testing
from zc.buildout.testing import system, rmdir, mkdir
from zc.buildout.testing import normalize_path

def svn_start(test, project=None):
    """create a test server
    """
    sample = test.globs['sample_buildout']
    base = os.path.split(sample)[0]
    root = os.path.split(base)[0]
    os.chdir(root)
    system('svnadmin create %s/repos' % root)
    svn = 'file://%s' % os.path.join(root, 'repos')

    if project:
        sample = project

    project = os.path.split(sample)[1]
    mkdir(root, 'tmp')
    mkdir(root, 'tmp', project)
    mkdir(root, 'tmp', project, 'tags')
    mkdir(root, 'tmp', project, 'branches')
    shutil.copytree(sample, os.path.join(root, 'tmp', project, 'trunk'))
    os.chdir(os.path.join(root,'tmp'))
    system('svn import %s/ -m ""' % svn)
    rmdir(root, 'tmp')

    os.chdir(base)
    rmdir(sample)
    test.globs.update(
            test_dir=base,
            svn_url=svn,
            )

def releaserSetUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    test.globs['test'] = test
    test.globs['svn_start'] = svn_start

def releaserTearDown(test):
    zc.buildout.testing.buildoutTearDown(test)

def clearBuildout(test=None):
    zc.buildout.testing.buildoutTearDown(test)
    zc.buildout.testing.buildoutSetUp(test)

def clearRepository(test, project=''):
    zc.buildout.testing.buildoutTearDown(test)
    zc.buildout.testing.buildoutSetUp(test)
    svn_start(test, project)

