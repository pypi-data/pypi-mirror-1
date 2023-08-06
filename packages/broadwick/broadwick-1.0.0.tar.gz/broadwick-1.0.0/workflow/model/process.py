from sqlalchemy import *
from sqlalchemy.orm import *
from workflow.model.base import Base
import sets
import logging
import pickle
import datetime


activity_role = Table('activity_role', Base.metadata,
    Column('activity_id', Integer, ForeignKey('activity.id')),
    Column('role_id', Integer, ForeignKey('role.id')),
    mysql_engine='InnoDB'
    )
activity_condition = Table('activity_condition', Base.metadata,
    Column('activity_id', Integer, ForeignKey('activity.id')),
    Column('condition_id', Integer, ForeignKey('act_condition.id')),
    mysql_engine='InnoDB'
    )
activity_result = Table('activity_result', Base.metadata,
    Column('activity_id', Integer, ForeignKey('activity.id')),
    Column('result_id', Integer, ForeignKey('act_result.id')),
    mysql_engine='InnoDB'
    )

class _context(object):
    
    def __getitem__(self, name):
        name = str(name)
        for v in self.work_values:
            if v.name == name:
                return pickle.loads(v.value)
        raise KeyError(name)

    def __setitem__(self, name, value):
        name = str(name)
        if self.context().get(name) != value:
            for wv in self.work_values:
                if wv.name == name:
                    wv.value = pickle.dumps(value)
                    return
            self.work_values.append(WorkValue(name=name, value=pickle.dumps(value)))
        
    def context(self, result=None):
        if result is None:
            result = {}
        for value in list(self.work_values):
            result[value.name] = pickle.loads(value.value)
        return result

    def context_by_key(self):
        """Helper function to provide a sorted context by key"""
        result = self.context()
        keys = result.keys()
        keys.sort()
        for key in keys:
            yield key,result[key]


class Activity(Base, _context):
    __tablename__='activity'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    name =  Column(String(80), nullable=False, unique=True)
    notes = Column(Text, default=None)
    roles = relation('Role', secondary=activity_role)
    
    def __repr__(self):
        return '<Activity name=%r>' % self.name
    
    def resolve(self):
        return self
    
    @classmethod
    def find_or_create(cls, session, name):
        try:
            return session.query(cls).filter_by(name=name).one()
        except:
            result = cls(name=name)
            session.add(result)
            return result
        
    
class Process(Base, _context):
    __tablename__='process'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    name =  Column(String(80), nullable=False)
    version = Column(Integer, default=0)
    created =  Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self):
        return '<Process(id=%s, name=%r)>' % (self.id, self.name)

    def defineInitActivities(self, activities):
        self.definePreCondition(None, activities)

    def definePreCondition(self, activity, conditions, join=False, display=None):
        condition = ActCondition(activity=activity,join=join)
        self.pre_activities.append(condition)
        for activity in conditions:
            condition.conditions.append(activity)

    def definePostCondition(self, activity, results, choice=False, display=None):
        result = ActResult(activity=activity, choice=choice)
        self.post_activities.append(result)
        for activity in results:
            result.results.append(activity)
    
    def getInitActivities(self):
        result = []
        for condition in self.pre_activities:
            if condition.activity == None:
                result = result + list(condition.conditions)
        return result
    
    def getPostActivities(self, activity, choice=0):
        result = []
        for condition in self.post_activities:
            if condition.activity == activity :
                if condition.choice == True :
                    try:
                        result.append( condition.results[choice] )
                    except IndexError:
                        logging.exception('choice out of range of choices')
                else :
                    result = result + condition.results
        return result
    
    def getPreActivities(self, activity, items):
        completed = []
        todo = []
        joinContext = {}
        for item in items:
            joinContext.update(item.context())            
            if item.completed is not None:
                completed.append(item.activity)
            else:
                todo.append(item.activity)
        result = []
        for condition in [pre for pre in self.pre_activities if pre.activity is not None]:
            pre_conditions = list(condition.conditions)
            if activity in pre_conditions:
                if condition.join is True:
                    if condition.activity in completed:
                        continue
                    canAdd = True
                    for con in pre_conditions:
                        if con in todo:
                            canAdd = False
                            break
                    if canAdd is True:
                        result.append((condition.activity, joinContext)) 
                else:
                    if activity in condition.conditions:
                        result.append((condition.activity,None))
        logging.info('activity: %r' % activity )
        logging.info('todo: %r' % todo )
        logging.info('completed: %r' % completed )
        logging.info('result: %r' % result )
        return result

    def getActivities(self):
        result = sets.Set()
        for condition in self.pre_activities:
            if condition.activity is not None:
                result.add(condition.activity)
            result = result | sets.Set(condition.conditions)
        for condition in self.post_activities:
            if condition.activity is not None:
                result.add(condition.activity)
            result = result | sets.Set(condition.results)      
        return result
        
    def getDestroys(self):
        result = []
        for act in self.getActivities():
            acts = self.getPostActivities(act)
            if len(acts) == 0:
                result.append(act)
        for condition in self.pre_activities:
            for act in condition.conditions:
                if condition.activity is not None and act in result:
                    result.remove(act)
        return result
    
    def flows_on_date(self, session, date):
        from_date = datetime.datetime(date.year, date.month, date.day)
        date = date + datetime.timedelta(1)
        to_date = datetime.datetime(date.year, date.month, date.day)
        return session.query(Workflow)\
                            .filter(and_(Workflow.process_id==self.id,
                                         Workflow.started >= from_date,
                                         Workflow.started < to_date))\
                            .order_by(Workflow.started.desc())
    
    @classmethod
    def getLatestVersion(cls, session, name):
        return session.query(cls).filter_by(name=name).order_by(cls.version.desc()).first()


