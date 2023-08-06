##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""XXX short summary goes here.

$Id: tests.py 102792 2009-08-14 21:03:37Z jim $
"""
import unittest
from zope.testing import doctest
import ZODB.tests.util

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('referrers.txt', 'strip_versions.test',
            setUp=ZODB.tests.util.setUp, tearDown=ZODB.tests.util.tearDown,
            ),
        ))

