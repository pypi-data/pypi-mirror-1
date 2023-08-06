"""
  Author:     Peter Bunyan
  Program:    subscriber

  Date:       Jan. 24, 2007

  Description:    Twisted Stomp test subscriber.
                  
"""
from broadwick.messaging.twistedstomp import StompClient
from broadwick.utils.log import initialise_logging
from twisted.internet import reactor
import time, logging

EXAMPLE_TOPIC = '/topic/stomp_test'
EXAMPLE_QUEUE = '/queue/stomp_test'


class Subscriber(object):
    def __init__(self):
        self.count = 0
        self.delay = 0

    def onMessage(self, headers, body, client):
        # logging.info ("Received: %s" % body)
        now = time.time()

        if '_start' in headers:
            self.count = 1
            self.delay = 0
            self.start = float(headers['_start'])
        else:
            self.count += 1

        self.delay += now - float(headers['_sent'])
        if '_count' in headers:
            if self.count == int(headers['_count']):
                logging.info('Counts match - received all %d messages' % self.count)
            else:
                logging.error('Count mismatch - expected %s but got %s' % (headers['_count'], self.count))
            logging.info('Avg delay: %f secs' % (self.delay / self.count))
            if now != self.start:
                logging.info('Throughput: %f msgs / sec' % (self.count / (now - self.start)))

    def onPublishedMessage(self, header, body, client):
        logging.info('Got published message: %s' % body)
        client.ack(header['message-id'])

def main():

    from optparse import OptionParser, OptionGroup
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('--verbose', action='store_true', help='log more')
    parser.add_option('--login', default='guest', help='STOMP login. default: %default')
    parser.add_option('--passcode', default='guest', help='STOMP passcode. default: %default')
    parser.add_option('--server-type', default='AMQ', help='STOMP server type. Can be AMQ or RMQ. default: %default')
    parser.add_option('--host', default='localhost', help='STOMP server. default: %default')
    parser.add_option('--port', default=61613, type='int', help='STOMP server port. default: %default')
    options, args = parser.parse_args()

    if args:
        parser.error('Unexpected arguments given')
    
    initialise_logging(log_level=logging.DEBUG if options.verbose else logging.INFO) 
    logging.info('Connect to stomp server %s:%s type %s' % (options.host, options.port, options.server_type))
    client = StompClient(host = options.host,
                         port = options.port,
                         login = options.login,
                         passcode = options.passcode,
                         clientId = 'stomp.examples.test_subscriber',
                         serverType = options.server_type
                         )

    sub1 = Subscriber()
    client.broadcastSubscribe(EXAMPLE_TOPIC, sub1.onMessage)

    sub2 = Subscriber()
    client.publishSubscribe(EXAMPLE_QUEUE, sub2.onPublishedMessage)

    reactor.run()

if __name__ == '__main__': 
    main()
    
