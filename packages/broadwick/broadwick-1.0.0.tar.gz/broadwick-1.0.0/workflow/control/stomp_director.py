from sets import Set
from pydispatch import dispatcher
from broadwick.messaging.events import LoggedInEvent, ConnectionLostEvent
from broadwick.workflow.process_utils import ContextToStomp, StompToContext
from workflow.control.base_director import BaseDirector
from workflow import model
import logging
import datetime


class StompDirector(BaseDirector):

    def __init__(self, control, client, replyTo=None):
        BaseDirector.__init__(self, control)
        self.client = client
        self.destinations = {}
        self.monitor_destinations = {}
        self.monitor_mask = '/topic/ActiveMQ.Advisory.Consumer.Queue.'
        self.replyTo = replyTo or '/queue/process'
        self.pinged = {}
        self.client.publishSubscribe(self.replyTo, self.onMessage)
        self.client.broadcastSubscribe(self.monitor_mask+'>', self.onMessage)
        dispatcher.connect(self._dispatched, LoggedInEvent, client)
        dispatcher.connect(self._dispatched, ConnectionLostEvent, client)
        
        
    def _dispatched(self, signal=None, sender=None, *args, **kwargs):
        logging.debug('signaled %r %r' % (signal, sender))
        
    def actors(self):
        return self.monitor_destinations.keys()
        
    def pingstate(self, activityName):
        try:
            queue = self.destinations[activityName]
        except KeyError:
            raise 'unregistered activity: %s' % activityName
        try:
            lastPinged = self.pinged[queue]
            return datetime.datetime.now() - lastPinged
        except KeyError:
            raise 'not pinged %s' % activityName


    def ping(self, activityName, expires=None):
        try:
            queue = self.destinations[activityName]
        except KeyError:
            raise Exception('unregistered activity: %s' % activityName)
        try:
            del self.pinged[queue]
        except KeyError: pass
        self.client.broadcast(queue, '', headers={ 'process-activity':'__ping__',
                                                  'reply-to': self.replyTo,
                                                  'expires': str(expires or 0)
                                                  })


    def getDestination(self, activityName):
        return self.destinations.get(activityName, None)
    
    def getDestinations(self):
        """returns a dictionary of destinations and number of subscribers"""
        return self.monitor_destinations


    def describe(self, queue):
        if queue in self.monitor_destinations.keys():
            logging.debug('requesting description %s' % queue)
            self.client.publish(queue, body='', headers={
                 'process-activity':'__describe__',
                 'reply-to': self.replyTo,
                 })


    def register(self, activityName, destination):
        logging.debug ("register")
        self.destinations[activityName] = destination
        logging.debug('registered %s' % activityName)
                    

    def perform(self, session, context):
        if self.client.isConnected() is False:
            return False
        activity = context.activity.name
        perform = context.activity.resolve().name
        destination = self.destinations.get(perform)
        if destination:
            self.client.publish(destination, body=ContextToStomp(context.context()),
                                headers={
                                     'correlation-id' : str(context.id),
                                     'process-activity' : activity,
                                     'process-perform' : perform,
                                     'reply-to': self.replyTo })
            self.control.begun(context, destination)
            return True
        return False
        

    def onMessage(self, headers, body, client):
        logging.debug('%s\n%s' % (str(headers), body.replace('\n', ' ')))
        try:
            if headers.get('type', None) =='Advisory':
                destination = headers['destination']
                if destination.startswith(self.monitor_mask):
                    destination = '/queue/%s' % destination[len(self.monitor_mask):]
                    if destination != self.replyTo:
                        consumers = int(headers['consumerCount']) 
                        if consumers == 0:
                            del self.monitor_destinations[destination]
                            for key,value in self.destinations.items():
                                if value == destination:
                                    del self.destinations[key]
                            logging.info('no longer available: %s' % destination)
                        elif self.monitor_destinations.has_key(destination) is False:                            
                            self.monitor_destinations[destination] = consumers                     
                            logging.debug(self.monitor_destinations)
                            session = self.control.session()
                            activities = model.Service.get_activity_names(session, destination)
                            if activities:
                                for activity in activities:
                                    self.register(activity, destination)
                                self.control.canWork()
                                logging.info('available for work: %s' % destination)
                            session.close()
                        else:
                            self.monitor_destinations[destination] = consumers
                            logging.info('workers: %s (%s)' % (destination,consumers))
            elif headers.has_key('__describe__'):
                queue = headers['__describe__']
                session = self.control.session()
                try: 
                    activities = model.Service.load_description(session, queue, body)
                    for activity in activities:
                        self.register(activity, queue)
                    session.commit()
                except:
                    logging.exception('registering %s' % queue)
                    session.rollback()
                session.close()
                client.ack(headers['message-id'])
                logging.debug('description %s' % queue)
            elif headers.has_key('__ping__'):
                self.pinged[headers['__ping__']] = datetime.datetime.now()
                client.ack(headers['message-id'])
            elif headers.has_key('__startProcess__'):
                processName = headers['__startProcess__']
                try:
                    context = StompToContext(body)
                    self.control.start(processName, context)
                    logging.debug('started %s' % processName)
                except:
                    logging.exception('starting %s' % processName)
                client.ack(headers['message-id'])
            elif headers.has_key('__error__'):        
                self._with_item(headers['correlation-id'],
                                self.control.error, 
                                headers['__error__'], body)
                client.ack(headers['message-id'])
            elif headers.has_key('__split__'):
                context = StompToContext(body)
                choice = headers.has_key('__choice__') and int(headers['__choice__']) or None
                self._with_item(headers['correlation-id'],
                                self.control.split, 
                                context,
                                choice)
                client.ack(headers['message-id'])
                logging.debug('split %s' % headers['correlation-id'])
            elif headers.has_key('__callAgain__'):
                context = StompToContext(body)
                self._with_item(headers['correlation-id'],
                                self.control.schedule,
                                context, int(headers['__callAgain__']))
                client.ack(headers['message-id'])
                logging.debug('callAgain %s' % headers['correlation-id'])
            elif headers.has_key('__choice__'):
                context = StompToContext(body)
                self._with_item(headers['correlation-id'],
                                self.control.done,
                                context, int(headers['__choice__']))
                client.ack(headers['message-id'])
                logging.debug('choice %s' % headers['correlation-id'])
            elif headers.has_key('__complete__'):
                context = StompToContext(body)
                self._with_item(headers['correlation-id'],
                                self.control.complete,
                                context)
                client.ack(headers['message-id'])
                logging.debug('complete %s' % headers['correlation-id'])
            elif headers.has_key('__done__'):
                context = StompToContext(body)
                try:
                    self._with_item(headers['correlation-id'],
                                   self.control.done,
                                   context=context)
                except:
                    logging.exception('handling %s' % headers)
                client.ack(headers['message-id'])
                logging.debug('handled %s' % headers)
            else:
                client.ack(headers['message-id'])
                logging.warn('unhandled %s' % headers)
        except:
            logging.exception('receiving message %s' % headers)
