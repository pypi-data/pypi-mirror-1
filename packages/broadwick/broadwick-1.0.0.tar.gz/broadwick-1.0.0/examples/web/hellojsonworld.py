import broadwick.utils
from broadwick.web import expose_json

class HelloJsonWorld:
    @expose_json
    def index(self):
        return {'msg' : 'Hello World'}

broadwick.utils.quickstart(HelloJsonWorld())

