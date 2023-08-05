##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Testing for z3c.etestbrowser

$Id: tests.py 71409 2006-12-05 07:44:33Z ctheune $
"""

import unittest

from zope.app.testing import functional
from zope.testing import doctest


def test_suite():
    return unittest.TestSuite(
        functional.FunctionalDocFileSuite("README.txt",
            optionflags=doctest.REPORT_NDIFF|doctest.NORMALIZE_WHITESPACE|
                doctest.ELLIPSIS))
