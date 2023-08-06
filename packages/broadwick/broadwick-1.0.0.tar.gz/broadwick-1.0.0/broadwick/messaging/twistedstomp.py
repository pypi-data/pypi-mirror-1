"""
  Author:     Peter Bunyan, Jonathan Marshall
  Program:    twisted stomp

  Date:       June 2008

  Description:    Twisted Stomp implementation.
"""
import logging
import socket
import os
import re

from pydispatch import dispatcher
from twisted.internet import reactor, defer, protocol

# The uuid module is included in the standard python distrib
# from python 2.5
import uuid

RMQ_STOMP_HEADERS = 'exchange', 

_hostname = socket.gethostname()
_pid = os.getpid()

from broadwick.messaging.events import LoggedInEvent, ConnectionLostEvent

class LoseConnection(Exception): pass
class ErrorFromServer(Exception):
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body

class AnotherLineReceiver(protocol.Protocol):
    """Similar in concept to twisted's LineReciever.

    Twisted's LineReceiver was not designed for a streaming connection
    where you are constantly switching back and forth between line (header)
    data and binary payload data. 

    a) Twisted's Line Receiver is recursive and you will blow the recursion
    limits if you receive a large number of packets of data at one.

    b) Twisted's Line Receiver does a lot of copying and slicing of the 
    buffer, so it is inefficient

    This code uses a slightly different API in order to avoid these problems

      """
    line_mode = True
    data = ''

    def dataReceived(self, data):
        # #logging.debug('data received: %r' % data)
        data = self.data + data # self.data is data that was not previously processed
        ptr = 0 # invariant: all data before ptr has been processed

        try:
            while True:
                # Process all line data
                while self.line_mode:
                    headerend = data.find('\n', ptr)
                    if headerend != -1:
                        line = data[ptr:headerend]
                        self.line_mode = self.lineReceived(line)
                        ptr = headerend + 1
                    else:
                        # Not enough data for a header line. Wait for more data
                        self.data = data[ptr:]
                        return

                # Process the binary data
                while not self.line_mode:
                    newptr, self.line_mode = self.rawDataReceived(data, ptr)
                    if newptr != ptr:
                        ptr = newptr
                    elif not self.line_mode:
                        # No data consumed and not switched back to line mode => more body required
                        self.data = data[newptr:]
                        return
        except LoseConnection, ex:
            self.transport.loseConnection()

    def lineReceived(self, line):
        """Return True to continue processing lines, False to switch to raw data mode"""
        raise NotImplementedError()

    def rawDataReceived(self, data, ptr):
        """Return new ptr, line_mode

        If you consume X bytes of data, the first value should be ptr + X
        If you wish to switch to line mode, the second value should be True

        If you return ptr, False you have not consumed data and you wish to
        stay in raw mode which implies that you need more raw data 
        """
        raise NotImplementedError()

