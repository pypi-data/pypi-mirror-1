from genshi.template import TemplateLoader

from broadwick.web.resource.base_res import BaseResource

class GenshiResource(BaseResource):
    """We expect a dictionary for results.
    If a template filename is given when we are instantiated we will pass the results
    along to the filename.
    If no template filename is given we expect the results to be a dictionary with
    data members 'template' and 'data'. template will be the template to load and 
    data will be the data to pass to that template

    TODO: that feels like a hack. Is there a better way?
    """
    loader = TemplateLoader(".", auto_reload=True)
    def __init__(self, template, method='xhtml', encoding='utf-8', ext='.html', *args, **kwargs):
        # TODO: The Dojo toolkit seems barf
        # when xhtml+xml is used. E.g. BorderContainer tests do not work, hence the
        # default content type is text/html
        kwargs.setdefault('content_type', 'text/html')
        BaseResource.__init__(self, ext=ext, *args, **kwargs)
        self.template = template
        self.method = method
        self.encoding=encoding

    def formatResult(self, result, request):
        if self.template is None:
            filename = result['template']
            result = result['data']
        else:
            filename = self.template

        template = self.loader.load(filename)
        return template.generate(**result).render(method=self.method, encoding=self.encoding)

