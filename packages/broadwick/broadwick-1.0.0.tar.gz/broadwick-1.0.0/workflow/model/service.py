from sqlalchemy import *
from sqlalchemy.orm import *
from workflow.model.base import Base
import xml.etree.ElementTree as ET
from workflow.model.process import Process, Activity
from workflow.model.person import Role
import pickle
import logging
import datetime


class Service(Base):
    __tablename__='service'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    name = Column(String(80))
    description = Column(Text, default=None)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=None)
    version = Column(Integer, default=0)
    
    @classmethod
    def find_or_create(cls, session, name, description):
        """
        Does nothing if a queue exists with the specified name and the specified description
        Otherwise, creates a new ServiceDescription for that queue

        """
        result = session.query(Service).filter_by(name=name, version=0).first()

        if result:
            if description == result.description:
                logging.debug ("Latest version of %s already has this description. Won't do anything" %
                              name)
                return result
            else:
                oldest = session.query(Service).filter_by(name=name, version=0).first()
                if oldest:
                    result.version=oldest.version+1
                else:
                    result.version=1

        # There is no service description for this queue,
        # or there is one and it has a different description.
        # Make a new one, and version it
        result = Service(name=name, description=description, version=0)
        session.add(result)
        return result
    
    
    def _checkProcessCreation (self, session, process):
        """
        1. Check the service description created time for the specified queue
        2. If this time > process created time: return True
        """
        service_desc = Service.getLatestVersion(session,  self.name)
        if service_desc is None or service_desc.created > process.created:
            return True
        else:
            return False

    @classmethod
    def getLatestVersion(cls, session, name):
        return session.query(cls).filter_by(name=name).order_by(cls.version.desc()).first()
        
    
    @classmethod
    def _load_description(cls, session, name, description):
        service = cls.find_or_create(session, name, description)
        logging.debug ("loadDescription")
        root = ET.fromstring(description)
        result = []
        activities = root.findall('activity')
        for activity in activities:
            name = activity.get('name')
            logging.debug('define activity %s' % name)
            act = Activity.find_or_create(session, name)
            if act.notes != activity.findtext('notes'):
                act.notes = activity.findtext('notes')
            auto = activity.get('automatic')
            if auto == 'True':
                role = Role.find_or_create(session, 'automatic')
                if role not in act.roles:
                    act.roles.append(role)
            display = activity.get('display')
            if display and display != 'None':
                act.display = display
            perform = activity.get("perform")
            if perform:
                act.perform = perform
            result.append(name)
    
        processes = root.findall('process')
        for process in processes:
            name = process.get('name')
            logging.debug('define process %s' % name)
            # this will return the latest version of this named process
            p = session.query(Process).filter_by(name=name, version=0).first()
            # we know what the queue is that affects this process
            # if any of those have creation time greater than the process creation time,
            # we need to create a new process version. 
            new_process_version = False
            if p:
                logging.debug ("Got process %s version %s" % (name, p.version))
                new_process_version = service._checkProcessCreation(session, p)
    
            if new_process_version or p is None:
                # if we are here, we need to create a new process in the database
                # and all the other things necessary like work items, activity conditions & results
                
                p = Process(name=name)
                session.add(p)
                p.notes = process.findtext('notes')
                for value in process.findall('context/value'):
                    if value.attrib.has_key('type') and value.attrib['type']=='python':
                        try:
                            p[value.attrib['key']] = eval(value.text)
                        except:
                            logging.exception('passing %s' % value.attrib['key'])
                            raise
                    else:
                        try:
                            p[value.attrib['key']] = pickle.loads(value.text)
                        except:
                            logging.exception("#%s#" % value.text)
                            p[value.attrib['key']] = value.text
                activities = []
                for init in process.findall("init"):
                    activities.append(Activity.find_or_create(session, init.get('activity')))
                p.defineInitActivities(activities)
                for pre in process.findall('precondition'):
                    r = Activity.find_or_create(session, pre.get('result'))
                    activities = []
                    for cond in pre.findall("condition"):
                        activities.append(Activity.find_or_create(session, cond.get('activity')))
                    join = pre.get('join')=='True'
                    # this puts things in act_condition_activity and act_result_activity
                    p.definePreCondition(r, activities, join)
                for post in process.findall('postcondition'):
                    r = Activity.find_or_create(session, post.get('activity'))
                    choice = post.get('choice')=='True'
                    activities = []
                    for cond in post.findall("result"):
                        activities.append(Activity.find_or_create(session, cond.get('activity')))
                    # this puts things in act_condition_activity and act_result_activity
                    p.definePostCondition(r, activities, choice)
        return result

    @classmethod
    def load_description(cls, session, name, description):
        return cls._load_description(session, name, description)
    
    @classmethod
    def get_activity_names(cls, session, name):
        result = []
        service = cls.getLatestVersion(session, name)
        if service:
            root = ET.fromstring(service.description)
            activities = root.findall('activity')
            for activity in activities:
                result.append(activity.get('name'))   
        return result
    
         
    
