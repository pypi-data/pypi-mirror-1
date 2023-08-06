from twisted.web import xmlrpc
from workflow import model
from workflow.control.base_director import BaseDirector
import logging

class XMLRPCDirector(BaseDirector):

    def __init__(self, control, name, actor_host, actor_port):
        BaseDirector.__init__(self, control)
        self.actor = xmlrpc.Proxy('http://%s:%i/RPC2' % (actor_host, actor_port))
        self.name = name
        self.activities = []
        self.busy = False
    
    def actors(self):
        return [self.name]
        
        
    def describe(self, name):
        if name == self.name:
            logging.debug('describe %s' % name)
            self.actor.callRemote('describe').addCallback(self._description, name)\
                                             .addErrback(self._catchFailure)
        
        
    def _description(self, result, name):
        session = self.control.session()
        try: 
            self.activities = model.Service.load_description(session, name, result)
            session.commit()
        except:
            logging.exception('registering %s' % name)
            session.rollback()
        session.close()
        logging.debug('description %s' % name)
        
        
        
    def perform(self, session, context):
        activity = context.activity.name
        perform = context.activity.resolve().name
        if self.busy is False and activity in self.activities:   
            logging.debug('performing %s' % context)         
            self.actor.callRemote('perform', context.id, activity, context.context(), perform)\
                                  .addCallback(self._performed)\
                                  .addErrback(self._catchFailure)
            self.control.begun(context, self.name)
            self.busy = True
            return True
        return False 


    def _performed(self, result): 
        logging.debug('performed %s' % result)         
        self.busy = False
        if result.get('result') == '__error__':        
            self._with_item(result['correlation-id'],
                            self.control.error, 
                            result['err'], result['msg'])
            logging.debug('error %s' % result['correlation-id'])
        elif result.get('result') == '__split__':
            self._with_item(result['correlation-id'],
                            self.control.split, 
                            result['context'],
                            result.get('choice'))
            logging.debug('split %s' % result['correlation-id'])
        elif result.get('result') == '__callAgain__':
            self._with_item(result['correlation-id'],
                            self.control.schedule,
                            result['context'], int(result['when']))
            logging.debug('callAgain %s' % result['correlation-id'])
        elif result.get('result') == '__choice__':
            self._with_item(result['correlation-id'],
                            self.control.done,
                            result['context'], int(result['choice']))
            logging.debug('choice %s' % result['correlation-id'])
        elif result.get('result') == '__complete__':
            self._with_item(result['correlation-id'],
                            self.control.complete,
                            result['context'])
            logging.debug('complete %s' % result['correlation-id'])
        elif result.get('result') == '__done__':
            try:
                self._with_item(result['correlation-id'],
                               self.control.done,
                               context=result['context'])
            except:
                logging.exception('handling %s' % result)
            logging.debug('handled %s' % result)
        else:
            logging.warn('unhandled %s' % result)   
            

    def _catchFailure(self, failure):
        logging.warn("Error %s: %s" % (self.name, failure.getErrorMessage())) 
        logging.exception(failure)
        self.busy = False 