class ActCondition(Base):
    __tablename__='act_condition'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    join = Column('joincondition', Boolean, default=False)    
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    process = relation(Process, primaryjoin=process_id==Process.id, uselist=False, backref="pre_activities")    
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=True)
    activity = relation(Activity, primaryjoin=activity_id==Activity.id, uselist=False)     
    conditions = relation(Activity, secondary=activity_condition)
    created =  Column(DateTime, nullable=False, default=datetime.datetime.now)



class ActResult(Base):
    __tablename__='act_result'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    choice = Column('choiceresult', Boolean, default=False)    
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    process = relation(Process, primaryjoin=process_id==Process.id, uselist=False, backref="post_activities")    
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=True)
    activity = relation(Activity, primaryjoin=activity_id==Activity.id, uselist=False) 
    results = relation(Activity, secondary=activity_result)
    created =  Column(DateTime, nullable=False, default=datetime.datetime.now)


class Workflow(Base, _context):
    __tablename__='workflow'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey('process.id'), nullable=False)
    process = relation(Process, primaryjoin=process_id==Process.id, uselist=False, backref="workflows")
    has_errors = Column(Boolean, default=False)
    started =  Column(DateTime, nullable=False, default=datetime.datetime.now)
    ended =  Column(DateTime, nullable=True) 

    def __repr__(self):
        return '<Workflow(id=%s, process=%r)>' % (self.id, self.process.name)

    def context(self, context=None):
        return _context.context(self, self.process.context())

    def getWork(self):
        result = []
        for item in self.work_items:
            if item.handled == False:
                result.append(item)
        return result
    

class WorkItem(Base, _context):
    __tablename__='workitem'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey('workflow.id'), nullable=False)
    workflow = relation(Workflow, primaryjoin=workflow_id==Workflow.id, uselist=False, backref='work_items')   
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=True)
    activity = relation(Activity, primaryjoin=activity_id==Activity.id, uselist=False)
    queue = Column(String(80))
    started =  Column(DateTime, nullable=False, default=datetime.datetime.now) 
    waited = Column(Integer, default=0)
    completed =  Column(DateTime, nullable=True) 
    handled = Column(Boolean, default=False) 
    msg = Column(String(1024))
    has_errors = Column(Boolean, default=False)
    err = Column(String(1024))
    
    def __repr__(self):
        return '<WorkItem(id=%s, activity=%r, workflow=%s, process=%r)>' % (self.id, self.activity.name,
                                                                self.workflow.id, self.workflow.process.name)
    
    def context(self):
        result = self.workflow.context()
        result = self.activity.context(result)
        return _context.context(self, result)
    
    def isAutomatic(self):
        for role in self.activity.roles:
            if role.name == 'automatic':
                return True
        return False

    
    
class WorkValue(Base):
    __tablename__='workvalue'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)  
    name =  Column(String(80), nullable=False)
    value = Column(Text())
    activity_id = Column(Integer, ForeignKey('activity.id'))
    activity = relation(Activity, primaryjoin=activity_id==Activity.id, uselist=False, backref='work_values')
    process_id = Column(Integer, ForeignKey('process.id'))
    process = relation(Process, primaryjoin='WorkValue.process_id==Process.id', uselist=False, backref='work_values')
    workflow_id = Column(Integer, ForeignKey('workflow.id'))
    workflow = relation(Workflow, primaryjoin=workflow_id==Workflow.id, uselist=False, backref='work_values')
    workitem_id = Column(Integer, ForeignKey('workitem.id'))
    workitem = relation(WorkItem, primaryjoin=workitem_id==WorkItem.id, uselist=False, backref='work_values') 
    created =  Column(DateTime, nullable=False, default=datetime.datetime.now)
    
    
