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
"""Unit tests for HTML Sanitizer
Original file z.a.publisher.xmlrpc/ftests.py
$Id: tests.py 23 2007-03-19 jwashin $
"""
import zope.interface
import zope.publisher.interfaces.browser
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite
import unittest

def test_suite():
    suite = unittest.TestSuite(doctest.DocFileSuite(
        'sanitizer_README.txt', 
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    suite.addTest(DocTestSuite('zif.xtemplate.lxmlhtmlutils'))
    return suite

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')
