import broadwick.utils
from broadwick.web import expose, request_param
from twisted.internet.defer import inlineCallbacks, succeed, returnValue

class HelloHeaderWorld:
    @expose
    @request_param('request')
    def index(self, request):
        request.setHeader('content-type', 'text/plain')
        return '<b>Hello World</b>'

    @inlineCallbacks
    @expose
    @request_param('request')
    def inline_test(self, request):
        yield succeed(None)
        request.setHeader('content-type', 'text/plain')
        returnValue('<b>Hello World Bingy Bingy Boing</b>')

broadwick.utils.quickstart(HelloHeaderWorld())
