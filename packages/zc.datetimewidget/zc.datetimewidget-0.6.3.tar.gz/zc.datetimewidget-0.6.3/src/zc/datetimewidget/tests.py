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
"""Datetime Widget unittests

$Id: tests.py 103123 2009-08-24 08:05:17Z icemac $
"""
__docformat__ = "reStructuredText"
import os
import doctest
import unittest

from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import functional, setup


def setUp(test):
    setup.placefulSetUp()

def tearDown(test):
    setup.placefulTearDown()

DTWidgetLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'DTWidgetLayer', allow_teardown=True)

def test_suite():
    DemoSuite = functional.FunctionalDocFileSuite('demo/README.txt')
    DemoSuite.layer = DTWidgetLayer
    return unittest.TestSuite(
        (
        DocFileSuite('widgets.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('datetimewidget.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DemoSuite,
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

