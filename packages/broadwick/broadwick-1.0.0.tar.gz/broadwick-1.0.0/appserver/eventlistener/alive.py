#!/usr/bin/env /usr/bin/python -u
#
# ripped off from the supervisor memmon
# An event listener meant to be subscribed to 
# PROCESS_STATE_EXITED, PROCESS_STATE_FATAL, PROCESS_STATE_UNKNOWN
# events.
# Will email a specified list of users when this happens.
#
# A supervisor config snippet that tells supervisor to use this script
# as a listener is below.
#
# [eventlistener:watch]
# command=python -u watch.py [options]
# events=PROCESS_STATE_EXITED,PROCESS_STATE_FATAL,PROCESS_STATE_UNKNOWN
# 
# This process must not have any stdout or stderr.write calls in it!!!
# That's why they've all been commented out. After a stdout or stderr write
# and flush, nothing ever gets sent again and the process has to be restarted.
# This is highly annoying but I don't know a way around it. 

doc = """\
alive.py [-m email_address]

Options:

-m -- specify an email address.  The script will send mail to this
      address when any process is restarted.  If no email address is
      specified, email will not be sent.

Example:

alive.py -m j.arthur.random@foo.com

"""

import os
import sys
import time
import xmlrpclib
import socket
import pprint
import glob
import stat

from supervisor import childutils
from supervisor.datatypes import byte_size
from threading import Thread

from broadwick.utils import mail as bwmail
from broadwick.utils import log


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from appserver.common import model

from xmlrpclib import ServerProxy, Fault


import logging

def usage():
    print doc
    sys.exit(255)

def shell(cmd):
    return os.popen(cmd).read()


            

class Alive(object):
    def __init__(self, db_uri, server_name):
        self.ACTIONS = {
        "PROCESS_STATE_EXITED" : self.alert,
        "PROCESS_STATE_FATAL" : self.alert,
        "PROCESS_STATE_UNKNOWN" : self.alert,
        "PROCESS_STATE_STARTING" : self.starting,
        }      
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.pscommand = 'ps -orss= -p %s'
        self.mailed = False # for unit tests
        self.email_from = "Appserver@%s" % socket.gethostname().lower()
        self.server_name = server_name

        self.db_uri = db_uri
        self.engine = create_engine(self.db_uri)
        self.SessionCls = sessionmaker(self.engine, autoflush=True, autocommit=True)
        
        session = self.SessionCls()
        server = session.query(model.Server).filter_by(name=self.server_name).one()
        self.xmlrpc = ServerProxy("http://%s:%s" % (server.host, server.port))
        session.close()
        
        
    def starting(self, headers, payload):
        """
        Tell the error checker to refresh itself
        """
        items = payload.split(" ")

        vals = [(item[0], item[1]) for item in [x.split(":") for x in items]]
        itemdict = dict(vals)
        #self.stdout.write ("event %s payload %s\n" % (headers['eventname'], pprint.pformat(itemdict)))
        #self.stdout.flush()
        processname = itemdict['processname']
        if processname in ('alive', 'error_checker'):
            #childutils.listener.ok(self.stdout)
            return # don't care about myself
        try:
            # remember to send the app name with \n so that the line receiver
            # will pick it up
            self.xmlrpc.supervisor.sendProcessStdin("%s:error_checker" % self.server_name, "%s\n" % processname)

        except Fault, f:
            if "BAD_NAME" in str(f):
                pass
            else:
                raise
        #childutils.listener.ok(self.stdout)


        
    def alert(self, headers, payload):
        session = self.SessionCls()
        items = payload.split(" ")
        vals = [(item[0], item[1]) for item in [x.split(":") for x in items]]
        itemdict = dict(vals)
        #self.stderr.write("event %s payload %s\n" % (headers['eventname'], pprint.pformat(itemdict)))
        #self.stderr.flush()
        processname = itemdict['processname']
        if processname == 'alive':
            return # don't care about myself
        # who should be told about this? It'll be in the database
        try:
            dbapp = session.query(model.Application).filter_by(name=processname).one()
            if dbapp.job is True:
                # it's a job, and it's done. Don't complain.
                #childutils.listener.ok(self.stdout)
                return
            # now get the current server
            dbserver = session.query(model.Server).filter_by(name=self.server_name).one()
            # the people who should be told about this are the server admin(s) and
            # app admins
            mail_list = []
            for admin in dbserver.server_admins:
                mail_list.append(admin.email)
            for admin in dbapp.app_admins:
                mail_list.append(admin.email)
            #logging.info ("Sending to %s" % mail_list)
            #self.stdout.write("Sending to: %s\n" % mail_list)
            mailhost = dbserver.mail_server
            #self.stdout.write("Using server %s" % mailhost)
            #self.stdout.flush()
            bwmail.sendmail(to=mail_list, subject="Process %s down" % itemdict['processname'], 
                            message="%s\n%s"% (pprint.pformat(itemdict), headers['eventname']),
                            email_from=self.email_from,
                            mail_server=mailhost)
        except Exception, e:
            # if no rows, just ignore
            #self.stderr.write("Died with %s on processname %s" % (str(e), processname))

            #self.stderr.flush()
            pass
        #self.stdout.flush()    

        session.close()
        
    def run(self):
        # it would be nice if this used Twisted. However, I can't be bothered (PC)
        while 1:
            #self.stderr.write("Running\n")
            #self.stderr.flush()
            # we explicitly use self.stdin, self.stdout, and self.stderr
            # instead of sys.* so we can unit test this code
            #self.stderr.write("childutils: %s" % childutils)
            headers, payload = childutils.listener.wait(self.stdin, 
                                                        self.stdout)
            #self.stderr.write ("event %s payload %s\n" % (headers['eventname'], payload))
            #self.stderr.flush()
            eventname = headers['eventname']
            if not eventname in self.ACTIONS:
                # do nothing with events we don't care about
                childutils.listener.ok(self.stdout)
                continue
            # if we're here, get information from db server
            try:
                self.ACTIONS[eventname](headers, payload)
            except:
                self.stderr.write("Died handling event %s" % eventname)
                self.stderr.flush()
            childutils.listener.ok(self.stdout)
        
            

def main():
    #log.initialise_logging()
    from optparse import OptionParser
    parser = OptionParser(usage='%prog: [options]')
    parser.add_option('--server_name', help='case-sensitive server name as defined in database')
    parser.add_option('--db_uri', help='DB URI of where to get information from eg. mysql://user:passwd@hostname/appserver')

    options, args = parser.parse_args()

    a = Alive(db_uri=options.db_uri, server_name = options.server_name)
    a.run()
    

if __name__ == '__main__':
    main()
    
    
    
