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
"""Functional tests for JSON Views
Original file z.a.publisher.xmlrpc/ftests.py
$Id: ftests.py 23 2006-12-16 17:08:48Z jwashin $
Mod by jmw 7 Oct 06 for JSON Views
"""
import zope.interface
import zope.app.folder.folder
import zope.publisher.interfaces.browser
from zope.app.testing import ztapi, functional, setup
from zope.testing import doctest

def setUp(test):
    setup.setUpTestAsModule(test, 'zif.xtemplate.README')

def tearDown(test):
    setup.tearDownTestAsModule(test)

def test_suite():
    return functional.FunctionalDocFileSuite(
        'README.txt', setUp=setUp,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='test_suite')
