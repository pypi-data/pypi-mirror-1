from broadwick.web import expose, expose_genshi, expose_json, redirect, auth_roles, request_param
from broadwick.workflow.process_utils import SyncContext
from twisted.web import static
from types import ListType
from workflow.control.control import Control
from workflow import config
from workflow.crud.crud import Crud
from workflow.control.xmlrpc_director import XMLRPCDirector
import decimal
import logging
import datetime
import model
import os


def _to_json(obj):
    if hasattr(obj, '_sa_class_manager'):
        """JSONify SQLAlchemy objects."""
        props = {}
        for key in obj.__dict__:
            if not key.startswith('_sa_'):
                props[key] = _to_json(getattr(obj, key))
        return props
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return str(obj)
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    return obj

def _sync_context(values, context, key, value):
    if type(key) == ListType:
        for i, k in enumerate(key):
            if k is not None and k is not '':
                item = context.get(k)
                if repr(item) != value[i]:
                    item = eval(value[i])
                values[k] = item
    elif value is not None and value is not '':
        item = context.setdefault(key, None)
        if repr(item) != value:
            item = eval(value)
            values[key] = item

def resource_path(f=None):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource')
    if f:
        path = os.path.join(path, f)
    return path


class View(object):
    
    def __init__(self):
        self.resource =  static.File(resource_path())
        self.favicon = static.File(resource_path('favicon.ico'))
        self.dojo = static.File(config.dojo.path)
        self.control = Control.CONTROL
        self.admin = Crud(model.base.Base)
    
    @expose    
    @request_param('request')
    def add(self, request, name=None, host=None, port=None):
        XMLRPCDirector(self.control, name, host, int(port))
        redirect('index.html')
    
    @expose_genshi(template=resource_path('index.genshi'))
    @request_param('request')
    def index(self, request, **kwargs):
        return {}
    
    @expose_genshi(template=resource_path('_actors.genshi'))
    @request_param('request')
    def _actors(self, request):
        return {'actors': self.control.actors()}
    
    @expose_genshi(template=resource_path('_processes.genshi'))
    @request_param('request')
    def _processes(self, request):
        return {'processes': request.sa_session.query(model.Process).all()}
    
    @expose_genshi(template=resource_path('_workflows.genshi'))
    @request_param('request')
    def _workflows(self, request, process=None, flow=None, date=None):
        if date:
            logging.info(date)
            date = datetime.datetime.strptime(date,'%Y-%m-%d')
        else:
            date = datetime.datetime.now()
        process = request.sa_session.query(model.Process).get(process)
        flows = process.flows_on_date(request.sa_session, date)
        return { 'process': process,
                 'workflows': flows, 'flow': flow, 'date': date }
        
    
    @expose_genshi(template=resource_path('_workitems.genshi'))
    @request_param('request')
    def _workitems(self, request, flow=None):
        return { 'flow': request.sa_session.query(model.Workflow).get(flow) }
    
    @expose_genshi(template=resource_path('_workcontext.genshi'))
    @request_param('request')
    def _workcontext(self, request, work=None):
        item = request.sa_session.query(model.WorkItem).get(work)
        context = item.context()
        keys = context.keys()
        keys.sort()
        return { 'start_context': context, 'keys': keys }
    
    @expose_genshi(template=resource_path('_start.genshi'))
    @request_param('request')
    def _start(self,request,id,key=None,value=None,action=None,remove=None,add=None):
        logging.info((id,key,value,action,remove,add))
        process = request.sa_session.query(model.Process).get(int(id))
        error = message = None
        if key is None:
            values = process.context()
        else:
            context = process.context()
            values = {}
            _sync_context(values, context, key, value)
        keys = values.keys()
        keys.sort()
        if remove is not None and remove is not '':
            del values[keys[int(remove)]]
            del keys[int(remove)]
        elif (add is None or add is '') and action == "Start '%s'" % process.name:
            self.control.start(request.sa_session, process, values)
            request.sa_session.commit()
            message = "Workflow begun..."
        return {'id':process.id, 'name': process.name, 'start_context': values, 'keys': keys,
                'error': error, 'submit': "Start '%s'" % process.name, 'action': '_start.html',
                'message': message }
     

    @expose_genshi(template=resource_path('_start.genshi'))
    @request_param('request')
    def _run(self,request,id,key=None,value=None,action=None,remove=None,add=None):
        logging.info((id,key,value,action,remove,add))
        workItem = request.sa_session.query(model.WorkItem).get(int(id))
        error = message = None
        if key is None:
            values = workItem.context()
        else:
            context = workItem.context()
            values = {}
            _sync_context(values, context, key, value) 
        keys = values.keys()
        keys.sort()
        if remove is not None and remove is not '':
            del values[keys[int(remove)]]
            del keys[int(remove)]
        elif (add is None or add is '') and action == "Run '%s'" % workItem.activity.name:
            SyncContext(workItem, values)
            if self.control.perform(request.sa_session, workItem):
                request.sa_session.commit()
                message = "workitem running..."
            else:
                error = 'Unable to run!'
        return {'id':workItem.id, 'name': workItem.activity.name, 'start_context': values, 'keys': keys,
                'error' : error, 'submit': "Run '%s'" % workItem.activity.name, 'action': '_run.html',
                'message': message }
        
        
    @expose_genshi(template=resource_path('_schedule.genshi'))
    @request_param('request')
    def _schedule(self, request, schedule=None, process=None, starting=None, every=None, ending=None, day=None, remove=None):
        if remove is not None:
            schedule = request.sa_session.query(model.Schedule).get(int(remove))
            request.sa_session.delete(schedule)
            request.sa_session.commit()
            redirect('_schedule.html')
        if schedule is not None:
            schedule = request.sa_session.query(model.Schedule).get(int(schedule))
            if process is not None:
                schedule.from_tuple(starting,ending,every,day,schedule.active)
                request.sa_session.commit()
                redirect('_schedule.html')
        elif process is not None:
            process = request.sa_session.query(model.Process).get(int(process))            
            schedule = model.Schedule(process=process.name)
            schedule.from_tuple(starting,ending,every,day,False)
            request.sa_session.add(schedule)
            request.sa_session.commit()
            redirect('_schedule.html')
        return { 'processes': request.sa_session.query(model.Process).all(),
                 'schedule': schedule, 
                 'schedules': request.sa_session.query(model.Schedule).all(),
                 'sa_session': request.sa_session }
        

    @expose    
    @request_param('request')
    def _activate_schedule(self, request, id=None):
        schedule = request.sa_session.query(model.Schedule).get(int(id))
        self.control.scheduler.activate(request.sa_session, schedule)
        request.sa_session.commit()
        redirect('_schedule.html')
        
    @expose_genshi(template=resource_path('_describe.genshi'))
    @request_param('request')
    def _describe(self, request, actor=None, load=None):
        if load:
            self.control.describe(load)
            actor = load
        activities = model.Service.get_activity_names(request.sa_session, actor)
        return { 'actor': actor, 'activities': activities }
    
    
    @expose_genshi(template=resource_path('test.genshi'))
    @request_param('request')
    def test(self, request, section=None):
        return {'section': section }
    
    

