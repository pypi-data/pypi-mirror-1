##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Test zope.publisher.browser doctests

$Id: test_browser.py 105429 2009-11-02 07:47:51Z ctheune $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite

__docformat__ = "reStructuredText"

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.publisher.browser'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
