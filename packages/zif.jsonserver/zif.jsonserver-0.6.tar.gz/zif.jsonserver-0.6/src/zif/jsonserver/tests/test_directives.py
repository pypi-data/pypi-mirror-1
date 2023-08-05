##############################################################################
#
# Copyright (c) 2001 - 2005 Zope Corporation and Contributors.
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
"""Test 'jsonrpc' ZCML Namespace directives.

mod from zope.app.publisher.xmlrpc.tests.test_directives.py jwashin 2005-06-06
altered imports for zif namespace jwashin 2006-12-16
"""
import unittest

from zope.configuration import xmlconfig
from zope.configuration.exceptions import ConfigurationError
from zope.app.component.tests.views import IC, V1, Request
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory

from zif.jsonserver.interfaces import IJSONRPCRequest

from zif import jsonserver
from zif.jsonserver import jsonrpc
from zope.interface import implements
from zope.component import queryMultiAdapter, getMultiAdapter

#Michael Dudzik wanted this for his test setup
import zif.jsonserver.tests

request = Request(IJSONRPCRequest)

class Ob(object):
    implements(IC)

ob = Ob()

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def testView(self):
        self.assertEqual(
            queryMultiAdapter((ob, request), name='test'), None)
        xmlconfig.file("jsonrpc.zcml", jsonserver.tests)
        view = queryMultiAdapter((ob, request), name='test')
        self.assert_(V1 in view.__class__.__bases__)
        self.assert_(jsonrpc.MethodPublisher in view.__class__.__bases__)

    def testInterfaceProtectedView(self):
        xmlconfig.file("jsonrpc.zcml", jsonserver.tests)
        v = getMultiAdapter((ob, request), name='test2')
        v = ProxyFactory(v)
        self.assertEqual(v.index(), 'V1 here')
        self.assertRaises(Exception, getattr, v, 'action')

    def testAttributeProtectedView(self):
        xmlconfig.file("jsonrpc.zcml", jsonserver.tests)
        v = getMultiAdapter((ob, request), name='test3')
        v = ProxyFactory(v)
        self.assertEqual(v.action(), 'done')
        self.assertRaises(Exception, getattr, v, 'index')

    def testInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("jsonrpc.zcml", jsonserver.tests)
        v = getMultiAdapter((ob, request), name='test4')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testDuplicatedInterfaceAndAttributeProtectedView(self):
        xmlconfig.file("jsonrpc.zcml", jsonserver.tests)
        v = getMultiAdapter((ob, request), name='test5')
        self.assertEqual(v.index(), 'V1 here')
        self.assertEqual(v.action(), 'done')

    def testIncompleteProtectedViewNoPermission(self):
        self.assertRaises(ConfigurationError, xmlconfig.file,
                          "jsonrpc_error.zcml", jsonserver.tests)

    def test_no_name(self):
        xmlconfig.file("jsonrpc.zcml", jsonserver.tests)
        v = getMultiAdapter((ob, request), name='index')
        self.assertEqual(v(), 'V1 here')
        v = getMultiAdapter((ob, request), name='action')
        self.assertEqual(v(), 'done')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
