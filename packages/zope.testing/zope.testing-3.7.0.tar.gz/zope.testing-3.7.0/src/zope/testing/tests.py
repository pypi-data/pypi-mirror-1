##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for the testing framework.

$Id: tests.py 90401 2008-08-27 07:41:00Z srichter $
"""

import os
import sys
import unittest
from zope.testing import doctest, testrunner

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.testing.loggingsupport'),
        doctest.DocTestSuite('zope.testing.renormalizing'),
        doctest.DocTestSuite('zope.testing.server'),
        doctest.DocFileSuite('doctest.txt'),
        doctest.DocFileSuite('formparser.txt'),
        doctest.DocFileSuite('module.txt'),
        doctest.DocFileSuite('setupstack.txt'),
        ))
