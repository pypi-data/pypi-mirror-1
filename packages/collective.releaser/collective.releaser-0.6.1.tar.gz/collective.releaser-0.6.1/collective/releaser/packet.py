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
from subprocess import Popen, PIPE
import os
import shutil
import re
import pkg_resources
import subprocess
import tempfile
import sys
from ConfigParser import ConfigParser
import datetime
import docutils.examples
from docutils.utils import SystemMessage

from collective.releaser import base
from collective.releaser.base import savewd

re_version = re.compile(r"""^version\s*=\s*(?:"|')(.*?)(?:"|')""",
                        re.MULTILINE|re.DOTALL)

re_name = re.compile(r"""name\s*=\s*(?:"|')(.*?)(?:"|')""",
                     re.MULTILINE|re.DOTALL)

def _get_setup():
    """returns setup content"""
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    return open(setup_py).read()

def get_version():
    """extract the version of the current package"""
    return get_metadata('version')

def get_name():
    """extract the name of the current package"""
    return get_metadata('name')

@savewd
def get_metadata(name, package_path=None):
    if package_path is not None:
        os.chdir(package_path)
    content = os.listdir(os.getcwd())
    if 'setup.py' not in content:
        raise ValueError('No setup.py file found in %s' % os.getcwd())
    name = name.replace('_', '-')
    command = '%s setup.py --%s' % (sys.executable, name)
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    return p.stdout.read().strip()


    import setuptools
    attrs = {}
    old = setuptools.setup
    try:
        def _setup(**kw):
            if name in kw:
                attrs[name] = kw[name]
        setuptools.setup = _setup
        import setup
    finally:
        setuptools.setup = old
    return attrs.get(name)

def raise_version(version):
    """raises the version"""

    # check version.txt
    for root, dirs, files in os.walk(os.getcwd()):
        for dirname in dirs:
            if not os.path.isdir(os.path.join(root, dirname, 'tests')):
                continue
            filename = os.path.join(root, dirname, 'version.txt')
            if not os.path.isfile(filename):
                continue
            f = open(filename, 'wb')
            try:
                f.write(version)
            finally:
                f.close()

    # check setup.py
    new_setup = re_version.sub("version = '%s'" % version, _get_setup())
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    f = open(setup_py, 'wb')
    try:
        f.write(new_setup)
    finally:
        f.close()

def check_tests():
    """runs the tests over the package"""
    try:
        base.check_call('%s setup.py test' % sys.executable, shell=True)
        return True
    except base.CalledProcessError:
        return False

def increment_changes():
    """increment changes"""

    author = get_metadata('maintainer')
    if author == 'UNKNOWN':
        author = get_metadata('author')
    if author == 'UNKNOWN':
        author = get_metadata('contact')
    if author != 'UNKNOWN':
        author = '[%s]' % author
    else:
        author = ''

    version = get_version()
    locations = (os.path.join(os.getcwd(), 'CHANGES'),
                 os.path.join(os.getcwd(), 'CHANGES.txt'))
    CHANGES = locations[0]
    if not os.path.exists(CHANGES) and os.path.exists(locations[1]):
        CHANGES = locations[1]

    year = datetime.datetime.now().strftime('%Y')
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    trunk_re = re.compile(r'^trunk \(.*\)$', re.DOTALL)
    trunk_line = 'trunk (%s)' % now
    bootstrap = [trunk_line, len(trunk_line) * '=', '',
                 '  - xxx ' + author, '']

    if os.path.exists(CHANGES):
        content = open(CHANGES).read()
        # let's replace the trunk with the current version and date
        version_line = '%s (%s)' % (version, now)
        underline = len(version_line) * '='
        content = content.split('\n')
        for index, line in enumerate(content):
            if trunk_re.match(line):
                content[index] = version_line
                content[index+1] = underline
                break
        content = bootstrap + content
    else:
        # no CHANGES file, let's create it
        content = bootstrap

    f = open(CHANGES, 'wb')
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

def create_tag():
    """creates a tag for the current version"""
    if not base.has_svn_support():
        raise base.ReleaseError('You need Subversion client')

    version = get_version()
    paths = _get_svn_paths()
    root = paths['root']
    tag_root = paths['tag_root']
    tag = paths['tag']
    trunk = paths['trunk']

    # commiting trunk
    base.svn_commit('preparing release %s' % version)

    # checking if tag_root exists
    base.svn_mkdir(tag_root)

    # checking if the tag exists, if so, override it
    base.svn_remove(tag)
    base.svn_copy(trunk, tag, 'tag for %s release' % version)

    # now let's work on the tag: making a few changes in setup.cfg
    rep = tempfile.mkdtemp()
    old_rep = os.getcwd()
    try:
        os.chdir(rep)
        base.svn_checkout(tag, rep)
        setup_file = os.path.join(rep, 'setup.cfg')
        if os.path.exists(setup_file):
            setup_cfg = ConfigParser()
            setup_cfg.read([setup_file])
            changed = False
            if 'egg_info' in setup_cfg.sections():
                for option in ('tag_build', 'tag_svn_revision'):
                    if option in setup_cfg.options('egg_info'):
                        setup_cfg.remove_option('egg_info', option)
                        changed = True
            if changed:
                setup_cfg.write(open(setup_file, 'w'))
            base.svn_commit('fixed setup.cfg for %s' % version)
    finally:
        os.chdir(old_rep)
        shutil.rmtree(rep, ignore_errors=True)

def _checkout_tag():
    version = get_version()
    paths = _get_svn_paths()
    rep = tempfile.mkdtemp()
    base.svn_checkout(paths['tag'], rep)
    os.chdir(rep)

def _run_setup(*args):
    old_args = sys.argv
    sys.argv = [sys.argv[0]] + list(args)
    __import__('setup')
    del sys.modules['setup']
    sys.argv = old_args

def pypi_upload(commands):
    """upload into pypi"""
    if base.has_svn_support():
        try:
            _checkout_tag()
        except base.ReleaseError:
            # inline releasing
            pass

    for command in commands:
        base.display('Running "%s"' % command)
        _run_setup(*command.split())

def get_long_description(package_path):
    return get_metadata('long_description', package_path)

def check_long_description(desc):
    if isinstance(desc, str):
        desc = desc.decode('utf8')
    try:
        docutils.examples.internals(desc)
    except SystemMessage:
        return False
    return True

def check_package(package_path=None):
    if package_path is None:
        package_path = os.getcwd()
    desc = get_long_description(package_path)
    if desc is None:
        return True
    return check_long_description(desc)

