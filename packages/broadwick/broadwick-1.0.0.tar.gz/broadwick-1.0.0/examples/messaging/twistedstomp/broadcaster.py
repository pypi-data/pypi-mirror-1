"""
  Author:     Peter Bunyan, Jonathan Marshall
  Program:    broadcaster

  Date:       Jan. 24, 2007

  Description:    Twisted Stomp test broadcaster that sends 
                  non-persistent messages, requesting no receipt
                  
"""
import examples.messaging.twistedstomp.subscriber as subscriber
from twisted.internet import reactor
from broadwick.messaging.twistedstomp import StompClient
import time, logging

MESSAGE_COUNT = 10000

class Broadcaster(StompClient):
    def onLoggedIn(self):
        StompClient.onLoggedIn(self)

        self.count = 0
        logging.info('broadcasting %i messages to %s' % (MESSAGE_COUNT,
                                                         subscriber.EXAMPLE_TOPIC))
        self._nextMessage()
    
    def _nextMessage(self):
        for i in range(10): # Send a batch of messages before yielding the CPU
            self.count = self.count + 1
            now = time.time()
            nowstr = repr(now)
            headers = {}

            if self.count == 1:
                headers['_start'] = nowstr
                self.start = now
            if self.count == MESSAGE_COUNT:
                headers['_end'] = nowstr
                headers['_count'] = MESSAGE_COUNT
                duration = now - self.start
                logging.info('sent %d in %f second(s)' % (self.count, duration))
            elif self.count > MESSAGE_COUNT:
                self.disconnect()
                reactor.callLater(2, reactor.stop)
                return
            headers['_sent'] = nowstr

            body = 'Hi there %i from broadcaster' % self.count
            self.broadcast(subscriber.EXAMPLE_TOPIC, 
                             body, headers)
            # logging.info('sent %r' % body)
            # time driven send
        reactor.callLater(0, self._nextMessage)



        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)    
       
    client = Broadcaster(host='localhost', port=61613,
                         login='test_broadcaster') 
    reactor.run()
