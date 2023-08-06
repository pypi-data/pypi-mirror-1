# Copyright (C) 2009 by the Free Software Foundation, Inc.
#
# This file is part of flufl.i18n
#
# flufl.i18n is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# flufl.i18n is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.i18n.  If not, see <http://www.gnu.org/licenses/>.
"Test harness for doctests."

# pylint: disable-msg=E0611,W0142

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'additional_tests',
    ]


import atexit
import doctest
import os
# pylint: disable-msg=F0401
from pkg_resources import (
    resource_filename, resource_exists, resource_listdir, cleanup_resources)
import unittest


DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)


def setup(testobj):
    """Test setup."""
    # Make sure future statements in our doctests match the Python code.
    testobj.globs['absolute_import'] = absolute_import
    testobj.globs['unicode_literals'] = unicode_literals


def additional_tests():
    "Run the doc tests (README.txt and docs/*, if any exist)"
    doctest_files = [
        os.path.abspath(resource_filename('flufl.i18n', 'README.txt'))]
    if resource_exists('flufl.i18n', 'docs'):
        for name in resource_listdir('flufl.i18n', 'docs'):
            if name.endswith('.txt'):
                doctest_files.append(
                    os.path.abspath(
                        resource_filename('flufl.i18n', 'docs/%s' % name)))
    kwargs = dict(module_relative=False,
                  optionflags=DOCTEST_FLAGS,
                  setUp=setup,
                  )
    atexit.register(cleanup_resources)
    return unittest.TestSuite((
        doctest.DocFileSuite(*doctest_files, **kwargs)))
