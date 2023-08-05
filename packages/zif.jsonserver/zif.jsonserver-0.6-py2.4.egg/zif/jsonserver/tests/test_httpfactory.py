##############################################################################
#
# Copyright (c) 2003 - 2005 Zope Corporation and Contributors.
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
"""Tests for the JSONRPC Publication Request Factory.

modified from zope.app.publication.tests.test_requestpublicationfactories.py jwashin 2005-11-06
Altered imports to reflect zif namespace

"""
from unittest import TestCase, TestSuite, main, makeSuite

from StringIO import StringIO
from zope import component,interface
from zope.publisher.browser import BrowserRequest
from zope.publisher.http import HTTPRequest
from zif.jsonserver.jsonrpc import JSONRPCRequest
from zope.component.testing import PlacelessSetup
from zif.jsonserver.interfaces import IJSONRPCRequestFactory
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.http import HTTPPublication
from zif.jsonserver.requestpublicationfactory import JSONRPCFactory
from zif.jsonserver.jsonrpc import JSONRPCPublication

from zope.app.testing import ztapi

class DummyRequestFactory(object):
    def __call__(self, input_stream, env):
        self.input_stream = input_stream
        self.env = env
        return self

    def setPublication(self, pub):
        self.pub = pub

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        self.__factory = HTTPPublicationRequestFactory(None)
        self.__env =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0'
            }

    def test_jsonrpcfactory(self):
        jsonrpcrequestfactory = DummyRequestFactory()
        interface.directlyProvides(
            jsonrpcrequestfactory, IJSONRPCRequestFactory)
        component.provideUtility(jsonrpcrequestfactory)
        env = self.__env
        factory = JSONRPCFactory()
        self.assertEqual(factory.canHandle(env), True)
        request, publication = factory()
        self.assertEqual(isinstance(request, DummyRequestFactory), True)
        self.assertEqual(publication, JSONRPCPublication)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
