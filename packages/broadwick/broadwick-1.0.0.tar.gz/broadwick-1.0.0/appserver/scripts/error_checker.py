"""
Go to database
Get all processes on this server
Start watching the logs- 
Every N seconds (default: 10), see if new errors have appeared
If any have, email the process owners

This process needs to know what server it should be monitoring
so we have to pass it in

Can't make this part of the app server proper, as can't get twisted to play nicely
with asyncore which is used by supervisord. Hence, this will be installed in /usr/bin
by setup.py and the supervisord will automatically add it in to the running applications

Be aware of the following:

1. This process will match on strings of the type "2008-10-13 12:34:56,789 ERROR" or FATAL and will
   save the stack trace until the next line, or until end of file
2. This process will only detect error messages that happen when it is running

This process has no knowledge of when the database is updated. The appserver dashboard 
will restart it when any changes happen. We don't expect this to be often (several times a day at most)
so we will just restart it instead of figuring out a nice way of getting input into it. 

If a process goes down, we don't need to do anything to this - it will just keep monitoring a 
logfile that never changes. Unless this turns out to be a problem with CPU load, not changing this. 

"""
import broadwick.utils.mail as bwmail
import broadwick.utils.log as log
import broadwick.utils.tailfile as tailfile

from broadwick.web import expose_xmlrpc
from broadwick.utils import quickstart
from broadwick.web.xmlrpc import DocXMLRPC


from xmlrpclib import ServerProxy, Fault
import socket, os, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser
from appserver.common import model

import logging
import pprint
import stat
import re
import os

from twisted.internet import reactor, task, stdio, protocol
from twisted.protocols import basic

POLL_SECS = 1


DF_RE = "^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d"

START_RE = re.compile(r"%s (?=ERROR|FATAL|CRITICAL)" % DF_RE)
#TB_RE = re.compile(r"Traceback \(most recent call last\)")
DEF_RE = re.compile(r"Unhandled error in Deferred")

END_RE = re.compile(r'%s ' % DF_RE)

# other useful things we could match on:
# Traceback (most recent call last)
# Unhandled error in Deferred

class ErrorCheck(basic.LineReceiver):
    delimiter = "\n" # for stdio
    
    def __init__(self,  server_name, db_uri=None, session_cls=None,):
        if session_cls is None and db_uri is None:
            raise Exception ("You must specify either a session class or a db URI")
        
        if session_cls is not None:
            self.SessionCls = session_cls
        else:
            self.db_uri = db_uri
            self.engine = create_engine(self.db_uri)
            self.SessionCls = sessionmaker(self.engine, autoflush=True, autocommit=True)
        
        self.server_name = server_name        
        self.tailers = {}
        self.refresh()
        reactor.addSystemEventTrigger("before", "shutdown", self.stopAll)
        
        
    def lineReceived(self, line):
        """
        Whatever I get here is going to be the application name.
        I will refresh that application's error tailer. 
        if I don't have an application by that name, I will ignore it
        """
        appname = line.strip()
        tailer = self.tailers.get(appname)
        if tailer is None:
            logging.info ("I got rubbish: %s, ignoring" % line)
            return
        tailer.stop()
        self.clearLineBuffer()
        tailer.start()
        logging.info ("I have refreshed tailer for application %s" % appname)
        
        
        

    def stopAll(self):
        for appname, tailer in self.tailers.iteritems():
            tailer.stop()
        

    def refresh(self, appName=None):
        session = self.SessionCls()
        self.server = None
        self.xmlrpc = None
        try:
            self.server = session.query(model.Server).filter_by(name=self.server_name).one()
            self.xmlrpc = ServerProxy("http://%s:%s" % (self.server.host, self.server.port))
        except:
            msg = "No server with name %s" % self.server_name
            logging.exception (msg)
            raise Exception(msg)
        self.logdir =  os.path.join(self.server.root, "log")        
        self.apps = self.server.applications
        for app in self.apps:
            # get the original tailer if it's there, and stop it
            if appName is not None and app.name != appName:
                continue
            existing = self.tailers.get(app.name)
            if existing is not None:
                existing.stop()
            
            filename = os.path.join(self.logdir, "%s.log" % app.name)
            logging.info ("Starting watcher for file %s" % filename)
            mail_list = []
            for admin in self.server.server_admins:
                mail_list.append(admin.email)
            for admin in app.app_admins:
                mail_list.append(admin.email)
            if app.name in self.tailers:
                del self.tailers[app.name]
            self.tailers[app.name] = ErrorTailer(filename=filename,
                                                 delay=POLL_SECS,
                                                 mail_list=mail_list,
                                                 mail_server=self.server.mail_server)
            # might not have the file yet. If we get IOError, ignore it 
            try:
                self.checkAndStart(app.name)
                
            except (IOError, Fault):
                logging.info ("Couldn't open file %s or couldn't find process, retry in 10s" % filename)
                reactor.callLater(10, self.checkAndStart, app.name)

    def checkAndStart(self, appname):
        # see if this app is running based on the xmlrpc status
        processinfo = self.xmlrpc.supervisor.getProcessInfo("%s:%s" % (self.server_name, appname))
        state = processinfo['statename']
        logging.info ("Process info for %s: \n%s" % (appname, pprint.pformat(state)))
        if state in ('RUNNING', 'STARTING'): 
            self.tailers[appname].start()
        elif state in ('STOPPING', 'STOPPED'):
            logging.info ("Process %s is dead, don't bother error checking its logfile" % appname)
        

        
