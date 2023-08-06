# Copyright (C) 2004-2010 Barry A. Warsaw
#
# This file is part of munepy.
#
# munepy is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# munepy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with munepy.  If not, see <http://www.gnu.org/licenses/>.

import distribute_setup
distribute_setup.use_setuptools()

import re
import sys

# Do not import __version__ from munepy.  Doing so causes problems with
# doctests running under 2to3.
with open('munepy/__init__.py') as fp:
    for line in fp:
        if line.startswith('__version__'):
            mo = re.search(r'\d+.\d+.\d', line)
            assert mo, 'No valid __version__ string found'
            __version__ = mo.group(0)
            break
    else:
        raise AssertionError('No __version__ assignment found')


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
    license         = 'LGPLv3',
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
