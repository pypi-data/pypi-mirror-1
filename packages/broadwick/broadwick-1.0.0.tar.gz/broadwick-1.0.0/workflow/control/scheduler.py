from twisted.internet import reactor
from workflow import model
from broadwick.workflow.process_utils import AlreadyDoneException
import logging
import datetime, time
import sys

def register(type, target):
    return Scheduler(target)


class Scheduler(object):

    def __init__(self, control):
        self.control = control
        self.schedules = {}
        self.flushing = None
    
    def event(self, eventId):
        session = self.control.session()
        event = session.query(model.ScheduledEvent).get(eventId)
        try:
            nextEvent = None
            if event.work_item is not None:
                try:
                    self.control.perform(session, event.work_item)
                except AlreadyDoneException: pass
            else:
                process = model.Process.getLatestVersion(session, event.cause.process)
                self.control.start(session, process)
                nextEvent = event.cause.getNextEvent(datetime.datetime.now(),
                                                     datetime.timedelta(0,60))
            event.done()
            del self.schedules[event.id]
            logging.info('done event %s' % event.id)
            session.commit()
            if nextEvent is not None:
                self.schedule(nextEvent)
        except:
            logging.exception('error event[%s]' % event.id)
            err = sys.exc_info()
            event.err = 'error: %s %s' % (str(err[0]), str(err[1]))
        finally:
            session.close()


    def schedule(self, event):
        # this will schedule events within the next 24hr period
        delta = event.starts - datetime.datetime.now()
        if delta.days <= 0:
            if delta > datetime.timedelta():
                secs = delta.seconds + float(delta.microseconds)/1000000
            else:
                secs = 1
            logging.info('scheduled %s in %s' % (event, secs))
            assert event.id != None, 'event not committed %r' % event
            self.schedules[event.id] = reactor.callLater(secs, self.event, event.id)
    
    
    def activate(self, session, schedule):
        schedule.active = not schedule.active
        if schedule.active == True:
            event = schedule.getNextEvent(now=datetime.datetime.now())
            if event is not None:
                session.commit()
                self.schedule(event)
        else:
            for key, value in self.schedules.items():
                event = session.query(model.ScheduledEvent).get(key)
                if event.cause == schedule:
                    logging.info('descheduling %r' % event)
                    value.cancel()
                    del self.schedules[key]
                    session.delete(event)


    def run(self):
        session = self.control.session()
        logging.info('clearing schedule')
        # clear old schedules
        query = 'UPDATE %s SET %s="1900-1-1 00:00:00" WHERE %s is NULL' % (
                                    model.ScheduledEvent.__tablename__, 
                                    'completed',
                                    'work_item_id')
                                    
        logging.debug(query)
        session.execute(query)
        # remove any existing tasks
        for key, value in self.schedules.items():
            value.cancel()
            del self.schedules[key]

        logging.debug('loading schedule')
        # reload callAgains
        for event in model.ScheduledEvent.scheduledEvents(session):
            self.schedule(event)
        # create new from schedules
        for schedule in model.Schedule.activeSchedules(session):
            event = schedule.getNextEvent(now=datetime.datetime.now())
            if event is not None:
                session.commit()
                self.schedule(event)

        #call at midnight plus 5 seconds to build the next day.
        now = datetime.datetime.now()
        tomorrow = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1.0)
        time2t = tomorrow - now
        self.flushing = reactor.callLater(5+time2t.seconds, self.run)
        session.commit()
        session.close()


    def nextRun(self):
        return self.flushing.time - time.time()
