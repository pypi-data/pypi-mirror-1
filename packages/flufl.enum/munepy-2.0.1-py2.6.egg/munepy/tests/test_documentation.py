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

"""Doctest harness."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'test_suite',
    ]


import os
import sys
import doctest
import unittest

import munepy


DOT = '.'
COMMASPACE = ', '



class chdir:
    """A context manager for temporary directory changing."""
    def __init__(self, directory):
        self._curdir = None
        self._directory = directory

    def __enter__(self):
        self._curdir = os.getcwd()
        os.chdir(self._directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self._curdir)
        # Don't suppress exceptions.
        return False



def stop():
    """Call into pdb.set_trace()"""
    # Do the import here so that you get the wacky special hacked pdb instead
    # of Python's normal pdb.
    import pdb
    pdb.set_trace()



def setup(testobj):
    """Test setup."""
    # Make sure future statements in our doctests are the same as everywhere
    # else.
    testobj.globs['absolute_import'] = absolute_import
    testobj.globs['unicode_literals'] = unicode_literals
    testobj.globs['stop'] = stop



def test_suite():
    suite = unittest.TestSuite()
    topdir = os.path.dirname(munepy.__file__)
    packages = []
    for dirpath, dirnames, filenames in os.walk(topdir):
        if 'docs' in dirnames:
            docsdir = os.path.join(dirpath, 'docs')[len(topdir)+1:]
            packages.append(docsdir)
    # Under higher verbosity settings, report all doctest errors, not just the
    # first one.
    flags = (doctest.ELLIPSIS |
             doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_NDIFF)
    # Add all the doctests in all subpackages.
    doctest_files = {}
    with chdir(topdir):
        for docsdir in packages:
            package_path = 'munepy.' + DOT.join(docsdir.split(os.sep))
            for filename in os.listdir(docsdir):
                base, extension = os.path.splitext(filename)
                if os.path.splitext(filename)[1] == '.txt':
                    module_path = package_path + '.' + base
                    docpath = os.path.join(docsdir, filename)
                    doctest_files[module_path] = docpath
    for module_path in sorted(doctest_files):
        test = doctest.DocFileSuite(
            doctest_files[module_path],
            package='munepy',
            optionflags=flags,
            setUp=setup)
        suite.addTest(test)
    return suite
