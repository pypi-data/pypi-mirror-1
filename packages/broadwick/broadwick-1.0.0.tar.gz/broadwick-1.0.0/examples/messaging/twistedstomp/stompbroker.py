import logging
import re

from twisted.internet import reactor
from twisted.internet import protocol

from broadwick.utils.log import initialise_logging
from broadwick.messaging.twistedstomp import AnotherLineReceiver, uuidgen


class StompServerProtocol(AnotherLineReceiver):
    _emptyBody = ''
    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = '%s:%s' % (addr.host, addr.port)
        self._resetMessage()
        self.login = '???'
        self.subscriptions = {}
        self.recurseLevel = 0
        self.recursionLimit = 10
        self.instanceid = uuidgen()
        self.mcount = 1
        logging.info('Connection from %s' % self.addr)
        

    def _resetMessage(self):
        self.command = None
        self.headers = {}
        self.body = ''
        self.contentLength = None

    def endMessage(self):
        """A full message has been received. Act on it"""
        # logging.debug(
                # 'Got:\nCommand: %r\nHeaders:%r\nBody:%r' % 
                # (self.command, self.headers, self.body)
                # )
        if self.command is not None:
            # Make somebody isn't trying to attack us
            if '.' in self.command:
                self._senderror('Bad command %r' % self.command)
                self.transport.loseConnection()
                return

            handler = getattr(self, '_on%s' % self.command, None)
            if handler is None:
                self._senderror('Command %r not implemented' % self.command)
            else:
                handler()
            
        self._resetMessage()

    def lineReceived(self, data):
        # logging.debug('Line received: %r' % data)
        if self.command is None:
            if data != '':
                self.command = data
            return True

        if data == '':
            # End of headers, following data is body. Go to raw mode to handle
            return False
        
        if '\0' in data:
            self._senderror('Null character in header line: %r' % data)
            raise LoseConnection()

        pos = data.find(':')
        if pos != -1:
            header, data = data[:pos], data[pos+1:]
            data = data.replace('\\n', '\n')
        else:
            self._senderror('Bad header line: %r' % data)
            raise LoseConnection()

        if header == 'content-length':
            try:
                self.contentLength = int(data)
            except ValueError:
                self._senderror('Bad header line: %r' % data)
                raise LoseConnection()

        self.headers[header] = data
        return True
    
    def rawDataReceived(self, data, ptr):
        # logging.debug('raw data received: %r, %d' % (data[ptr:], ptr))
        assert not self.body

        eom = -1

        if self.contentLength is not None:
            # Should have {content length worth of data][null byte][next message]
            available = len(data)-ptr

            if available > self.contentLength:
                # In case of badly formatted message look for the next frame
                # terminator
                eom = ptr + self.contentLength
                eom = data.find('\0', eom)
        else:
            eom = data.find('\x00', ptr)

        if eom != -1:
            consumed = eom-ptr
            self.body = data[ptr:eom]
            self.endMessage()

            return eom+1, True
        else:
            return ptr, False

    def connectionLost(self, reason):
        logging.info('Connection lost from %s(%s): %s' % (self.login, self.addr, reason.getErrorMessage()))
        self.factory.clientConnectionLost(self)

    def _send(self, command, headers, body):
        out = ["%s\n" % (command)]
        for k,v in headers.iteritems():
            out.append("%s:%s\n" % (k,str(v).replace('\n','\\n')))
        out.append('\n')
        out.append(body)
        out.append('\0')
        # logging.debug('Sending to %s (%s): %r' % (self.login, self.addr, ''.join(out)))
        self.transport.writeSequence(out)

    def _senderror(self, error):
        """send an error message to the client"""
        logging.info('Sending error to %s (%s) : %s. Incoming message:\nCommand:%r\nHeaders:%r ' % 
                (self.login, self.addr, error, self.command, self.headers)
                )
        self._send('ERROR', {}, 'StompServer: %s\x00\n' % error)

                
    def _onCONNECT(self):
        login = self.headers.get('login', None)
        if login is None:
            self._senderror('Required field login not specified on CONNECT message')
            self.transport.loseConnection()
            return

        self.login = login
        logging.info('Connect from %s at %s' % (self.login, self.addr))
        self._send(
            'CONNECTED',
            {'session' : uuidgen()},
            self._emptyBody
            )

    def _onSUBSCRIBE(self):
        dest = self.headers.get('destination', None)
        if dest is None:
            self._senderror('destination missing from SUBSCRIBE message')
            return

        if not dest.startswith('/topic/'):
            self._senderror('sorry, I\'m too dumb to deal with destination %r' % dest)
            return

        # if self.headers.get('ack', 'auto') != 'auto':
            # self._senderror('sorry, I\'m too dumb to cope with client acked messages (subscription to %s)' % dest)
            # return

        self.subscriptions[dest] = destRegexp(dest)
        logging.info('%s (%s) has subscribed to %s' % (self.login, self.addr, dest))

    def _onUNSUBSCRIBE(self):
        dest = self.headers.get('destination', None)
        if dest is None:
            self._senderror('destination missing from UNSUBSCRIBE message')
            return

        try:
            del self.subscriptions[dest]
        except KeyError:
            pass
        logging.info('%s (%s) has unsubscribed from %s' % (self.login, self.addr, dest))

    def _onDISCONNECT(self):
        """Screw you guys, I'm going home"""
        self.transport.loseConnection()

    def _onACK(self):
        """Do nothing, we're not an acking sort of server"""
        pass

    def _onSEND(self):
        dest = self.headers.get('destination', None)
        if dest is None:
            self._senderror('destination missing from SEND message')
            return
        if not dest.startswith('/topic/'):
            self._senderror('sorry, I\'m too dumb to deal with destination %r' % dest)
            return
        if self.headers.get('persistent', None) == 'true':
            self._senderror('sorry, I\'m too dumb to deal with persistent messages')
            return
        if 'receipt' in self.headers:
            self._senderror('sorry, I\'m too dumb to send you receipts for messages')
            return
        self.mcount += 1
        self.headers['message-id'] = '%s.%s' % (self.instanceid, self.mcount)
        self.factory.sendMessage(dest, self.headers, self.body)

class StompServerFactory(protocol.ServerFactory):
    protocol = StompServerProtocol

    def __init__(self):
        # protocol.ServerFactory.__init__(self)
        self.clients = {}

    def buildProtocol(self, addr):
        p = StompServerProtocol(self, addr)
        self.clients[id(p)] = p
        return p

    def clientConnectionLost(self, client):
        try:
            del self.clients[id(client)]
        except KeyError:
            pass

    def sendMessage(self, dest, headers, body):
        # logging.debug('distribute message to %s, %s' % (dest, headers))
        for client in self.clients.itervalues():
            for sub in client.subscriptions.itervalues():
                if re.match(sub, dest):
                    client._send('MESSAGE', headers, body)

def destRegexp(dest):
    dest = dest.replace('.', '[.]')
    dest = dest.replace('*', '[^.]*')
    if dest[-1] == '>':
        dest = dest[:-1]
    else:
        dest += '$'
    return re.compile(dest)



def main(port = 61613):
    initialise_logging(logging.INFO)
    logging.info('Listening on port %s' % port)
    reactor.listenTCP(port, StompServerFactory())
    reactor.run()

if __name__ == '__main__':
    main()