class StompProtocol(AnotherLineReceiver):
    """Base StompProtocol suitable for decoding Stomp frames"""
    def __init__(self, *args, **kwargs):
        # LineReceiver.__init__(self, *args, **kwargs)
        self.headers = {}
        self._resetMessage()

    def _resetMessage(self):
        self.command = None
        self.headers.clear()
        self.body = ''
        self.contentLength = None

    def endMessage(self):
        """A full message has been received. Act on it"""
        logging.debug( 'Got:\nCommand: %r\nHeaders:%r\nBody:%r' % (self.command, self.headers, self.body))
        if self.command is not None:
            # Make somebody isn't trying to attack us
            if '.' in self.command:
                self._error('Bad command %r' % self.command)
                self.transport.loseConnection()
                return

            handler = getattr(self.factory, 'on%s' % self.command, None)
            if handler is None:
                handler = getattr(self, 'on%s' % self.command, None)
            if handler is None:
                self._error('Command %r not implemented' % self.command)
            else:
                handler(self.headers.copy(), self.body)
            
        self._resetMessage()

    def lineReceived(self, data):
        """A header line has been received"""
        #logging.debug('Line received: %r' % data)
        if self.command is None:
            if data != '':
                self.command = data
            return True

        if data == '':
            # End of headers, following data is body. Go to raw mode to handle
            return False
        
        if '\x00' in data:
            self._error('Null character in header line: %r' % data)
            raise LoseConnection()

        pos = data.find(':')
        if pos != -1:
            header, data = data[:pos], data[pos+1:]
            data = data.replace('\\n', '\n')
        else:
            self._error('Bad header line: %r' % data)
            raise LoseConnection()

        if header == 'content-length':
            try:
                self.contentLength = int(data)
            except ValueError:
                self._error('Bad header line: %r' % data)
                raise LoseConnection()

        self.headers[header] = data
        return True
    
    def rawDataReceived(self, data, ptr):
        """Raw (payload) data has been received"""
        #logging.debug('raw data received: %r, %d' % (data[ptr:], ptr))
        assert not self.body

        eom = -1

        if self.contentLength is not None:
            # Should have [payload data of length contentLength][null byte][next message]
            available = len(data)-ptr

            if available > self.contentLength:
                # In case of badly formatted message look for the next frame
                # terminator
                eom = ptr + self.contentLength
                eom = data.find('\x00', eom)
        else:
            eom = data.find('\x00', ptr)

        if eom != -1:
            consumed = eom-ptr
            self.body = data[ptr:eom]
            self.endMessage()

            return eom+1, True
        else:
            return ptr, False

    def _send(self, command, headers, body=''):
        if body is None: 
            body = ''
        out = ["%s\n" % (command)]
        for k,v in headers.iteritems():
            if k != 'content-length':
                if isinstance(v, unicode):
                    v = v.encode('utf8')
                try:
                    out.append("%s:%s\n" % (k,str(v).replace('\n','\\n')))
                except:
                    logging.error('Bum on %r : %r' % (k, v))
                    raise
        out.append('content-length:%s\n' % len(body))
        out.append('\n')
        out.append(body)
        out.append('\x00')
        logging.debug('Sending:\n%r' % ''.join(out))
        self.transport.writeSequence(out)

    def _error(self, msg):
        logging.debug(msg)


class StompClientProtocol(StompProtocol):
    """Protocol suitable for use by StompProtocol"""

    def __init__(self, *args, **kwargs):
        StompProtocol.__init__(self, *args, **kwargs)
        self.waitingReceipt = {}
        
    def connectionMade(self):
        self.factory.clientConnected(self)

    def login(self, login, passcode, clientId):
        headers = {'login' : login}
        if passcode:
            headers['passcode'] = passcode
        if clientId is not None:
            headers['client-id'] = clientId
        self._send('CONNECT', headers)

    def logout(self):
        self._send('DISCONNECT', {})

    def send(self, command, headers, body=None, destination=None, withReceipt=False, 
             persistent=False, transaction=None):
        if headers is None:
            headers = {}
        else:
            headers = headers.copy()

        if destination:
            headers['destination'] = destination

        if persistent:
            headers['persistent'] = 'true'

        if transaction:
            headers['transaction'] = transaction

        if withReceipt: 
            deferred = defer.Deferred()

            uuid = uuidgen()
            headers['receipt'] = uuid
            self.waitingReceipt[uuid] = deferred
        else:
            deferred = None

        self._send(command, headers, body)

        return deferred

    def connectionLost(self, reason):
        for d in self.waitingReceipt.values():
            if not d.called:
                d.errback(reason)
        self.waitingReceipt.clear()

    def onCONNECTED(self, headers, body):
        self.factory.onLoggedIn()

    def onMESSAGE(self, headers, body):
        self.factory.onMessage(headers, body)

    def onRECEIPT(self, headers, body):
        d = self._getReceiptDeferred(headers)
        if d:
            d.callback((headers, body))

    def onERROR(self, headers, body):
        message = headers.get('message', '')

        # Extension to the Stomp protocol - we allow error messages to specify 
        # a receipt id, so that you can know that you will never receive an ACK for
        # message that you have requested an ACK for
        d = self._getReceiptDeferred(headers)
        if d:
            d.errback(ErrorFromServer(headers, body))
        else:
            logging.warning('Error message from server: %s\n%s' % (message, body))

    def _getReceiptDeferred(self, headers):
        uuid = headers.get('receipt-id', None)
        if uuid:
            try:
                return self.waitingReceipt.pop(uuid)
            except KeyError:
                logging.warning('Receipt received for missing message: %s' % uuid)


#############################################################################

