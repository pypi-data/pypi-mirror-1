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
Generic Test case for tcplogger doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import re

from zope.testing import doctest, renormalizing
from svnhelper.testing import setUpRepository
from svnhelper.testing import tearDownRepository
from svnhelper.testing import svn_normalizer
from svnhelper.testing import mkrepos
from svnhelper.testing import rmrepos
from svnhelper.utils import *

def ls(*args):
    root = os.path.join(*args)
    for name in os.listdir(root):
        if os.path.isdir(os.path.join(root,name)):
            print 'd %s' % name
        else:
            print '- %s' % name

def svn(*args):
    return sh(get_binary('svn'), *args)[1]

def setUp(test):
    setUpRepository(test)

def tearDown(test):
    tearDownRepository(test)

package_dir = os.path.abspath(os.path.dirname(__file__))

test_package = os.path.join(package_dir, 'tests', 'my.testing')

flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_ONLY_FIRST_FAILURE)

def doc_suite():
    """Returns a test suite, based on doctests found in . """
    suite = []

    if package_dir not in sys.path:
        sys.path.append(package_dir)

    # filtering files on extension
    docs = [doc for doc in
            os.listdir(package_dir) if doc.endswith('.py')]
    docs = [doc for doc in docs if not doc.startswith('__')]

    for test in docs:
        fd = open(os.path.join(package_dir, test))
        content = fd.read()
        fd.close()
        if '>>> ' not in content:
            continue
        test = test.replace('.py', '')
        suite.append(doctest.DocTestSuite(
                     'svnhelper.%s' % test,
                     optionflags=flags,
                     globs=globals(),
                     setUp=setUp,
                     tearDown=tearDown,
                     checker = renormalizing.RENormalizing(svn_normalizer),
                     ))

    # filtering files on extension
    docs = [os.path.join(package_dir, doc) for doc in
            os.listdir(package_dir) if doc.endswith('.txt')]

    for test in docs:
        suite.append(doctest.DocFileSuite(
                     test, optionflags=flags,
                     globs=globals(),
                     setUp=setUp,
                     tearDown=tearDown,
                     checker = renormalizing.RENormalizing(svn_normalizer),
                     module_relative=False))

    return suite

def test_repository():
    """ make a test repository::

        >>> dirname = mkrepos()
        >>> rmrepos(dirname)
    """


def test_suite():
    """returns the test suite"""
    suite = []
    suite.extend(doc_suite())
    return unittest.TestSuite(suite)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