class ErrorTailer(tailfile.FollowTail):
    
    # maximum number of mails to send in INTERVAL
    MAX_NUM = 5
    # Throttling interval
    INTERVAL = 300

    def __init__(self, filename, delay, mail_list, mail_server):
        self.mail_list = mail_list
        self.mail_server = mail_server
        self.email_from = "Appserver@%s" % socket.gethostname().lower()
        
        tailfile.FollowTail.__init__(self, filename=filename, delay=delay)
        # allowed states: IDLE, FOUND_ERROR
        # state changes: if we find an error line, go into FOUND_ERROR and start keeping lines
        # when we find something that matches a non-error logging line, go into IDLE
        # and email the buffer. 
        self.state = "IDLE" 
        self.stack_trace = []
        self.resetCounters()
        

    def resetCounters(self):
        self.counter_start_time = datetime.datetime.utcnow() # so we only send N mails every Xmins
        self.last_sent_time = self.counter_start_time
        self.last_sent_counter = 0

    def stop(self):
        if self.stack_trace != []:
            self._reset()
        tailfile.FollowTail.stop(self)


    
    def start(self):
        self.resetCounters()
        tailfile.FollowTail.start(self)
       

    def _reset(self):
        self.state = "IDLE"
        
        # if it's been more than N minutes since last sent,
        # don't care about counter.
        since = (datetime.datetime.utcnow() - self.counter_start_time).seconds
        logging.debug ("Timer started %s seconds ago" % since)
        if since > self.INTERVAL:
            self.last_sent_counter == 0
            self.counter_start_time = datetime.datetime.utcnow()
            
            
        
        if self.last_sent_counter == self.MAX_NUM and since <= self.INTERVAL:
            logging.info("%s mails sent in %s seconds for %s. Not sending." %
                          (self.MAX_NUM, self.INTERVAL, self.filename))
            
        else:
            logging.debug ("Counter start timer %s counter %s" % (self.counter_start_time, self.last_sent_counter))
            if self.last_sent_counter == self.MAX_NUM:
                self.last_sent_counter = 0
                self.counter_start_time = datetime.datetime.utcnow()
            self.last_sent_counter += 1
            
            # at this point, if counter <= MAX_NUM and the timer has lapsed,
            # set counter back to 0.
            
            if (self.last_sent_counter <= self.MAX_NUM and 
                (since >= self.INTERVAL)):
                logging.info ("Resetting counter, it has been %s since last counter reset and we have only sent %s" % (since, self.last_sent_counter))
                self.counter_start_time = datetime.datetime.utcnow() 
                self.last_sent_counter = 0
            elif self.last_sent_counter == self.MAX_NUM:
                self.stack_trace.append ("\n\n ***** %s messages sent in %ss, no more will be sent for %ss *****" %
                                         (self.MAX_NUM, self.INTERVAL, self.INTERVAL))
            bwmail.sendmail(to=self.mail_list,
                            subject="error in %s" % self.filename,
                            message="\n".join(self.stack_trace),
                            mail_server=self.mail_server,
                            email_from=self.email_from)
            self.last_sent_time = datetime.datetime.utcnow()
            
                
        self.stack_trace = []
            

    def lineReceived( self, line ):
        #logging.info ("Got line: %s" % line)
        if self.state == "IDLE":
            if START_RE.match(line) or DEF_RE.match(line): #or TB_RE.match(line):
                self.state = "FOUND_ERROR"
                self.stack_trace.append(line)
        elif self.state == "FOUND_ERROR":
            if END_RE.match(line):
                self._reset()
            else:
                self.stack_trace.append(line)

    def fileReset(self, fileobj):
        if self.stack_trace != []:
            self._reset()
        self.resetCounters()
        return tailfile.FollowTail.fileReset(self, fileobj)
        


def main(db_uri, server_name):
    log.initialise_logging()
    ec = ErrorCheck(db_uri=db_uri, server_name=server_name)
    xmlrpc = DocXMLRPC(ec, allow_none=True,
                       server_title="error checker for app server %s" % server_name,
                       server_name = "error checker %s" % server_name,
                       server_documentation = "You shouldn't need to use this in real life")
    stdio.StandardIO(ec)
    #quickstart(xmlrpc, port=xmlrpcport)
    reactor.run()

if __name__ == '__main__':

    parser = OptionParser(usage='%prog: [options] database_uri server name')
    
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.error('Incorrect number of arguments passed. I need a database uri'
                     ' followed by the server name')
        
    db_uri, server_name = args[:2]
        
    main(db_uri, server_name)
    
