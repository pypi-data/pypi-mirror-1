"""Helpers for spawning processes"""
import os
import sys
import StringIO
import logging
from twisted.internet import reactor, protocol, defer, error, task

class FatProcessProtocol(protocol.ProcessProtocol):
    """
    A process protocol that allows capturing of stdout/stderr, sending stdin,
    and notification of completion.
    
    I tried writing this as separate classes or mixins but it just doesn't work
    as process.Protocol is an old-style (classic) class
    """
    def __init__(self, log_level = logging.INFO, log_freq = 5, stdin = None, **kwargs):
        self.log_level = log_level        
        self.stdin = stdin
        self.out_file = StringIO.StringIO()
        self.err_file = StringIO.StringIO()
        self.complete_deferred = defer.Deferred()

        if self.log_level is not None:
            self.flusher = task.LoopingCall(self.flushOutput)
            self.flusher.start(log_freq, now = False)
        else:
            self.flusher = None

    def connectionMade(self):
        protocol.ProcessProtocol.connectionMade(self)
        if self.stdin is not None:
            self.transport.write(self.stdin)
            # reactor.callLater(1, self.transport.closeStdin)
            self.transport.closeStdin()

    def flushOutput(self, force=False):
        self._flush(self.out_file, 'stdout', force)
        self._flush(self.err_file, 'stderr', force)
        
    def outReceived(self, d):
        self._write(self.out_file, d)

    def errReceived(self, d):
        self._write(self.err_file, d)
        
    def processEnded(self, reason):
        self.flushOutput(force=True)
        self.flusher.stop()
        if isinstance(reason.value, error.ProcessDone):
            self.complete_deferred.callback(reason.value)
        else:
            self.complete_deferred.errback(reason)        
        protocol.ProcessProtocol.processEnded(self, reason)
        
    def _write(self, f, d):
        """Append to the end of the file f without affecting the current position"""
        pos = f.pos
        f.seek(0, os.SEEK_END)
        f.write(d)
        f.seek(pos)

    def _flush(self, buf, msg, force = False):
        """Print out all un-printed data to the last \n (unless force is passed, in which case
           we print it all out
           """
        r = buf.read()
        if r:
            if not force:
                try:
                    to_print = r.rindex('\n')
                except ValueError:
                    buf.seek(-len(r), os.SEEK_CUR)
                    return

                buf.seek(to_print-len(r), os.SEEK_CUR)
                r = r[:to_print]

            logging.log(self.log_level, '%s from process:\n%s' % (msg, r))

class Process(object):
    def __init__(self, cmd, protocol, **kwargs):
        """ kwargs can include:
                path
                env
        allows the protocol class to be changed
        """
        if 'env' not in kwargs:
            kwargs['env'] = os.environ
            
        self.exe = reactor.spawnProcess(
                protocol, 
                cmd[0], 
                cmd,
                **kwargs
                )

    def kill(self):
        logging.info('killing %s' % self.exe)
        self.exe.signalProcess("KILL")
    
