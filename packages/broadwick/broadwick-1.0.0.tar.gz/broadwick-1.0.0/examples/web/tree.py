import broadwick.utils
from broadwick.web import expose, website

class World():
    @expose
    def index():
        return

class Hello():
    @expose
    def index():
        return

    world = World()
         
class HelloTreeWorld():
    @expose
    def index(self):
        return 

    hello = Hello()

broadwick.utils.quickstart(HelloTreeWorld())
