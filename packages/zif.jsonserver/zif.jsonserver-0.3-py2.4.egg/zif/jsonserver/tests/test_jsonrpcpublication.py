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
"""JSON-RPC Publication Tests

modified from zope.app.publication.tests.test_xmlrpcpublication.py jwashin 2005-06-06

removed references to JSONRPCPresentation 20060619 jmw
altered imports to reflect zif namespace 20061216 jmw

"""
import unittest

from zope.app.publication.tests.test_zopepublication import \
     BasePublicationTests
from zope.app.publication.traversers import TestTraverser
from zif.jsonserver.jsonrpc import JSONRPCPublication
from zope.interface import Interface, implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces import NotFound
from zif.jsonserver.interfaces import IJSONRPCRequest
from zif.jsonserver.interfaces import IJSONRPCPublisher
from zif.jsonserver.jsonrpc import TestRequest
from zope.app.testing import ztapi

class SimpleObject(object):
    def __init__(self, v):
        self.v = v



class JSONRPCPublicationTests(BasePublicationTests):

    klass = JSONRPCPublication

    def _createRequest(self, path, publication, **kw):
        request = TestRequest(PATH_INFO=path, **kw)
        request.setPublication(publication)
        return request

    def testTraverseName(self):
        pub = self.klass(self.db)
        class C(object):
            x = SimpleObject(1)
        ob = C()
        r = self._createRequest('/x', pub)
        ztapi.provideView(None, IJSONRPCRequest, IJSONRPCPublisher,
                          '', TestTraverser)
        ob2 = pub.traverseName(r, ob, 'x')
        self.assertEqual(removeAllProxies(ob2).v, 1)

    def testDenyDirectMethodAccess(self):
        pub = self.klass(self.db)
        class I(Interface):
            pass

        class C(object):
            implements(I)

            def foo(self):
                return 'bar'

        class V(object):
            def __init__(self, context, request):
                pass
            implements(IJSONRPCPublisher)

        ob = C()
        r = self._createRequest('/foo', pub)

        ztapi.provideView(I, IJSONRPCPublisher, Interface, 'view', V)
        ztapi.setDefaultViewName(I, 'view', type=IJSONRPCPublisher)
        self.assertRaises(NotFound, pub.traverseName, r, ob, 'foo')


    def testTraverseNameView(self):
        pub = self.klass(self.db)
        from zif.jsonserver.jsonrpc import IJSONRPCPublisher
        class I(Interface):
            pass

        class C(object):
            implements(I)

        ob = C()

        class V(object):
            def __init__(self, context, request):
                pass
            implements(IJSONRPCPublisher)


        # Register the simple traverser so we can traverse without @@
        from zif.jsonserver.jsonrpc import IJSONRPCPublisher
        from zif.jsonserver.interfaces import IJSONRPCRequest
        from zope.app.publication.traversers import SimpleComponentTraverser
        ztapi.provideView(Interface, IJSONRPCRequest, IJSONRPCPublisher, '',
                          SimpleComponentTraverser)

        r = self._createRequest('/@@spam', pub)
        ztapi.provideView(I, IJSONRPCRequest, Interface, 'spam', V)
        ob2 = pub.traverseName(r, ob, '@@spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)

        ob2 = pub.traverseName(r, ob, 'spam')
        self.assertEqual(removeAllProxies(ob2).__class__, V)


    def testTraverseNameSiteManager(self):
        pub = self.klass(self.db)
        class C(object):
            def getSiteManager(self):
                return SimpleObject(1)
        ob = C()
        r = self._createRequest('/++etc++site',pub)
        ob2 = pub.traverseName(r, ob, '++etc++site')
        self.assertEqual(removeAllProxies(ob2).v, 1)
        
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(JSONRPCPublicationTests),
        ))

if __name__ == '__main__':
    unittest.main()
