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
import subprocess
import tempfile
import sys
from ConfigParser import ConfigParser

from iw.releaser import base

re_version = re.compile(r"""^version\s*=\s*(?:"|')(.*?)(?:"|')""",
                        re.MULTILINE|re.DOTALL)  

def _get_setup():
    """returns setup content"""
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    return open(setup_py).read()

def get_version():
    """extract the version of the current package"""
    version = re_version.findall(_get_setup())
    if len(version) == 0:
        return None
    return version[0]

def raise_version(version):
    """raises the version"""
    new_setup = re_version.sub("version = '%s'" % version, _get_setup())
    setup_py = os.path.join(os.getcwd(), 'setup.py') 
    f = open(setup_py, 'w')
    try:
        f.write(new_setup)
    finally:
        f.close()

def check_tests():
    """runs the tests over the package"""
    try:
        # XXX get the env python
        base.check_call('python setup.py ztest', shell=True)
        return True
    except base.CalledProcessError:
        return False

def increment_changes():
    """increment changes"""
    version = get_version()
    CHANGES = os.path.join(os.getcwd(), 'CHANGES')
    if not os.path.exists(CHANGES):
        # no CHANGES file, let's create it
        content = ['* trunk',
                   '  - ',
                   '',
                   '* %s' % version,
                   '  - initial revision']
    else:
        # raising the version
        content = open(CHANGES).read()
        if '* %s' % version not in content:
            content = content.replace('* trunk', '* %s' % version)
            content = ['* trunk',  '  -'] + content.split('\n')
        else:
            content = content.split('\n')
    f = open(CHANGES, 'w')
    try:
        f.write('\n'.join(content))
    finally:
        f.close()

def _get_svn_paths():
    """return paths"""
    version = get_version()
    url = base.get_svn_url() 
    trunk = url
    if not url.endswith('/trunk'):
        raise base.ReleaseError('we are not in a trunk folder ! (%s)' % url) 

    paths = {}
    paths['trunk'] = trunk
    paths['root'] = trunk.replace('/trunk', '/')
    paths['tag_root'] = '%stags' % paths['root']
    paths['branch_root'] = '%sbranches' % paths['root']
    paths['tag'] = '%stags/%s' % (paths['root'], version)
    paths['branch'] = '%sbranches/%s' % (paths['root'], version)
    return paths

def create_branches():
    """creates a tag an a branch for the current version"""
    version = get_version()
    paths = _get_svn_paths()
    root = paths['root']
    tag_root = paths['tag_root']
    branch_root = paths['branch_root']
    tag = paths['tag']
    branch = paths['branch']
    trunk = paths['trunk']

    # commiting trunk
    base.svn_commit('preparing release %s' % version)
    
    # checking if tag_root and branch_root exists 
    for branch_ in (tag_root, branch_root):
        base.svn_mkdir(branch_)
   
    # checking if the branch exists, if so, override it
    base.svn_remove(branch)
    base.svn_copy(trunk, branch, 'branch for %s release' % version)

    # now let's work on the branch: removing setup.cfg if it exists
    base.svn_rm('%s/setup.cfg' % branch, "file not needed for release")
    
    # let's tag
    base.svn_remove(tag)
    base.svn_copy(branch, tag, 'tag for %s release' % version) 

def _checkout_tag():
    version = get_version()
    paths = _get_svn_paths()
    rep = tempfile.mkdtemp()
    base.svn_checkout(paths['tag_root'], rep)
    os.chdir(os.path.join(rep, version))

def _run_setup(*args):
    old_args = sys.argv
    sys.argv = [sys.argv[0] + 'setup.py'] + list(args)
    __import__('setup')
    sys.argv = old_args

def pypi_upload():
    """upload into pypi"""
    _checkout_tag()
    # let's upload on selected servers
    if os.environ.has_key('HOME'): 
        rc = os.path.join(os.environ['HOME'], '.pypirc')
        if not os.path.exists(rc):
            return 
        config = ConfigParser()
        config.read(rc)
        sections = config.sections()

        if 'distutils' in sections:
            index_servers = config.get('distutils', 'index-servers')
            _servers = [server.strip() for server in 
                        index_servers.split('\n')
                        if server.strip() != '']
            for server in _servers:
                if config.has_option(server, 'repository'):
                    repository = config.get(server, 'repository')
                else:
                    repository = 'http://pypi.python.org/pypi'
                _pypi_upload(repository)

        elif 'server-login' in sections:
            if config.has_option(server, 'repository'):
                repository = config.get(server, 'repository')
            else:
                repository = 'http://pypi.python.org/pypi' 
            _pypi_upload(repository)     
        
def _pypi_upload(repository):
    res = raw_input('Do you want to upload to %s ? (Y/n):' % repository)

    res = res.lower().strip()
    if res == 'y':
        _run_setup('mregister', 'sdist', 'bdist_egg', 'mupload', '-r',
                   repository)

