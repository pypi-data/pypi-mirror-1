import simplejson
from broadwick.web.resource.base_res import BaseResource

# TODO, derive from simplejson.JSONEncodeer and add in types not currently supported
# see http://simplejson.googlecode.com/svn/tags/simplejson-1.8.1/docs/index.html

JSONEncoder = simplejson.JSONEncoder

class JsonResource(BaseResource):
    def __init__(self, cls=JSONEncoder, content_type='application/json', ext='.json', *args, **kwargs):
        BaseResource.__init__(self, ext=ext, *args, **kwargs)
        self.cls = cls
        self.content_type = content_type

    def formatResult(self, result, request):
        request.setHeader('content-type', self.content_type)
        # TODO: Need to do this to avoid potential security issues with JSON endpoints
        # request.setHeader('content-type', 'text/json-comment-filtered') 
        # but and then return '/*' + dumps(...) '*/'
        # make this a config option?
        return simplejson.dumps(result, cls=self.cls)
