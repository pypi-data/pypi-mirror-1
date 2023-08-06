from broadwick.web.resource.base_res import BaseResource
from StringIO import StringIO

class StringResource(BaseResource):
    def __init__(self, ext='.html', *args, **kwargs):
        BaseResource.__init__(self, ext=ext, *args, **kwargs)

    def formatResult(self, result, request):
        if isinstance(result, StringIO):
            return result.getvalue()
        return result
        



