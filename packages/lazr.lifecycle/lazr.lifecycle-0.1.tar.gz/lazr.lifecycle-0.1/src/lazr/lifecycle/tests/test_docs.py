# Copyright 2009 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.lifecycle
#
# lazr.lifecycle is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.lifecycle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.lifecycle.  If not, see <http://www.gnu.org/licenses/>.
"Test harness for doctests."

# pylint: disable-msg=E0611,W0142

__metaclass__ = type
__all__ = [
    'additional_tests',
    ]

import atexit
import doctest
import os
from pkg_resources import (
    resource_filename, resource_exists, resource_listdir, cleanup_resources)
import unittest
import warnings

DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF)


def raise_warning(message, category=None, stacklevel=1):
    if category is None:
        kind = 'UserWarning'
    else:
        kind = category.__class__.__name__

    print "%s: %s" % (kind, message)

def setUp(test):
    """Makes any warning an error."""
    test.globs['saved_warn'] = warnings.warn
    warnings.warn = raise_warning

def tearDown(test):
    """Reset the warnings."""
    warnings.warn = test.globs['saved_warn']


def additional_tests():
    "Run the doc tests (README.txt and docs/*, if any exist)"
    doctest_files = [
        os.path.abspath(resource_filename('lazr.lifecycle', 'README.txt'))]
    if resource_exists('lazr.lifecycle', 'docs'):
        for name in resource_listdir('lazr.lifecycle', 'docs'):
            if name.endswith('.txt'):
                doctest_files.append(
                    os.path.abspath(
                        resource_filename('lazr.lifecycle', 'docs/%s' % name)))
    kwargs = dict(
        setUp=setUp, tearDown=tearDown,
        module_relative=False,
        optionflags=DOCTEST_FLAGS)
    atexit.register(cleanup_resources)
    return unittest.TestSuite((
        doctest.DocFileSuite(*doctest_files, **kwargs)))
