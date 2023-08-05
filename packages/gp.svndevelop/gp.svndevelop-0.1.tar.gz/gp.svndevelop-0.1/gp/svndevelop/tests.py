# -*- coding: utf-8 -*-
# Copyright (C)2007 Gael Pasgrimaud

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
"""
Generic Test case for gp.svndevelop doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os

from zope.testing import doctest, renormalizing
import zc.buildout.testing
import svnhelper.testing
import svnhelper.tests
from svnhelper.core import helper

test_package = os.path.dirname(svnhelper.tests.__file__)
test_package = os.path.join(test_package, 'tests', 'my.testing')

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('gp.svndevelop', test)
    svnhelper.testing.setUpRepository(test)
    test.globs['init_test_package'](test_package)
    helper.import_to(test.globs['package_dir'],
                     test.globs['repository'])

def tearDown(test):
    svnhelper.testing.tearDownRepository(test)
    zc.buildout.testing.buildoutTearDown(test)

flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_ONLY_FIRST_FAILURE)

def test_suite():
    return unittest.TestSuite([doctest.DocFileSuite(
                os.path.join(os.path.dirname(__file__), 'README.txt'),
                optionflags=flags,
                globs=globals(),
                setUp=setUp,
                tearDown=tearDown,
                module_relative=False)])


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

