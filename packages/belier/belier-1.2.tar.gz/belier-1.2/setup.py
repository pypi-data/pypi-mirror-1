# -*- coding: utf-8 -*-
# Copyright © 2008 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
import os.path

CLASSIFIERS = [
    'Intended Audience :: System Administrators',
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Natural Language :: French',
    'Programming Language :: Python',
]



setup(name = 'belier',
    version = '1.2',
    license = 'GNU GPL v3',
    description = 'Ssh connection generation tool',
    long_description = 'Belier allows automated openings of a shell or command executions on remote computers through ssh. The main feature is Belier\'s ability to cross several computers before joining the final machine.',
    classifiers = CLASSIFIERS,
    author = 'Carl Chenet',
    author_email = 'chaica@ohmytux.com',
    url = 'http://www.ohmytux.com/belier',
    download_url = 'http://www.ohmytux.com/belier',
    packages = ['belier'],
    scripts = ['bel'],
    data_files=[(os.path.join('share','locale','fr','LC_MESSAGES'), ['i18n/fr/bel.mo'])]
)