class StompClient(protocol.ReconnectingClientFactory):
    protocol = StompClientProtocol
    maxDelay = 10
    def __init__(self, host, port, login, passcode=None, clientId = None, reconnect = True, serverType='AMQ'):
        """clientId: If None, we will create an id that can be used to track
        this process down. If you are using durable connections you must supply your own id

        reconnect: If true we will attempt to reconnect (and re-subscribe to 
        any previous subscriptions) if we lose connection to the server

        serverType: The type of the server. Can be AMQ (ActiveMQ) or RMQ (RabbitMQ)
        """
        self.host = host
        self.port = port
        self.login = login
        self.passcode = passcode
        self.clientId = clientId
        self.subscriptions = {}
        self.loggedIn = False
        self.serverType = serverType
        self._connector = None

        assert self.serverType in ('AMQ', 'RMQ')

        if not reconnect:
            self.stopTrying()
        reactor.connectTCP(host, port, self)

    def isConnected(self):
        return self._connector is not None

    def disconnect(self):
       if self._connector is not None:
            self.stopTrying()
            return self._connector.logout()

    def publish(self, destination, body, headers=None):
        """
            There will be a receipt and amq will store this msg

            Returns: a deferred object to be called on confirmation of 
            receipt by amq.
        """
        assert destination.startswith('/queue/')
        if self.serverType == 'RMQ':
            headers = fudge_rmq_headers(headers)
            headers['delivery-mode'] = '2'
        return self._connector.send('SEND', headers, body, 
                                    destination=destination,
                                    withReceipt=True, persistent=True)

    def begin(self):
        """Begin a transaction. You can be notified when the transaction
        has begun by adding to the deferred member of the returned transaction
        object"""
        return StompTransaction(self._connector)
    
    def broadcast(self, destination, body, headers=None):
        """
            Broadcast a message (on a topic)
            there will be no receipt and amq will not store this msg
        """
        assert destination.startswith('/topic/')
        if self.serverType == 'RMQ':
            headers = fudge_rmq_headers(headers)
            headers.setdefault('exchange', 'amq.topic')

        return self._connector.send('SEND', headers, body, destination=destination)

    def publishSubscribe(self, destination, callback):
        """Subscribe to published messages. We only support queues
        
            callback will receive arguments
            (message headers, message body, this StompClient)
            """
        assert destination.startswith('/queue/')

        headers = {}
        headers['ack'] = 'client'

        # AMQ-workaround. If you subscribe to a queue and your prefetch size is not 1
        # and you crash whilst processing message AMQ will not forward any more messages to you
        # from the queue until AMQ is restarted (and the jconsole will show one consumer of 
        # your queue even though your program has quit)
        if self.serverType == 'AMQ':
            headers['activemq.prefetchSize'] = '1'
        return self._subscribe(destination, headers, callback)

    def broadcastSubscribe(self, destination, callback):
        """Subscribe to broadcast messages. We only support topics

            callback will receive arguments
            (message headers, message body, this StompClient)
            """
        assert destination.startswith('/topic/')

        headers = {}
        headers['ack'] = 'auto'

        if self.serverType == 'AMQ':
            headers['activemq.dispatchAsync']='true'
        elif self.serverType == 'RMQ':
            headers['id'] = uuidgen()
            headers['destination'] = ''
            headers['exchange'] = 'amq.topic'
            headers['routing_key'] = destination
        return self._subscribe(destination, headers, callback)

    def durableSubscribe(self, destination, callback):
        """Subscribe to broadcast messages. We only support topics

            callback will receive arguments
            (message headers, message body, this StompClient)
            """
        assert destination.startswith('/topic/')
        assert self.clientId

        headers = {}
        if self.serverType == 'AMQ':
            headers['activemq.subcriptionName'] = self.clientId
            headers['activemq.prefetchSize'] = '1' # See publishSubscribe for details
        else:
            raise NotImplementedError('durable subscriptions on server type %r' % self.serverType)

        return self._subscribe(destination, headers, callback)

    def unsubscribe(self, destination):
        """Unsubscribe from a queue / topic"""
        assert destination.startswith('/queue/') or destination.startswith('/topic/')

        try:
            del self.subscriptions[destination]
        except KeyError:
            pass

        return self._connector.send('UNSUBSCRIBE', {'destination' : destination})

    def ack(self, msgId, withReceipt=False):
        """msgId: the id of the message to be acked"""
        return self._connector.send('ACK', {'message-id' : msgId}, None, withReceipt=withReceipt)

    ##### Notifications
    def clientConnectionLost(self, connector, reason):
        logging.info('Connection to %s:%s lost: %s' % (self.host, self.port, reason.value))
        self._connector.connectionLost(reason)
        self._connector = None
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        dispatcher.send(ConnectionLostEvent, self)

    def clientConnected(self, connector):
        """
            Connection worked we can login...
        """
        logging.info('Connected to %s:%s' % (self.host, self.port))
        self._connector = connector
        if self.clientId is None:
            clientId = '%s.%s.%s.%s' % (self.login, _hostname, _pid, uuidgen())
        else:
            clientId = self.clientId

        self._connector.login(self.login, self.passcode, clientId)

    def onLoggedIn(self):
        """We have logged in. We will re-subscribe to everything previously subscribed to
        """
        self.loggedIn = True
        for destination, (destRegexp, headers, callback) in self.subscriptions.iteritems():
            self._doSubscribe(headers)
        dispatcher.send(LoggedInEvent, self)

    def onMessage(self, headers, body):
        """We have received a message. Send it to the right subscription"""
        if self.serverType == 'RMQ':
            for key, value in headers.items():
                if key.startswith('X-'):
                    del headers[key]
                    headers[key[2:]] = value

        target = headers['destination']
        for destination, (destRegexp, subheaders, callback) in self.subscriptions.iteritems():
            if re.match(destRegexp, target):
                try:
                    callback(headers, body, self)
                except (SystemExit, KeyboardInterrupt):
                    raise
                except:
                    logging.exception('Unhandled error whilst processing STOMP message:')

    def onSubscribe(self, headers):
        """We have just sent a subscription request"""
        pass

    ### Helpers
    def _subscribe(self, destination, headers, callback):
        headers.setdefault('destination', destination)
        self.subscriptions[destination] = destRegexp(destination), headers, callback
        if self.loggedIn:
            self._doSubscribe(headers)

    def _doSubscribe(self, headers):
        self._connector.send('SUBSCRIBE', headers)
        self.onSubscribe(headers)

