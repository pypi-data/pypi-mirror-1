# Copyright (C) 2004-2010 Barry A. Warsaw
#
# This file is part of munepy.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import distribute_setup
distribute_setup.use_setuptools()

import sys

from munepy import __version__
from setuptools import setup, find_packages



if sys.hexversion < 0x20600f0:
    print('munepy requires at least Python 2.6')
    sys.exit(1)



setup(
    name            = 'munepy',
    version         = __version__,
    description     = 'Yet another Python enumeration package',
    long_description= """\
munepy is yet another Python enum package, with a slightly different take on
syntax and semantics than previous such packages.""",
    author          = 'Barry Warsaw',
    author_email    = 'barry@python.org',
    license         = 'LGPL',
    url             = 'http://launchpad.net/munepy',
    keywords        = 'enum',
    packages        = find_packages(),
    include_package_data    = True,
    use_2to3        = True,
    convert_2to3_doctests   = [
        'munepy/docs/README.txt',
        ],
    test_suite      = 'munepy.tests.test_documentation.test_suite',
    )
