"""
Requires you to have a connection to a supervisord instance running xmlrpc on the specified port
with supervisor-twiddler installed.
"""

import xmlrpclib
from appserver.common.model import *
import logging
import os
import pprint
import operator
import socket
from appserver.common import model
from appserver.scripts import error_checker

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker

from broadwick.utils import network_utils as nu

class AppserverProxy(object):
    
    def __init__(self, db_uri): 
        """
        Database session
        """
        self.db_uri = db_uri
        engine = create_engine(self.db_uri, pool_recycle=3600)
        self.SessionCls = sessionmaker(engine, autoflush=True, autocommit=True)
        # key: server name, value: xmlrpclib.ServerProxy
        session = self.SessionCls()
        servers = session.query(Server).all()
        self.cache = {}
        for server in servers:
            proxy = xmlrpclib.ServerProxy("http://%s:%s" % (server.host, server.port))
            self.cache[server.name] = proxy
            
    def getProxy(self, serverName):
        session = self.SessionCls()
        dbserver = session.query(Server).filter_by(name=serverName).one()
        proxy = self.cache.setdefault(serverName, xmlrpclib.ServerProxy("http://%s:%s" % (dbserver.host, dbserver.port)))
        return proxy
    
        
    def getServerInfo(self, serverName):
        session = self.SessionCls()
        dbserver = session.query(Server).filter_by(name=serverName).one()
        apps = dbserver.applications

        proxy = self.getProxy(serverName)
            
        # test if I can reach the server
        try:
            proxy.system.listMethods()
        except socket.error:
            raise 
        
        
        logging.info ("Got proxy: %s" % proxy)
        info = proxy.supervisor.getAllProcessInfo()
        groups = proxy.twiddler.getGroupNames()
        
        hasgroup = serverName in groups
        if hasgroup is False:
            logging.info ("This server %s doesn't exist yet, please set it up" % serverName)
            return {}
                
        # all of the application names in the existing config
        names = dict([(item['name'], item) for item in info])
        return names
    
    def updateServer(self, serverName, to_update=None):
        # if there isn't anything installed at all, do a setup
        # otherwise, go through one by one
        logging.info ("Setting up server")
        session = self.SessionCls()
        proxy = self.getProxy(serverName)
        
        
        info = self.getServerInfo(serverName)
        groups = proxy.twiddler.getGroupNames()
        if info == {} and serverName not in groups:
            # may have been added at previous crash
            proxy.twiddler.addGroup(serverName, 999)            
        else:
            logging.info ("This server already has group %s, not adding" % serverName)
            
        # set up error checker process. even if it's already running, restart it.
        # this is because the error checker has no way of knowing about database changes.
        # we just restart it instead of trying to figure out how to get this into it.
        # long-winded explanation: the error checker runs in Twisted. 
        # The supervisor event listeners use asyncore. I can't be bothered to try and
        # make the two talk to each other. Feel free to try. 
        self.setupErrorChecking(serverName)
        
        
        dbserver = session.query(Server).filter_by(name=serverName).one()
        
        # set the server environment using broadwick rpcinterface
        proxy.broadwick.setEnv(dbserver.environment if dbserver.environment is not None else '')
                
        if to_update is None:
            apps = dbserver.applications
            appNames = [app.name for app in apps]
        else:
            appNames = to_update
        for appName in appNames:
            # there is a reason why we get the app from the db again
            # in addApplication
            # it is because with the Ajax webpages we may have a time interval
            # between the fetching of the app from db and pushing to supervisor
            self.addApplication(serverName, appName)

    
    def setupErrorChecking(self, serverName):
        """
        This must be injected into supervisord as a separate process because
        it runs using Twisted
        """
        proxy = self.getProxy(serverName)
        session = self.SessionCls()
        dbserver = session.query(Server).filter_by(name=serverName).one()
        
        server_root = dbserver.root
        server_env = dbserver.environment.split("\n") if dbserver.environment is not None else ''
        
        # this is a system process, so its root will be wherever the module is
        appdir = os.path.join(server_root)
        name = "error_checker"
        cmd = "python -m appserver.scripts.error_checker %s %s" % (self.db_uri, serverName)
        
        try:
            proxy.supervisor.stopProcess("%s:%s" % (serverName, name))
            proxy.twiddler.removeProcessFromGroup(serverName, name)
            logging.info ("Old instance of %s removed from %s" % (name, serverName))
        except:
            logging.info ("couldn't stop %s" % name)
        
        settings = {

            'directory'   : appdir,
             #'environment' : env,
            'startretries' : '0',
            'stdout_logfile' : os.path.join(server_root, "log/%s.log" % name),
            'stdout_logfile_maxbytes' : '0',
            'stdout_logfile_backups' : '0',
            'stderr_logfile_maxbytes' : '0',
            'stderr_logfile_backups' : '0',
            'logfiles_timestamped' : 'true',
            'redirect_stderr' : 'true',
            'autostart'       : 'true',
            'autorestart'     : 'true',
            'startsecs'       : '2',
            'priority'        : '0',
            'job'             : 'false',
        }

        # take the server user if it's set,
        # otherwise don't set it. 
        # set it by appending "sudo -u [uid]" to the command line. 
        if (dbserver.uid is not None and dbserver.uid != ''):
            logging.info ("Taking server UID = %s" % dbserver.uid)
            
            settings['command'] = "sudo -u %s %s" % (dbserver.uid, cmd)
        else:
            settings['command'] = cmd
        

        logging.info ("Adding to supervisor with settings:\n%s" % pprint.pformat(settings))
        try:
            spapp = proxy.supervisor.getProcessInfo("%s:%s" % (serverName, name))
        except xmlrpclib.Fault, f:
            if "BAD_NAME" in str(f):
                logging.info ("Don't have this app %s" % name)
                
            proxy.twiddler.addProgramToGroup(serverName, name, settings)

        
            
    def addApplication(self, serverName, appName):
        proxy = self.getProxy(serverName)
        session = self.SessionCls()
        dbapp = session.query(Application).filter_by(name=appName).one()
        # check if we have it first
        spapp = None
        fqName = "%s:%s" % (serverName, dbapp.name)
        try:
            spapp = proxy.supervisor.getProcessInfo(fqName)
        except xmlrpclib.Fault, f:
            if "BAD_NAME" in str(f):
                logging.info ("Don't have this app %s" % dbapp.name)
            else:
                logging.exception ("Died with some other error")
                raise
        if spapp is not None:
            # check the database last-updated time against the supervisor app start time
            # if spapp.start_time > database last-updated, do nothing
            # if spapp.start_time < database last-updated, remove it and stop it
            appserver_state = spapp['statename']
            if appserver_state not in ('STOPPED', 'BACKOFF', 'EXITED', 'FATAL'):
                appserver_start_time = datetime.datetime.fromtimestamp(spapp['start'])
                logging.info ("This application has been running since %s, last-updated in database at %s" %
                              (appserver_start_time, dbapp.last_updated))
                        
                if appserver_start_time < dbapp.last_updated:
                    logging.info ("database is newer than application. Restart")
                    if appserver_state == 'RUNNING':
                        proxy.supervisor.stopProcess(fqName)
                    # now remove it
                    logging.info ("Removing old supervisor process %s" % fqName)
                    logging.info ("Its details were: %s" % pprint.pformat(spapp))
                    proxy.twiddler.removeProcessFromGroup(serverName, dbapp.name)
                else:
                    logging.info ("application is newer than database. Do nothing")
                    return
            else:
                logging.info ("Stopped process. update it")
                proxy.twiddler.removeProcessFromGroup(serverName, dbapp.name)
                
        # we actually want to check when it has been running for. 
        # if the configuration has changed, we will restart the process
        logging.info ("Adding application to server %s" % serverName)
        # integer values must be converted to String or supervisor will barf

        env = ["SERVER_NAME=%s" % serverName]
        if dbapp.environment is not None:
            env += dbapp.environment.split("\n")
        env = ",".join(env)
        logging.info ("Env from db: %s" % env)
        dbserver = session.query(Server).filter_by(name=serverName).one()
        
        server_root = dbserver.root
        server_env = dbserver.environment.split("\n") if dbserver.environment is not None else ''
        if server_env:
            env += "," + ",".join(server_env)
        
        if "RELEASE_ENVIRONMENT=YES" in env:
            # we need to do different things to the app root
            appdir = os.path.join(server_root, "apps", "run", dbapp.name)
        else:
            appdir = os.path.join(server_root, "apps", "src")

        pythonpath = appdir
        
        env = "%s,%s,%s" % ("PYTHONPATH=%s" % pythonpath, 
                            "PYTHON_EGG_CACHE=%s" % server_root,
                            env)
        logging.info ("Environment: %s" % env)
        
        settings = {
            #'command' : dbapp.cmd,
            'directory'   : appdir,
            'environment' : env,
            'startretries' : '0',
            'stdout_logfile' : os.path.join(server_root, "log/%s.log" % dbapp.name),
            'stdout_logfile_maxbytes' : '0',
            'stdout_logfile_backups' : '0',
            'stderr_logfile_maxbytes' : '0',
            'stderr_logfile_backups' : '0',
            'logfiles_timestamped' : 'true',
            'redirect_stderr' : str(dbapp.redirect_stderr).lower(),
            'autostart'       : str(dbapp.autostart).lower(),
            # we will ignore the autorestart flag and set it to false if this is a job
            'autorestart'     : 'false' if dbapp.job is True else str(dbapp.autorestart).lower(),
            'startsecs'       : str(dbapp.startsecs),
            'priority'        : str(dbapp.priority),            
            'job'             : str(dbapp.job).lower(),
        }
        # take the application user if it's set,
        # otherwise take the server user if it's set,
        # otherwise don't set it. 
        # set it by appending "sudo -u [uid]" to the command line. 

        # We also allow variable substitution of some things. 
        # The following are currently allowed:
        # %(APPDIR)s : replaced by the absolute path to the application.
        # needed for ActiveMQ
        subst_vars = {
            "APPDIR" : appdir, 
            "SERVERNAME" : serverName,
            "PROCNAME" : dbapp.name,
            }

        subst_cmd = dbapp.cmd % subst_vars
        logging.info ("Substituted command line string: %s" % subst_cmd)
        if (dbapp.uid is not None and dbapp.uid != ''):
            logging.info ("Taking application UID = %s" % dbapp.uid)
            #settings['user'] = dbapp.uid
            #settings['command'] = subst_cmd
            # just setting the user does not work. 
            settings['command'] = "sudo -u %s %s" % (dbapp.uid, subst_cmd)
        elif (dbserver.uid is not None and dbserver.uid != ''):
            logging.info ("Taking server UID = %s" % dbserver.uid)
            #settings['user'] = dbserver.uid
            #settings['command'] = subst_cmd
            settings['command'] = "sudo -u %s %s" % (dbserver.uid, subst_cmd)
        else:
            settings['command'] = subst_cmd
        
        if dbapp.redirect_stderr is False:
            settings['stderr_logfile'] = os.path.join(server_root, "log/%s.stderr.log" % dbapp.name)
        logging.info ("Adding to supervisor with settings:\n%s" % pprint.pformat(settings))
        proxy.twiddler.addProgramToGroup(serverName, dbapp.name, settings)
        # auto-restart will take over here, if it's set.   
        

        
        
        
        
