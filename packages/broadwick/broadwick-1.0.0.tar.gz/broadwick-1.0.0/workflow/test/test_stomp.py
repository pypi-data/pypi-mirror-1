from workflow.control import Control
from workflow.control import StompDirector
from broadwick.messaging.twistedstomp import StompClient
from twisted.internet import reactor
import broadwick.web.utils
from broadwick.web.adapter.sa_adapter import SARequestAdapter
from broadwick.workflow.process_utils import dictFromClass
from workflow import config
from workflow.view import View
import logging


def run():
    logging.basicConfig(level=logging.DEBUG)
    control = Control(**dictFromClass(config, 'sql'))
    stomp = StompClient(**dictFromClass(config, 'stomp'))
    director = StompDirector(control, stomp)
    adapters = [
                SARequestAdapter(control.session),
                ]
    broadwick.web.utils.listen(View(), config.web.port, request_adapters=adapters )
    reactor.callLater(2, director.describe, "/queue/Sample")
    reactor.run()


if __name__ == '__main__':
    run()