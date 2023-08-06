from twisted.web import resource, static
import broadwick.utils
from broadwick.web import expose_genshi

class HelloGenshiWorld:
    @expose_genshi(template='examples/web/resource/hello.genshi')
    def index(self):
        return {'msg' : 'Hello World'}

    resource = static.File('resource')

broadwick.utils.quickstart(HelloGenshiWorld())
