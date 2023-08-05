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
from tempfile import mkdtemp
import base

join = os.path.join

extract_path = re.compile(r'^(htt(?:p|ps)://)(.*?)/?$')

def _log(msg):
    print msg

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
        version = '.'.join([str(step) for step in version])
        raise base.ReleaseError('You must run python%s' % version)
    else:
        return '.'.join([str(v) for v in version])


def diff_releases(old=None, new=None, result=None):
    """takes two tarballs, and generates a diff one"""
    if old is None:
        if len(sys.argv) < 3:
            print 'Usage %s old_tarball new_tarball [diff_tarball]' % \
                sys.argv[0]
            sys.exit(0)
        old = sys.argv[1]
        new = sys.argv[2]
        if len(sys.argv) > 3:
            result = sys.argv[3]

    old_tarball = base.TarFile.open(old)
    new_tarball = base.TarFile.open(new)
    old_name = os.path.split(old)[-1]
    new_name = os.path.split(new)[-1]
    root_old_name = '.'.join(old_name.split('.')[:-1])
    root_new_name = '.'.join(new_name.split('.')[:-1])

    if result is None:
        result = '%s-to-%s.tgz' % (root_old_name, root_new_name)

    
    old_files = {}
    for f in old_tarball.getmembers():
        old_files[f.name] = f

    tmp = mkdtemp()

    _log('Selecting files')
    for f in new_tarball.getmembers():
        if f.name in old_files:
            if f.isfile():
                # if its a file checking the diff
                old_file = old_files[f.name]
                old_content = old_tarball.extractfile(old_file)
                old_content = old_content.read()
                new_content = new_tarball.extractfile(f).read()
                if old_content == new_content:
                    continue
        new_tarball.extract(f, tmp)

    # now writing the diff tarball
    _log('Writing archive')
    diff_tarball = base.TarFile.open(result, 'w:gz')
    try:
        for root, dirs, filenames in os.walk(tmp):
            for filename in filenames:
                path = join(root, filename)
                arcname = path.replace(tmp, '')
                diff_tarball.add(path, arcname, False)
    finally:
        diff_tarball.close()
    _log('Diff done.')

def archive_contents(archive, location, previous=None):
    """generates the tarball"""
    location = os.path.realpath(location)
    dirname, name = os.path.split(location)
    tar = base.TarFile.open(join(dirname, archive), 'w:gz')
    try:
        for root, dirs, filenames in os.walk(location):
            for filename in filenames:
                path = join(root, filename)
                arcname = path.replace(location, name)
                tar.add(path, arcname, False)
    finally:
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

def _python():
    """returns python bin"""
    possible_locations = (join('bin', 'python'),
                          join('bin', 'python2.4'),
                          join('Scripts', 'python'))
    for location in possible_locations:
        if os.path.exists(location):
            return location
    return 'python'

def deploy_release(path=None, target=None, archiving='full'):
    """deploy a release in-place"""
    print 'Checking python version ...'
    print '%s ok.' % check_python()

    if path is None:
        if len(sys.argv) < 2:
            print 'usage : project_deploy http://to/your/buildout/config.cfg'
            sys.exit(1)
        path = sys.argv[1]

    url, filename = parse_url(path)
    folder = url.split('/')[-1]
    release_name = '%s-%s' % (folder, filename.split('.')[0])
    if not target:
        target = release_name

    if os.path.isfile(path) or os.path.isdir(path):
        target = url

    if not os.path.isdir(target):
        os.mkdir(target)

    root = os.path.realpath(target)
    os.chdir(root)

    # changes all paths
    if not os.path.isfile(path) and not os.path.isdir(path):
        # let's get the buildout
        print base.system('svn co %s .' % url)
    else:
        target = url

    print 'Using local directory %s with %s' % (target, filename)

    # let's generate a virtualenv python
    # to make sure we don't loose eggs
    old = sys.argv
    try:
        sys.argv = ['project_deploy', '--no-site-packages', '.']
        from virtualenv import main
        main()
    finally:
        sys.argv = old

    # now we can run bootstrap.py
    python = _python()

    print base.system('%s bootstrap.py' % python)

    # then bin/buildout -v
    binary = join('bin', 'buildout')
    buildout = 'buildout.cfg'

    # see if download-cache was present
    try:
        cache = get_option(filename, 'buildout', 'download-cache')
    except ConfigParser.NoOptionError:
        raise base.ReleaseError(("You need to add 'download-cache = downloads'"
                                 "' in the [buildout] section"))

    print 'Checking binary.'
    buildout_cmd = '%s -c %s -v' % (binary, filename)
    print 'Calling %s' % buildout_cmd
    try:
        if not base.check_command(buildout_cmd):
            raise base.ReleaseError('Something went wrong in deployement')
    except:
        # second chance (re-runned buildouts)
        if not base.check_command(buildout_cmd):
            raise base.ReleaseError('Something went wrong in deployement')

    print '%s ok.' % binary

    # archiving process: changes buildout.cfg and create a tarball
    if filename != 'buildout.cfg':
        set_option(buildout, 'buildout', 'extends', filename)

    set_option(buildout, 'buildout', 'install-from-cache',
               'true')
    set_option(buildout, 'buildout', 'offline', 'true')

    # archiving:
    #  - a full archive
    #  - an diffed archived
    print 'Archiving %s.' % target
    if archiving == 'none':
        return
    archive = 'release-%s-%s.tgz' % (os.path.split(target)[-1],
                                     filename.split('.')[0])
    archive_contents(archive, '.')
    print '%s ok.' % archive

