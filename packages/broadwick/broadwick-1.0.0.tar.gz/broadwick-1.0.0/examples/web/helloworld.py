import broadwick.utils
from broadwick.web import expose

class HelloWorld:
    @expose
    def index(self):
        return '<b>Hello World</b>'

    @expose(content_type='text/xml', ext='.xml')
    def xml(self):
        return '<sparky>Hello World</sparky>'


if __name__== '__main__':
    broadwick.utils.quickstart(HelloWorld())

