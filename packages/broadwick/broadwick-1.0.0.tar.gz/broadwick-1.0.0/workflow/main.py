from twisted.internet import reactor
import broadwick.web.utils  
import broadwick.utils.log
from broadwick.web.adapter import SARequestAdapter, BasicAuthRequestAdapter
from broadwick.messaging.twistedstomp import StompClient
from broadwick.web.xmlrpc import DocXMLRPC
from broadwick.workflow.process_utils import dictFromClass
from workflow.control.control import Control
from workflow.control.stomp_director import StompDirector
from workflow.view import View
from workflow import config
from workflow import model
import logging


class LoginRequestAdapter(BasicAuthRequestAdapter):
    
    def login(self, request):
        try:
            user = request.sa_session.query(model.Person).filter_by(email=request.getUser(), 
                                                                    password=request.getPassword()).one()
            logging.debug('auth loaded %s' % request.getUser())
            return [role.name for role in user.roles]
        except:
            logging.debug('failed to auth %s' % request.getUser())


def run():
    broadwick.utils.log.initialise_logging(log_level=logging.INFO)
    control = Control(**dictFromClass(config, 'sql'))
    stomp = StompClient(**dictFromClass(config, 'stomp'))
    director = StompDirector(control, stomp)
    xmlrpc_view = DocXMLRPC(control,
                     allow_none = True, 
                     server_title = config.xml.title,
                     server_name = config.xml.title,
                     server_documentation = config.xml.description,
                     
                     )
    broadwick.web.utils.listen(xmlrpc_view, config.xml.port)
    adapters = [
                SARequestAdapter(control.session),
#                LoginRequestAdapter('intent')
                ]
    broadwick.web.utils.listen(View(), config.web.port, request_adapters=adapters )
    reactor.run()


if __name__ == '__main__':
    run()

