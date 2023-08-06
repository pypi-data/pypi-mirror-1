
from broadwick.web.resource.base_res import BaseResource


class CsvResource(BaseResource):
    def __init__(self, filename=None, content_type='text/csv', ext='.csv', *args, **kwargs):
        BaseResource.__init__(self, ext=ext, *args, **kwargs)
        self.content_type = content_type
        self.filename = filename

    def formatResult(self, result, request):
        request.setHeader('content-type', self.content_type)
        request.setHeader('content-disposition', 'attachment; filename=%s.csv' % self.filename)
        return result

