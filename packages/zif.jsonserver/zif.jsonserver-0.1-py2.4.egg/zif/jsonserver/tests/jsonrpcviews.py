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
"""JSON-RPC Views test objects

adapted from zope.publisher.tests.xmlrpcviews
jwashin 2005-06-06
altered import to reflect zif namespace jmw 20061216

"""
from zope.interface import Interface, implements
from zif.jsonserver.interfaces import IJSONRPCPublisher

class IC(Interface): pass

class V1(object):
    implements(IJSONRPCPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request
    def action(self):
        return 'done'
    def index(self):
        return 'V1 here'

class VZMI(V1):
    pass

class R1(object):
    def __init__(self, request):
        self.request = request

    implements(IJSONRPCPublisher)

class RZMI(R1):
    pass

