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
import sys
import os
import re
from os.path import join
from setuptools import Command
from ConfigParser import ConfigParser

from collective.releaser.base import yes_no_input
from collective.releaser.base import safe_input
from collective.releaser.base import display
from collective.releaser.base import package_match
from collective.releaser.base import ReleaseError
from collective.releaser.base import has_svn_support
from collective.releaser.base import svn_commit

from collective.releaser.packet import get_version
from collective.releaser.packet import get_name
from collective.releaser.packet import raise_version
from collective.releaser.packet import check_tests
from collective.releaser.packet import increment_changes
from collective.releaser.packet import create_tag
from collective.releaser.packet import pypi_upload
from collective.releaser.packet import check_package

from collective.releaser.hook import apply_hooks

from msgfmt import Msgfmt

ROOT_FILE = join(os.path.expanduser("~"), '.pypirc')
ROOT_FILE_2 = join(os.path.expanduser("~"), 'pypirc')
CONF_FILE = 'iw-releaser.cfg'

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
            display('You must specify a version in auto mode')
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

def _get_commands(conf, package_name):
    """Reads a conf file and extract the commands to run"""
    parser = ConfigParser()
    parser.read(conf)

    def _validate_command(cmd, package, glob_style=False):

        command = 'mregister sdist bdist_egg mupload'
        packages = []

        for option in ('packages', 'release-packages'):
            if option in parser.options(cmd):
                packages = parser.get(cmd, option).split('\n')
                break

        for option in ('command', 'release-command'):
            if option in parser.options(cmd):
                command = parser.get(cmd, option)
                break

        exprs = [r.strip() for r in packages]
        founded = []
        if not glob_style:
            for expr in exprs:
                founded = [r for r in re.findall(expr, package) if
                           r.strip() != '']
        else:
            founded = package_match(package, exprs)
        if founded != []:
            return '%s -r %s' % (command, cmd)
        return None

    # old style
    commands = []
    glob_style = False
    if 'release' in parser.sections():
        if parser.has_option('release', 'commands'):
            commands = parser.get('release', 'commands').split('\n')

        if parser.has_option('release', 'glob-style'):
            glob_style = parser.get('release', 'glob-style').strip().lower()
            glob_style = glob_style == 'true'
    # new style
    elif 'distutils' in parser.sections():
        if parser.has_option('distutils', 'index-servers'):
            commands = parser.get('distutils', 'index-servers').split('\n')
        if parser.has_option('distutils', 'glob-style'):
            glob_style = parser.get('distutils', 'glob-style').strip().lower()
            glob_style = glob_style == 'true'

    commands = [cmd.strip() for cmd in commands if cmd.strip() != '']
    res = [_validate_command(cmd, package_name, glob_style) for cmd in commands]
    return [r for r in res if r is not None]

def make_package_release(auto=False,
                         testing=False,
                         release=False,
                         upload=False,
                         new_version=''):
    """release process"""
    version = get_version()
    display('This package is version %s' % version)

    package_name = get_name()

    # let's check the package
    if not check_package():
        raise ReleaseError('The description is not rest compliant')

    # let's see if we have a conf file

    places = (join(os.path.expanduser("~"), CONF_FILE),
              join(os.getcwd(), CONF_FILE))
    commands = []
    for place in places:
        if os.path.exists(place):
            # let's load the infos
            commands = _get_commands(place, package_name)
            break

    # new format
    if commands == []:
        # let's try in pypirc
        for place in (ROOT_FILE, ROOT_FILE_2):
            if os.path.exists(place):
                commands = _get_commands(place, package_name)

    # tests (not called in auto mode)
    if not auto:
        if not testing:
            testing = yes_no_input(('Do you want to run tests before '
                                    'releasing ?'), default='n')
        if testing:
            check_tests()

    # releasing
    if not auto:
        if not release:
            release = yes_no_input(('Do you want to create the release ? '
                                    'If no, you will just be able to deploy again '
                                    'the current release'))
    else:
        release = True

    if release:
        if not auto:
            if not new_version:
                new_version = safe_input('Enter a version',
                                         version)
            if version != new_version:
                raise_version(new_version)
        else:
            if not new_version:
                new_version = str(float(version)+.1)
            display('Raising the version...')
            raise_version(new_version)

        if has_svn_support():
            display('Commiting changes...')
            svn_commit('bumped revision')
            display('Creating tag...')
            create_tag()
            display('Back on dev...')
            increment_changes()
            svn_commit('starting new developments')
    else:
        new_version = version

    if commands != []:
        pypi_upload(commands)
        display('%s released' % new_version)
        apply_hooks(package_name=package_name,
                    version=new_version)

class build_mo(Command):
    """Msgfmt"""

    description = "Build msgfmt .mo files from their .po sources"
    user_options = []


    def initialize_options(self):
        """init options"""

    def finalize_options(self):
        """finalize options"""

    def run(self):
        """runner"""

        self.find_locales(os.getcwd())

    def find_locales(self, path):
        """find 'locales' directories and compiles .po files
        """
        for directory in os.listdir(path):
            dir_path = join(path, directory)
            if not os.path.isdir(dir_path):
                continue

            if directory == 'locales':
                self.compile_po(dir_path)
            else:
                self.find_locales(dir_path)

    def compile_po(self, path):
        """path is a locales directory, find ??/LC_MESSAGES/*.po and compiles
        them into .mo
        """
        for language in os.listdir(path):
            lc_path = join(path, language, 'LC_MESSAGES')
            if os.path.isdir(lc_path):
                for domain_file in os.listdir(lc_path):
                    if domain_file.endswith('.po'):
                        file_path = join(lc_path, domain_file)
                        display("Building .mo for %s" % file_path)
                        mo_file = join(lc_path, '%s.mo' % domain_file[:-3])
                        mo_content = Msgfmt(file_path, name=file_path).get()
                        mo = open(mo_file, 'wb')
                        mo.write(mo_content)
                        mo.close()

