from sqlalchemy import *
from sqlalchemy.orm import *
from workflow.model.base import Base
from sqlalchemy.sql.expression import and_
from workflow.model.enum_type import Enum
import time
import datetime
import logging

SCHEDULE_PERIODS = ['none', 'hourly', 'daily', 'weekly']

class Schedule(Base):
    __tablename__='schedule'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    process =  Column(String(80), nullable=False)
    starting =  Column('starts', Time)
    ending =  Column('ends', Time)
    every =  Column(Time)
    period = Column(Enum(values=SCHEDULE_PERIODS), default=SCHEDULE_PERIODS[0])
    isMon = Column(Boolean, default=False)
    isTue = Column(Boolean, default=False)
    isWed = Column(Boolean, default=False)
    isThu = Column(Boolean, default=False)
    isFri = Column(Boolean, default=False)
    isSat = Column(Boolean, default=False)
    isSun = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
                
    def __repr__(self):
        return '<Scheduled id=%s, details=%r>' % (self.id, self.to_tuple())
    
    
    def from_tuple(self,starts,ends,every,dayMask,active):
        logging.info(str([starts,ends,every,dayMask,active]))
        starts = starts and datetime.datetime.strptime(starts,'%H:%M') or None
        ends = ends and datetime.datetime.strptime(ends,'%H:%M') or None
        every = every and datetime.datetime.strptime(every,'%H:%M') or None
        self.starting=starts
        self.ending=ends
        self.every=every
        self.isSun= 'Sun' in dayMask
        self.isMon= 'Mon' in dayMask
        self.isTue= 'Tue' in dayMask
        self.isWed= 'Wed' in dayMask
        self.isThu= 'Thu' in dayMask
        self.isFri= 'Fri' in dayMask
        self.isSat= 'Sat' in dayMask
        self.active=active
        
        
    def to_tuple(self):
        """ Returns (starts, ends, every, dayMask, active, processName, id)"""
        return (self.starting and self.starting.strftime('HH:MM') or None,
                self.ending and self.ending.strftime('HH:MM') or None,
                self.every and self.every.strftime('HH:MM') or None,
                '%s%s%s%s%s%s%s' % (self.isSun and 'S' or 's',
                      self.isMon and 'M' or 'm',
                      self.isTue and 'T' or 't',
                      self.isWed and 'W' or 'w',
                      self.isThu and 'T' or 't',
                      self.isFri and 'F' or 'f',
                      self.isSat and 'S' or 's',
                      ),
                self.active,
                self.process,
                self.id)    
    
    @classmethod
    def activeSchedules(cls, session):
        return session.query(cls).filter_by(active=True)
    
    
    def getNextEvent(self, now, after=None):
        result = None
        if after is not None:
            now = now + after
        day = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][int(now.strftime('%w'))]
        if eval('self.is%s' % day):
            if self.starting < now.time() and self.ending and self.ending > now.time():
                if self.every is None:
                    result = ScheduledEvent(starts=now, cause=self)
                else:
                    tdelta = datetime.timedelta(0, (self.every.hour*60 + self.every.minute)*60)
                    starts = datetime.datetime(now.year, now.month, now.day, self.starting.hour,
                                               self.starting.minute)
                    while starts < now:
                        starts = starts + tdelta
                    result = ScheduledEvent(starts=starts, cause=self)
            elif self.starting > now.time():
                starts = datetime.datetime(now.year, now.month, now.day, 
                                           self.starting.hour,
                                           self.starting.minute)
                result = ScheduledEvent(starts=starts, cause=self)
        return result


    def nextEvent(self, session):
        if self.active is True:
            return session.query(ScheduledEvent).filter(and_(ScheduledEvent.cause==self,
                                                             ScheduledEvent.completed==None))\
                                                .order_by(ScheduledEvent.starts.desc()).first()
        return None
    
    def nextEventTime(self, session, format=None):
        if self.active:
            next = self.nextEvent(session)
            if next and format:
                return next.starts.strftime(format)
            return next
    

class ScheduledEvent(Base):
    __tablename__='schedule_event'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    cause_id = Column(Integer, ForeignKey('schedule.id'), nullable=True)
    cause = relation(Schedule, primaryjoin=cause_id==Schedule.id, uselist=False, backref='events')
    started = Column(DateTime, nullable=False, default=datetime.datetime.now)
    completed = Column(DateTime)
    err = Column('failure', String(1024), nullable=True) 
    # used to schedule specific item call backs   
    work_item_id = Column(Integer, ForeignKey('workitem.id'), nullable=True)
    work_item = relation('WorkItem', primaryjoin='ScheduledEvent.work_item_id==WorkItem.id', 
                         uselist=False, backref='schedules')
    starts = Column(DateTime, default=None)
    
    def __repr__(self):
        return '<ScheduledEvent id=%s, cause=%r, item=%r>' % (self.id, self.cause, self.work_item)
    
    def done(self):
        self.completed = datetime.datetime.now()
        logging.info('completed %s' % self.id)
    
    @classmethod
    def scheduledEvents(cls, session):
        return session.query(cls).filter_by(completed=None).order_by(cls.started)
    
    @classmethod
    def scheduleWorkItem(cls, item, when=0):
        event =  ScheduledEvent()
        event.starts = event.started + datetime.timedelta(0,when)
        event.started = None
        item.schedules.append(event)
        return event
    
