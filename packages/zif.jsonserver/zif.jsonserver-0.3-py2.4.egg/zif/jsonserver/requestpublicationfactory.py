# class for json-rpc publication factory.
# like zope.app.publication.requestpublicationfactories, which
# registers SOAPFactory, XMLRPCFactory, HTTPFactory, and BrowserFactory.
# JSONRPCFactory is similar to those.

from zope.app.publication.interfaces import IRequestPublicationFactory
from interfaces import IJSONRPCRequestFactory
from zope import component
from jsonrpc import JSONRPCRequest, JSONRPCPublication
from zope.interface import implements

class JSONRPCFactory(object):
    implements(IRequestPublicationFactory)
    
    def canHandle(self,environment):
        return True
        
    def __call__(self):
        request_class = component.queryUtility(
            IJSONRPCRequestFactory, default=JSONRPCRequest)
        return request_class, JSONRPCPublication
