##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""DTML Page Evaluation Tests

$Id: tests.py 72131 2007-01-20 12:56:52Z mgedmin $
"""
import unittest
from zope.testing import doctest
from zope.app.testing import setup

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.sqlscript.browser.sqlscript',
                             setUp=setup.placelessSetUp,
                             tearDown=setup.placelessTearDown),
        ))
    
if __name__ == '__main__': unittest.main()
