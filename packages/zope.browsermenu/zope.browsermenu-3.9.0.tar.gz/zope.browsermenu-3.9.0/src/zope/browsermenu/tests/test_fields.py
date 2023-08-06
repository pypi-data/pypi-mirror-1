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
"""Test fields.

$Id: test_fields.py 103270 2009-08-27 13:56:02Z nadako $
"""
import unittest
from zope.testing import cleanup, doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.browsermenu.field',
                     setUp=lambda test:cleanup.setUp(),
                     tearDown=lambda test:cleanup.tearDown()),
        ))
