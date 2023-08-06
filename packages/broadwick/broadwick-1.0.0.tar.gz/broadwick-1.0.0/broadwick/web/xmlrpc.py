import xmlrpclib
import logging
from DocXMLRPCServer import XMLRPCDocGenerator
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

from twisted.internet import defer
from twisted.web import server, resource
from twisted.web.xmlrpc import Handler
import twisted

from broadwick.web.utils import expose

def expose_xmlrpc(obj):
    """Expose a function or object for XMLRPC"""
    def _expose(o):
        if not hasattr(obj, '_exposed_xmlrpc'):
            o._exposed_xmlrpc = True
        return o

    if obj is not None:
        return _expose(obj)
    else:
        return _expose

def isexposed(f):
    # xmlrpclib.ServerProxy instances always return True for 
    # hasattr(f, <any string you like>). We work around this here.
    # We could check __dict__ (or equivalently vars(f)) but that seems
    # to be overkill when the problem is specifically with ServerProxy
    return hasattr(f, '_exposed_xmlrpc') and not isinstance(f, xmlrpclib.ServerProxy)

def exposeds(obj):
    for attr in dir(obj):
        value = getattr(obj, attr)
        if isexposed(value):
            if hasattr(value, '__call__'):
                yield attr, value
            else:
                # Recurse
                for a, v in exposeds(value):
                    yield '%s.%s' % (attr, a), v

class XMLRPCDispatcher(SimpleXMLRPCDispatcher, XMLRPCDocGenerator):
    def __init__(self, control, allow_none, encoding):
        import sys
        if sys.version_info[:2] >= (2, 5):
            SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)
        else:
            SimpleXMLRPCDispatcher.__init__(self)
        XMLRPCDocGenerator.__init__(self)

class XMLRPCResource(resource.Resource):
     # Error codes for Twisted, if they conflict with yours then
    NOT_FOUND = 8001
    FAILURE = 8002

    def __init__(self, control,
                 register_introspection = False,
                 server_title = None,
                 server_name = None,
                 server_documentation = None,
                 allow_none=False, encoding='UTF-8',
                 use_datetime=False
                 ):
        self.allow_none = allow_none
        self.use_datetime = use_datetime
        self.encoding = encoding
        self.dispatcher = XMLRPCDispatcher(control, allow_none, encoding)
        for method, func in exposeds(control):
            self.dispatcher.register_function(func, method)

        if register_introspection:
            self.dispatcher.register_introspection_functions()

        if server_title is not None:
            self.dispatcher.set_server_title(server_title)
        if server_name is not None:
            self.dispatcher.set_server_name(server_name)
        if server_documentation is not None:
            self.dispatcher.set_server_documentation(server_documentation)

    def documentation(self):
        return self.dispatcher.generate_html_documentation()

    def render_POST(self, request):
        request.content.seek(0, 0)
        request.setHeader("content-type", "text/xml")

        args, method = xmlrpclib.loads(request.content.read(), self.use_datetime)

        defer.maybeDeferred(self.dispatcher._dispatch, method, args).addErrback(
                self._ebRender
            ).addCallback(
                self._cbRender, request
            )

        return server.NOT_DONE_YET

    def _ebRender(self, failure):
        """This is a copy from twisted.web.xmlrpc.XMLRPC with a decent error message"""
        if isinstance(failure.value, xmlrpclib.Fault):
            return failure.value
        return xmlrpclib.Fault(self.FAILURE, failure.getErrorMessage())

    def _cbRender(self, result, request):
        """This is a copy from twisted.web.xmlrpc.XMLRPC with allow_none and encoding set 
        (twisted 8.2 also does that)
        """
        if isinstance(result, Handler):
            result = result.result
        if not isinstance(result, xmlrpclib.Fault):
            result = (result,)
        try:
            s = xmlrpclib.dumps(result, methodresponse=True, 
                                allow_none=self.allow_none, encoding=self.encoding)
        except Exception, e:
            f = xmlrpclib.Fault(self.FAILURE, "Can't serialize output: %s" % (e,))
            s = xmlrpclib.dumps(f, methodresponse=True, allow_none=self.allow_none)
        request.setHeader("content-length", str(len(s)))
        request.write(s)
        request.finish()

class DocXMLRPC:
    """A web view with an XMLRPC interface available at /RPC2 and documentation available at /index.html
    """
    def __init__(self, control, **kwargs):
        self.RPC2 = XMLRPCResource(control, **kwargs)

    @expose
    def index(self):
        return self.RPC2.documentation()


