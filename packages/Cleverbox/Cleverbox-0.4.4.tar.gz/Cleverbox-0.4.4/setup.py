#!/usr/bin/env python2.4

# This file is part of the "Cleverbox" program.
#
# Cleverbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cleverbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cleverbox.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Tristan Rivoallan

from glob import glob
from setuptools import setup, find_packages

setup(

    # Project identity
    name='Cleverbox',
    version='0.4.4',
    description='Script for automating multiple trac instances deployment and maintenance.',
    long_description='The Cleverbox sits on top of [http://trac.edgewall.org Trac] and [http://subversion.tigris.org Subversion]. It provides an interactive shell for deploying and maintaining instances of both projects.',
    author='Tristan Rivoallan',
    author_email='trivoallan@clever-age.com',
    url='http://www.clever-age.org/trac/wiki/cleverbox',
    license='GPLv3',

    # Files
    packages=find_packages(),
    scripts=['scripts/cleverbox-admin'],
    data_files=[('/usr/share/cleverbox',     glob('assets/*')),
                ('/usr/share/doc/cleverbox', glob('docs/*')),
                ('/usr/share/man/man1',     glob('scripts/*.1'))],

    # Dependencies
    install_requires=['setuptools>=0.6b1', 'trac>=0.10.4', 'trac<=0.10.999']
)
