from twisted.web import resource, static
import broadwick.utils
from broadwick.web import expose_genshi

class HelloFormWorld:
    @expose_genshi(template='examples/web/resource/form.genshi')
    def index(self, name=None):
        return {'name' : name}

    resource = static.File('resource')

broadwick.utils.quickstart(HelloFormWorld())
