import zope.app.testing.functional as functional
from zope.testing import doctest
from zif.jsonserver.jsonrpc import JSONRPCRequest, JSONRPCPublication
 
class HTTPCaller(functional.HTTPCaller):
    def chooseRequestClass(self, method, path, environment):
        """Choose and return a request class and a publication class"""
        request_cls, publication_cls = super(HTTPCaller, self).chooseRequestClass(method, path, environment)
        
        content_type = environment.get('CONTENT_TYPE', '')
        is_json = content_type.startswith('application/json-rpc')
    
        if method in ('GET', 'POST', 'HEAD'):
            if (method == 'POST' and is_json):
                request_cls = JSONRPCRequest
                publication_cls = JSONRPCPublication
    
        return request_cls, publication_cls
    
def FunctionalDocFileSuite(*paths, **kw):
    globs = kw.setdefault('globs', {})
    globs['http'] = HTTPCaller()
    globs['getRootFolder'] = functional.getRootFolder
    globs['sync'] = functional.sync

    kw['package'] = doctest._normalize_module(kw.get('package'))

    kwsetUp = kw.get('setUp')
    def setUp(test):
        functional.FunctionalTestSetup().setUp()

        if kwsetUp is not None:
            kwsetUp(test)
    kw['setUp'] = setUp

    kwtearDown = kw.get('tearDown')
    def tearDown(test):
        if kwtearDown is not None:
            kwtearDown(test)
        functional.FunctionalTestSetup().tearDown()
    kw['tearDown'] = tearDown

    if 'optionflags' not in kw:
        kw['optionflags'] = (doctest.ELLIPSIS
                             | doctest.REPORT_NDIFF
                             | doctest.NORMALIZE_WHITESPACE)

    return doctest.DocFileSuite(*paths, **kw)