#############################################################################
class StompTransaction:
    """
    Transaction wrapper retieved from StompClient.begin()
    Do not resuse once commit or abort is called.
    Use the deferred to determine the success of the transaction begin

    status is one of 'open', 'committed', 'aborted' or 'error'

    """
    def __init__(self, connector):
        self._connector = connector
        self.txn = uuidgen()
        self.status = 'open' # Start opened so that we can immediately send messages

        self.deferred = self._connector.send('BEGIN', {}, None,
                                    withReceipt=True,
                                    transaction=self.txn)
        self.deferred.addCallback(self._done, 'open').addErrback(self._error, 'open')
        
    def __repr__(self):
        return 'StompTransaction %s %s' % (self.status, self.txn)
    
    def _done(self, result, status):
        #logging.debug('StompTransaction success, state now %s' % status)
        self.status = status
        return result

    def _error(self, result, status):
        logging.warning('StompTransaction failure moving to state %s : %r\n%s' % (status, result.getErrorMessage(), result.getTraceback()))
        self.status = 'error'
        return result

    def commit(self):
        assert self.status == 'open'
        deferred = self._connector.send('COMMIT', {}, None,
                                    withReceipt=True,
                                    transaction=self.txn)
        deferred.addCallback(self._done, 'committed').addErrback(self._error, 'committed')
        return deferred

    def abort(self):
        assert self.status == 'open'
        deferred = self._connector.send('ABORT', {}, None,
                                    withReceipt=True,
                                    transaction=self.txn)
        deferred.addCallback(self._done, 'aborted').addErrback(self._error, 'aborted')
    
        return deferred
    
    def publish(self, destination, body, headers=None):
        assert destination.startswith('/queue/')
        assert self.status == 'open'

        headers = fudge_rmq_headers(headers)
        return self._connector.send('SEND', headers, body, 
                                    destination=destination,
                                    withReceipt=True, persistent=True,
                                    transaction=self.txn)
    

def destRegexp(dest):
    """Convert a JMS destination header to a regular expression

    E.g. foo.bar.>  gets turned into foo[.]bar[.].*
    """
    dest = dest.replace('.', '[.]')
    dest = dest.replace('*', '[^.]*')
    if dest[-1] == '>':
        dest = dest[:-1]
    else:
        dest += '$'
    return re.compile(dest)

def uuidgen():
    """Return a uuid. We base64 encode it so that it takes up less storage
    space than the standard hexadecimal representation (22 bytes vs 36)"""

    return uuid.uuid1().bytes.encode('base64')[:-3]

def fudge_rmq_headers(headers):
    if headers:
        # Private headers must be prefixed with X- when sending to RabbitMQ
        return dict((('X-%s' % k, v) 
                      for k, v in headers.iteritems()
                      if k not in RMQ_STOMP_HEADERS
                      ))
    return {}


 
