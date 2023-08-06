"""broadwick twisted stomp tests

Note: This unit test assumes an ActiveMQ running on localhost:61613. To change this
set environment variable MESSAGE_URI before running.

"""
import os

from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred, DeferredList
from broadwick.messaging import ClientFactory
from pydispatch import dispatcher
from broadwick.messaging.events import LoggedInEvent, ConnectionLostEvent

MESSAGE_URI = os.environ.get('MESSAGE_URI', 'stomp://guest:guest@localhost:61613')

TOPIC1 = '/topic/stomp_test1'
QUEUE1 = '/queue/stomp_test1'

TEST_COMPLETED_MSG = {'body' : '', 'headers' : {'status': 'completed'}}

class TestTwistedStomp(TestCase):
    timeout = 120 # The longest test takes about 60s on my Mac Pro, so there.
    @inlineCallbacks
    def test_topic_one_pub_two_sub(self):
        pub1 = TopicPublisher()
        sub1 = TopicSubscriber(name='sub1')
        sub2 = TopicSubscriber(name='sub2')

        yield sub1.readyDeferred
        yield sub2.readyDeferred
        yield pub1.readyDeferred

        pub1.run()
        
        yield sub1.completed
        yield sub2.completed

        self.assertEqual(sub1.received, pub1.sent)
        self.assertEqual(sub2.received, pub1.sent)

        sub1.client.disconnect()
        sub2.client.disconnect()
        pub1.client.disconnect()

        yield _delay()

    @inlineCallbacks
    def test_queue_one_pub_one_sub(self):
        pub1 = QueuePublisher()
        sub1 = QueueSubscriber()

        yield sub1.readyDeferred
        yield pub1.readyDeferred

        yield _delay()
        pub1.run()
        
        yield sub1.completed

        self.assertEqual(sub1.received, pub1.sent)

        sub1.client.disconnect()
        pub1.client.disconnect()

        yield _delay()

    @inlineCallbacks
    def test_queue_one_pub_two_sub(self):
        pub1 = QueuePublisher()
        sub1 = QueueSubscriber(name='qsub1')
        sub2 = QueueSubscriber(name='qsub2')

        yield sub1.readyDeferred
        yield sub2.readyDeferred
        yield pub1.readyDeferred

        yield _delay()
        pub1.run()
        
        yield DeferredList([sub1.completed, sub2.completed], 
                           fireOnOneCallback=True
                           )
        yield _delay(1)

        self.assert_(sub1.received) # We should have some messages in each
        self.assert_(sub2.received)                           

        s1 = [(int(i), j) for i, j in sub1.received]
        s2 = [(int(i), j) for i, j in sub2.received]
        p1 = [(int(i), j) for i, j in pub1.sent]

        self.assertEqual(sorted(s1 + s2), 
                         p1
                         )

        sub1.client.disconnect()
        sub2.client.disconnect()
        pub1.client.disconnect()

        yield _delay()
        


class TopicPublisher:
    Messages = 100000
    def __init__(self, name='publisher'):
        self.name = name
        self.readyDeferred = Deferred()
        self.client = ClientFactory(MESSAGE_URI)
        self.sent = []
        dispatcher.connect(self.onLoggedIn, LoggedInEvent, self.client)

    def onLoggedIn(self):
        # print self.name, 'logged in'
        self.readyDeferred.callback(None)

    def run(self):
        for i in range(self.Messages):
            body = 'Message %s from %s' % (i, self.__class__.__name__)
            self.client.broadcast(TOPIC1, body, {'index' : i})
            self.sent.append((str(i), body))
        self.client.broadcast(TOPIC1, **TEST_COMPLETED_MSG)


class Subscriber:
    def __init__(self, name):
        self.name = name
        self.readyDeferred = Deferred()
        self.completed = Deferred()
        self.client = ClientFactory(MESSAGE_URI)
        self.received = []
        dispatcher.connect(self.onLoggedIn, LoggedInEvent, self.client)

    def onLoggedIn(self):
        # print self.name, 'logged in'
        self.readyDeferred.callback(None)

    def onMessage(self, headers, body, client):
        if headers.get('status') == 'completed':
            self.completed.callback(None)
            # print self.name, 'complete'
        else:
            # print self.name, 'on message', body
            # print headers
            self.received.append((headers['index'], body))

class TopicSubscriber(Subscriber):
    def __init__(self, name='subscriber'):
        Subscriber.__init__(self, name)
        self.client.broadcastSubscribe(TOPIC1, self.onMessage)

class QueueSubscriber(Subscriber):
    def __init__(self, name='qsubscriber'):
        Subscriber.__init__(self, name)
        self.client.publishSubscribe(QUEUE1, self.onMessage)


class QueuePublisher:
    Messages = 100000
    COMMIT_EVERY = 10
    ABORT_EVERY = 80
    
    def __init__(self, name='publisher'):
        self.name = name
        self.readyDeferred = Deferred()
        self.client = ClientFactory(MESSAGE_URI)
        self.sent = []
        dispatcher.connect(self.onLoggedIn, LoggedInEvent, self.client)

    def onLoggedIn(self):
        # print self.name, 'logged in'
        self.readyDeferred.callback(None)

    @inlineCallbacks
    def run(self):
        # print 'go'
        tx_messages = []

        for i in range(self.Messages):
            if tx_messages == []:
                self.transaction = self.client.begin()
            
            body = 'Message %s from %s' % (i, self.__class__.__name__)
            # print body
            d = self.transaction.publish(QUEUE1, body, {'index' : i})
            tx_messages.append((str(i), body))

            if (i % self.ABORT_EVERY) == 0:
                # print 'abort'
                yield self.transaction.abort()
                tx_messages = []
            elif (i % self.COMMIT_EVERY) == 0:
                # print 'commit'
                yield self.transaction.commit()
                self.sent.extend(tx_messages)
                tx_messages = []

        # shouldn't be in a transaction
        self.client.publish(QUEUE1, **TEST_COMPLETED_MSG)
        # print 'done', len(self.sent)


def _delay(seconds=1):
    # Yuck. But sometimes delaying for a wee tick is enough to have sockets properly close
    # and stop the unit test framework from reporting spurious problems.
    d = Deferred()
    reactor.callLater(seconds, d.callback, None)
    return d
                      
            
