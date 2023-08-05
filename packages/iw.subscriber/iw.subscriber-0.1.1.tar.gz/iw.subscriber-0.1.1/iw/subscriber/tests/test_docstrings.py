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
"""
Generic Test case for doc strings
"""
__docformat__ = 'restructuredtext'

import unittest
import random
import sys
import os

from zope.testing import doctest
from zope.publisher.browser import TestRequest

class TestBrain(object):

    def __init__(self, path='/portal/brain1', emails=['gael@ingeniweb.com']):
        self.path = path
        self.getMails = emails

    def getPath(self):
        return self.path

    def __repr__(self):
        return '<TestBrain at %s>' % self.path

def test_brains():
    brains = []
    def test_mails():
        l = xrange(5)
        return ['gael%i@ingeniweb.com' % random.choice(l) \
                    for i in xrange(random.choice(l))]
    for i in xrange(20):
        brains.append(TestBrain(path='/portal/brain%i' % i,
                                emails=test_mails()))
    return brains

current_dir = os.path.abspath(os.path.dirname(__file__))

def doc_suite(test_dir, globs=None):
    """Returns a test suite, based on doc tests strings found in /*.py"""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
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
        suite.append(doctest.DocTestSuite('iw.subscriber.%s' % test,
                                            optionflags=flags,
                                            globs=globs))

    # filtering files on extension
    docs = [doc for doc in
            os.listdir(os.path.join(package_dir, 'browser')) if doc.endswith('.py')]
    docs = [doc for doc in docs if not doc.startswith('__')]

    for test in docs:
        fd = open(os.path.join(package_dir,'browser', test))
        content = fd.read()
        fd.close()
        if '>>> ' not in content:
            continue
        test = test.replace('.py', '')
        suite.append(doctest.DocTestSuite('iw.subscriber.browser.%s' % test,
                                            optionflags=flags,
                                            globs=globs))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

