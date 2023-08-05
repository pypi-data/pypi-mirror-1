##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTML-Editor Widget unittests

$Id: tests.py 74087 2007-04-10 12:56:29Z dobe $
"""
__docformat__ = "reStructuredText"

import doctest
import unittest

from zope.testing.doctestunit import DocTestSuite
from zope.app.testing import setup


def setUp(test):
    setup.placefulSetUp()

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite(
        (
        DocTestSuite('z3c.widget.tiny.widget',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
