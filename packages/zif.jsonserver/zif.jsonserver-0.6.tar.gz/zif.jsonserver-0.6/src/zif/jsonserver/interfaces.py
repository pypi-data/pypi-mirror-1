##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. 
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
# adapted from various xmlrpc interface files jwashin 2005-06-26

#2005-08-16 A few changes needed after a zope3 trunk change
#2005-11-07 Allowed IDefaultBrowserLayer in JSONRPCRequest.  This permits skin
#           lookups
#2006-06-19 Removed reference to IPresentation and added interface for 
#           Premarshaller jmw

from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPApplicationRequest,\
        IHTTPCredentials
from zope.interface import Interface
from zope.component.interfaces import IView
from zope.interface import Attribute
from zope.app.publisher.xmlrpc import IMethodPublisher
from zope.publisher.interfaces.xmlrpc import IXMLRPCPublication
from zope.app.publication.interfaces import IRequestFactory
from zope.publisher.interfaces.browser import IDefaultBrowserLayer, \
        IBrowserPage
from zope.schema.interfaces import TextLine


class IJSONRPCRequestFactory(IRequestFactory):
    """Browser request factory"""

class IJSONRPCPublisher(IPublishTraverse):
    """JSON-RPC Publisher
    like zope.publisher.interfaces.xmlrpc.IXMLRPCPublisher
    """
class IJSONRPCPublication(IXMLRPCPublication):
    """Object publication framework.
    like zope.publisher.interfaces.xmlrpc.IXMLRPCPublication
    """
class IJSONRPCRequest(IHTTPApplicationRequest, IHTTPCredentials, IDefaultBrowserLayer):
    """JSON-RPC Request
    like zope.publisher.interfaces.xmlrpc.IXMLRPCRequest
    """
    jsonID=Attribute("""JSON-RPC ID for the request""")

class IJSONReader(Interface):
    def read(aString):
        """read and interpret a string in JSON as python"""
        
class IJSONWriter(Interface):
    def write(anObject, encoding=None):
        """return a JSON unicode string representation of a python object
           Encode if encoding is provided.
        """

class IJSON(IJSONReader,IJSONWriter):
    """read and write JSON"""

#class IMethodPublisher(Interface):
#
#    """Marker interface for an object that wants to publish methods
#    see zope.app.publisher.xmlrpc.IMethodPublisher
#
#    it's commented here for completeness; actually, this uses
#    the one in zope.app.publisher.xmlrpc
#    """

class IJSONRPCView(IView):
    """JSONRPC View
    like zope.app.publisher.interfaces.xmlrpc.IXMLRPCView
    """
    
class IJSONRPCPremarshaller(Interface):
    """Premarshaller to remove security proxies"""
    def __call__():
        """return the object without proxies"""

class IJSONView(IBrowserPage):
    """A view that is a JSON representation of an object"""
    contentType = TextLine(title=u"content-type", default=u"application/json")
    def doResponse():
        """return the list or dict that is response for this view"""
    def doCacheControl():
        """set any cache headers that may be needed.  Default sends 'no-cache'
        to KHTML browsers.  May be extended/overridden in subclasses"""
