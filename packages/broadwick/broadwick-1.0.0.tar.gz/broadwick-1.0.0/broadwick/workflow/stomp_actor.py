from twisted.internet import defer
from twisted.python import failure
from pydispatch import dispatcher
from broadwick.messaging.twistedstomp import StompClient
from broadwick.messaging.events import LoggedInEvent, ConnectionLostEvent
from broadwick.workflow.base_actor import BaseActor
from broadwick.workflow.process_utils import ClientContext, StompToContext,\
    ContextToStomp
import logging

class StompActor(BaseActor):
    
    def __init__(self, client, process_queue='/queue/process'):
        BaseActor.__init__(self)
        self.client = client
        self.process_queue = process_queue
        self.messageLock = defer.DeferredLock()
        dispatcher.connect(self._dispatched, LoggedInEvent, client)
        dispatcher.connect(self._dispatched, ConnectionLostEvent, client)
        
        
    def _dispatched(self, signal=None, sender=None, *args, **kwargs):
        logging.debug('signaled %r %r' % (signal, sender))

        
    def onMessage(self, headers, body, client):
        # We need to make sure that these are processed one at a time.
        # Acquire a lock and handle the call
        # Once finished, whether we get an error or not, ack the client the release the lock
        self.messageLock.acquire()\
                .addCallback(self.onMessage_Message, headers, body, client)\
                .addBoth(self.ackClient, headers, body, client)


    def onMessage_Message(self, reason, headers, body, client):
        """I handle a message with the command MESSAGE

        I may or may not return a deferred result.
        """
        activity = headers.get('process-activity')
        if activity == '__describe__':
            client.publish(headers['reply-to'],
                        self.describe(),
                        headers={ '__describe__': headers['destination'] })
        elif activity == '__ping__':
            client.publish(headers['reply-to'],
                    'hi there!',
                    headers={ '__ping__': self.q })
        elif activity and headers.has_key('correlation-id'):
            context = ClientContext(dict=StompToContext(body),
                                     workItemId = headers['correlation-id'],
                                     activity = activity,
                                     # kmanley 23 aug 07, added new process-perform header, 
                                     # but we need to conditionally check for it in order to 
                                     # not break older clients
                                     perform = headers.get('process-perform', activity),
                                     replyTo = headers['reply-to'],
                                     service = self)

            # doWork may or may not return a deferred.
            #  If doWork suceeds call doneWork
            #  If doneWork or doWork fails, pass the error to errorInWork
            return defer.maybeDeferred(self.doWork, context)\
                    .addCallback(self.doneWork, context)\
                    .addErrback(self.errorInWork, context)
        else:
            logging.warn('unhandled message: %s' % str(headers))
            
            
    @classmethod
    def doWebWork(cls, context):
        """The mashalled context worked by the registed action"""
        return defer.maybeDeferred(cls.instance.doWork, context)\
                    .addCallback(cls.instance.doneWork, context)\
                    .addErrback(cls.instance.errorInWork, context)
        

    def ackClient(self, reason, headers, body, client):
        if isinstance(reason, failure.Failure):
            logging.exception(reason)
        logging.debug('Acking client')
        try:
            client.ack(headers['message-id'])
        finally:
            self.messageLock.release()


    def doneWork(self, reason, context):
        assert context.replyTo is not None
        assert context.workItemId is not None
        self.client.publish(context.replyTo,
                        body=ContextToStomp(context.data),
                        headers={'__done__': 'True',
                                 'correlation-id': context.workItemId })
        
    def split(self, context):
        assert context.replyTo is not None
        assert context.workItemId is not None
        self.client.publish(context.replyTo,
                    body=ContextToStomp(context.data),
                    headers={'correlation-id': context.workItemId,
                     '__split__': 'True' })
        
    def callAgain(self, context, when):
        assert context.replyTo is not None
        assert context.workItemId is not None
        self.client.publish(context.replyTo,
                    body=ContextToStomp(context.data),
                    headers={'correlation-id': context.workItemId,
                     '__callAgain__': when })
    
    def choice(self, context, choice):
        assert context.replyTo is not None
        assert context.workItemId is not None
        self.client.publish(context.replyTo,
                    body=ContextToStomp(context.data),
                    headers={'correlation-id': context.workItemId,
                     '__choice__': choice })
        
    def complete(self, context):
        assert context.replyTo is not None
        assert context.workItemId is not None
        self.client.publish(context.replyTo,
                    body=ContextToStomp(context.data),
                    headers={'correlation-id': context.workItemId,
                     '__complete__': context.workItemId })
        
    def error(self, context, err, msg):
        assert context.replyTo is not None
        assert context.workItemId is not None
        self.client.publish(context.replyTo,
                    body=msg,
                    headers={'correlation-id': context.workItemId,
                     '__error__':err })
                    
    def startProcess(self, processName, context):
        self.client.publish(self.process_queue,
                         body=ContextToStomp(context),
                         headers={ '__startProcess__': processName })




def quickstart_stomp(target, queue=None, host='localhost', port=61613, 
                     login=None, passcode=None, clientId=None, reconnect=True,
                     process_queue='/queue/process'):
    from twisted.internet import reactor
    if queue is None:
        queue = '/queue/%s' % target.__class__.__name__
    if login is None:
        login = queue
    stomp = StompClient(host=host, port=port, login=login, passcode=passcode,
                        clientId=clientId, reconnect=reconnect)
    client = StompActor(stomp, process_queue=process_queue)
    client.addTarget(target)
    stomp.publishSubscribe(queue, client.onMessage)
    
    def _logged_in(signal, sender):
        logging.info('listening on %s for: %r' % (queue, client.activities()))
    dispatcher.connect(_logged_in, LoggedInEvent, stomp)
    
    reactor.run()
    