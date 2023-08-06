from broadwick.web.xmlrpc import expose_xmlrpc
from workflow.control.scheduler import Scheduler
from workflow.model.base import Base
from broadwick.workflow import process_utils
from workflow import model
import datetime
import logging

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy.orm import *


class WorkSessionExtension(SessionExtension):
    def after_commit(self, session):
        logging.debug("after commit!")
        Control.CONTROL.canWork()


class Control(object):
    
    CONTROL=None
    
    def __init__(self, url, create=True, drop=False, echo=False):
        Control.CONTROL = self
        self.directors = []
        engine = create_engine(url, echo=echo)
        Base.metadata.bind = engine
        self.worker = WorkSessionExtension()
        self._Session = sessionmaker(bind=engine, autoflush=True, autocommit=False, extension=self.worker)
        if drop is True:
            Base.metadata.drop_all(engine)
        if create is True:
            Base.metadata.create_all(engine)
        self.scheduler = Scheduler(self)
        self.scheduler.run()
            
            
    @expose_xmlrpc 
    def startProcess(self, processName, context=None):
        """Start a process by name, optionally providing a picklable dictionary as context"""
        session = self.session()
        self.start(session, processName, context)
        session.commit()
        return True

            
    def register_director(self, director):
        self.directors.append(director)
        
        
    def describe(self, actor):
        for director in self.directors:
            director.describe(actor)
            
    def actors(self):
        result = []
        for director in self.directors:
            result = result + director.actors()
        return result
        
        
    def session(self):
        return self._Session()
    
    def start(self, session, process, context=None):
        workflow = model.Workflow(process=process)
        session.add(workflow)        
        if context is not None:
            for key in context.keys():
                workflow[key] = context[key]
        context = workflow.context()
        work = []
        for activity in process.getInitActivities():
            logging.debug ("Spawning activity %s for workflow %s" % (activity.name, process))
            work.append(self._spawn(workflow, activity, context))
        return workflow
        
    
    def _spawn(self, workflow, activity, context):
        item = model.WorkItem(activity=activity)
        workflow.work_items.append(item)
        process_utils.SyncContext(item, context)
        return item


    def _after(self, item, choice):
        logging.info('after %r' % item)
        work = []
        context = item.context()
        if choice is not None:
            post_activities = item.workflow.process.getPostActivities(item.activity, choice)
        else:
            post_activities = item.workflow.process.getPostActivities(item.activity)
        for activity in post_activities:
            logging.info ("Activity %s is a post-condition of %s" % (item.activity.name, activity.name))
            work.append(self._spawn(item.workflow, activity, context))
        for activity, joinContext in item.workflow.process.getPreActivities(item.activity, list(item.workflow.work_items)):
            logging.info ("Activity %s is a pre-condition of %s" % (item.activity.name, activity.name))
            if joinContext:
                for key,value in joinContext.iteritems():
                    context[key]=value
            work.append(self._spawn(item.workflow, activity, context))
        return work
            
    
    def begun(self, item, queue=None):        
        item.handled=True
        item.queue = queue
        
    def done(self, item, context, choice=None):
        process_utils.SyncContext(item, context)
        item.completed=datetime.datetime.now()
        result = self._after(item, choice)
        self.completed(item.workflow)
        return result
        
    def wait(self, item, context, times=1):
        process_utils.SyncContext(item, context)
        result = False
        if item.waited < times:
            item.waited = item.waited + 1
            session.commit()
            result = True
        return result     

    def split(self, item, context, choice=None):        
        process_utils.SyncContext(item, context)
        item.err=None
        item.msg=None
        item.handled=False
        result = self._after(item, choice)
        return result

    def complete(self, item, context):        
        process_utils.SyncContext(item, context)
        item.completed=datetime.datetime.now()
        self.completed(item.workflow)
        
    def completed(self, workflow):
        if len(workflow.getWork()) == 0:
            workflow.ended = datetime.datetime.now()
        
    def error(self, item, err, msg):
        item.err=str(err)[:1023]
        item.msg=str(msg)[:1023]
        item.hasErrors=True
        item.workflow.hasErrors=True

    def schedule(self, item, context, when=0):
        process_utils.SyncContext(item, context)
        if when > 0:
            result = model.ScheduledEvent.scheduleWorkItem(item, when)
            return result
        else:
            item.handled = False
    
    def work(self):
        session = self.session()
        for workItem in [w for w in self.getWork(session) if w.isAutomatic()]:
            if self.perform(session, workItem):
                session.commit()
        session.close()
        
    def perform(self, session, workItem):
        for director in self.directors:
            if director.perform(session, workItem):
                logging.debug('accepting %r -> %r ' % (workItem, director))
                return True
        return False
    
    def canWork(self):
        from twisted.internet import reactor
        reactor.callLater(0, self.work)
    
    def getWork(self, session):
        return session.query(model.WorkItem).filter_by(handled=False, waited=0).order_by(model.WorkItem.started)
    
