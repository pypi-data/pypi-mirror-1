import broadwick.utils
from broadwick.web import expose, website, auth_roles, request_param, redirect
from broadwick.web.adapter.auth_adapter import TupleAuthRequestAdapter
import logging

class World():
    @expose
    @auth_roles(roles=['admin'])
    @request_param('request')
    def index(self, request):
        return "<a href='../'>hello</a> <a href='../../'>home</a> has role 'user': %s" % request.hasRoles(['user'])

class Hello():
    @expose
    @auth_roles(roles=['admin'])    
    @request_param('request')
    def index(self, request):
        if request.hasRoles(['user']):
            return 'hi there'
        return "<a href='../'>home</a> <a href='world/'>world</a>"

    world = World()
         
class HelloTreeWorld():
    @expose
    @auth_roles(roles=['user'])
    def index(self):
        return """
                <a href='hello/index.html'>hello</a> 
                <a href='hello/world/index.html'>world</a> 
                <a href='logout.html'>logout</a>"""

    @expose
    @request_param('request')
    def logout(self, request):
        TupleAuthRequestAdapter.logout(request)
        redirect('index.html')

    hello = Hello()


user_tuples = [
               ('peterb','pb',['user']),
               ('pc',None,['user']),
               ('peter.bunyan',None,['user','admin']),
               ('jonm','jm',['admin','user']),
               ]
adapter_list = [ 
                TupleAuthRequestAdapter('test', user_tuples) 
                ]
broadwick.utils.quickstart(HelloTreeWorld(), log_level=logging.DEBUG, request_adapters=adapter_list)
