##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
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
"""Location support tests

$Id: tests.py 107006 2009-12-23 13:17:16Z kobold $
"""

import doctest
import unittest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('location.txt'),
        doctest.DocTestSuite('zope.location.traversing'),
        doctest.DocTestSuite('zope.location.pickling'),
    ))
