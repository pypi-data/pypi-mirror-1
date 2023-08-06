from broadwick.web.utils import ReDirectException, AuthenticationException
from twisted.web.util import redirectTo
from twisted.internet.defer import maybeDeferred
import logging
import inspect

from twisted.internet import defer
from twisted.web import resource, server

class BaseResource(resource.Resource):
    def __init__(self, content_type=None, content_disposition=None, ext='.html', *args, **kwargs):
        # This resource is created by decorators - at the time
        # of creation the function being decorated will not be
        # bound to an object. We expect to be given the bound
        # function at a later stage before rendering
        self.func = None
        self.ext = ext
        self.content_disposition = content_disposition
        self.content_type = content_type
        self.request_adapters = []
        
    
    def before_request(self, request, params):
        for adapter in self.request_adapters:
            result = adapter.before_request(request, self, params)
            if result is not None:
                return result


    def after_request(self, request, result=None):
        for adapter in self.request_adapters:
            adapter.after_request(request, result)


    def render(self, request):
        params = {}
        for param, value in request.args.items():
            if len(value) == 1:
                value = value[0]
            params[param] = value

        argspec = inspect.getargspec(self.func)
        funcparams = argspec[0]
        funcdefaults = argspec[3] or []

        for param, default in zip(funcparams[::-1], funcdefaults[::-1]):
           params.setdefault(param, default)

        try:
            params[self.func._request_param] = request
        except AttributeError:
            pass
                
        if self.content_type is not None:
            request.setHeader('content-type', self.content_type)
        if self.content_disposition is not None:
            request.setHeader('content-disposition', self.content_disposition)

        request.setHeader('Expires', "Mon, 26 Jul 1997 05:00:00 GMT")
        request.setHeader('Cache-Control', 'no-cache, must-revalidate')
        request.setHeader('Pragma', 'no-cache')

        deferred = maybeDeferred(self._handleRequest, request, params)
        deferred.addCallbacks(self.writeDeferredResult, 
                              self.funcFailed,
                              callbackArgs=(request, ),
                              errbackArgs=(request, )
                              )\
                .addErrback(self.deferredFailed, request)
        return server.NOT_DONE_YET

    def _handleRequest(self, request, params):
        self.before_request(request, params)
        return self.func(**params)

    def funcFailed(self, result, request):
        if isinstance(result.value, ReDirectException):
            self.after_request(request)
            request.write(redirectTo(result.value.url, request))
            request.finish()
            return
        elif isinstance(result.value, AuthenticationException):
            self.after_request(request)
            request.write(result.value.message)
            request.finish()
            return
        return result

    def writeDeferredResult(self, result, request):
        if not request.finished:
            body = self.formatResult(result, request)
            self.after_request(request, result)
            request.setHeader('content-length', str(len(body)))
            request.write(body)
            request.finish()

    def deferredFailed(self, result, request):
        self.after_request(request, result)
        request.processingFailed(result)
