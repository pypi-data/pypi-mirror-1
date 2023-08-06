##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Password Managers Tests

$Id: tests.py 97566 2009-03-06 12:23:42Z nadako $
"""
import unittest
from zope.testing import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.password.password'),
        doctest.DocTestSuite(
            'zope.password.testing',
            optionflags=doctest.ELLIPSIS),
        ))
