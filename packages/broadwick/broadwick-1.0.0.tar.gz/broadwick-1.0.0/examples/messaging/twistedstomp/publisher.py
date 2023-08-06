"""
  Author:     Peter Bunyan
  Program:    publisher

  Date:       Jan. 24, 2007

  Description:    Twisted Stomp test broadcaster that sends 
                  persistent messages, requesting a receipt.
                  
                  A transaction contains 10 messages and the 7th
                  transaction is aborted as a test.
                  
"""
import examples.messaging.twistedstomp.subscriber as subscriber
from twisted.internet import reactor
from broadwick.messaging.twistedstomp import StompClient
import time, logging

MESSAGE_COUNT = 100
COMMIT_EVERY = 10
ABORT_EVERY = 80

assert MESSAGE_COUNT % COMMIT_EVERY == 0
assert ABORT_EVERY % COMMIT_EVERY == 0

class Publisher(StompClient):
    
    def onLoggedIn(self):
        self.count = 0
        logging.info('publishing %i messages to %s' % (MESSAGE_COUNT,
                                                       subscriber.EXAMPLE_QUEUE))
        self._nextMessage(None)
    
    def _txn_done(self, result):
        """callback from txn - done, log it"""
        headers, body = result
        receiptId = headers['receipt-id']
        logging.info('Transaction receipt: %s' % receiptId)
        if self.count >= MESSAGE_COUNT:
            duration = time.time() - self.start
            logging.info('sent in %f second(s)' % duration)
            self.disconnect()
            reactor.callLater(2, reactor.stop)

    def _publish(self):
        now = time.time()
        nowstr = repr(now)
        headers = {}

        if self.count == 1:
            headers['_start'] = nowstr
            self.start = now
        if self.count == MESSAGE_COUNT:
            headers['_end'] = nowstr
            headers['_count'] = MESSAGE_COUNT
        
        body = 'Hi there %i from publisher' % self.count
        deferred = self.transaction.publish(subscriber.EXAMPLE_QUEUE,
                               body, headers)
        logging.info('sent %s' % body)
        return deferred
    
    
    def _nextMessage(self, result):
        self.count += 1
        if self.count % COMMIT_EVERY == 1:
            self.transaction = self.begin()

        deferred = self._publish()

        if self.count % ABORT_EVERY == 0:
            self.transaction.abort().addCallback(self._txn_done)
        elif self.count % COMMIT_EVERY == 0: 
            self.transaction.commit().addCallback(self._txn_done)

        if self.count != MESSAGE_COUNT:
            deferred.addCallback(self._nextMessage)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)    
       
    publisher = Publisher(host='ldndev01', port=61613,
                            login='guest', passcode='guest')
    reactor.run()
