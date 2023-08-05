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
import ConfigParser
import os
import re
import sys

import base

join = os.path.join

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

def parse_url(url):
    """return base_url, cfg::

        >>> from iw.releaser.project import parse_url
        >>> parse_url('file:///svn.sf.net/')
        ('file:///svn.sf.net', 'buildout.cfg')
        >>> parse_url('file:///svn.sf.net/sample.cfg')
        ('file:///svn.sf.net', 'sample.cfg')
    """
    if not url.endswith('.cfg'):
        if url.endswith('/'):
            url = url[:-1]
        return url, 'buildout.cfg'
    url = url.split('/')
    filename = url.pop()
    return '/'.join(url), filename

def check_python(valid_version=(2, 4)):
    """raises if not the right python"""
    # need to but requirement somewhere un buildout
    version = sys.version_info[0:len(valid_version)]
    if version != valid_version:
        raise base.ReleaseError('You must run python%s' \
            % '.'.join(list(version)))
    else:
        return '.'.join([str(v) for v in version])


def archive_contents(archive, location):
    """ generates the tarball"""
    tar = base.TarFile.open(join(location, '..', archive), 'w:gz')
    # recurse on directory
    dirname, name = os.path.split(location)
    for root, dirs, filenames in os.walk(location):
        for filename in filenames:
            path = join(root, filename)
            arcname = path.replace(location, name)
            tar.add(path, arcname, False)
    tar.close()

def set_option(filename, section, option, value):
    """Setting option."""
    config = ConfigParser.ConfigParser()
    config.read([filename])
    if section not in config.sections():
        config.add_section(section)
    config.set(section, option, value)
    fd = open(filename, 'wb')
    try:
        config.write(fd)
    finally:
        fd.close()

def get_option(filename, section, option):
    """Reading option."""
    config = ConfigParser.ConfigParser()
    config.read([filename])
    return config.get(section, option)

def deploy_release(path=None, target=None):
    """deploy a release in-place"""

    print 'Checking python version ...'
    print '%s ok.' % check_python()

    if path is None:
        if len(sys.argv) < 2:
            print 'usage : project_deploy http://to/your/buildout/config.cfg'
            sys.exit(1)
        path = sys.argv[1]

    url, filename = parse_url(path)

    if not target:
        target = 'buildout'

    if os.path.isfile(path) or os.path.isdir(path):
        target = url

    if not os.path.isdir(target):
        os.mkdir(target)

    # changes all paths
    os.chdir(target)
    
    if not os.path.isfile(path) and not os.path.isdir(path):
        # let's get the buildout
        base.system('svn co %s .' % url)
    else:
        target = url

    print 'Using local directory %s with %s' % (target, filename)

    # now we can run bootstrap.py
    base.system('%s bootstrap.py' % sys.executable)

    # then bin/buildout -v
    binary = join('bin', 'buildout')
    buildout = 'buildout.cfg'

    # see if a develop remains
    try:
        develop = get_option(filename, 'buildout', 'develop')
    except ConfigParser.NoOptionError:
        # ok we are safe
        pass
    else:
        # we need to develop them
        develops = ['    %s' % line.strip() 
                    for line in develop.split('\n')
                    if line.strip() != '']
        msg = '\nYou need to make releases of theses packages:\n%s'
        msg = msg % '\n'.join(develops)
        raise base.ReleaseError(msg)

    print 'Checking binary.'
    if base.check_command('%s -v' % binary):
        base.ReleaseError('Something went wrong in deployement')
    print '%s ok.' % binary

    if filename != 'buildout.cfg':
        set_option(buildout, 'buildout', 'extends', filename)
        
    set_option(buildout, 'buildout', 'download-cache', 
               'downloads')

    if not os.path.isdir('downloads'):
        os.mkdir('downloads')

    print base.system(binary)

    set_option(buildout, 'buildout', 'install-from-cache', 
               'true')
    set_option(buildout, 'buildout', 'offline', 'true')

    print 'Archiving %s.' % target
    archive = filename.replace('.cfg', '.tar.gz')
    archive_contents(archive, '.')
    print '%s ok.' % archive

