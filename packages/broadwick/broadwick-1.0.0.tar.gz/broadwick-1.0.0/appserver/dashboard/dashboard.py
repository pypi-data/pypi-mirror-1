import os
import pickle
import logging
import datetime 
import twisted.web.static
import pprint
import socket

from pydispatch import dispatcher

from broadwick import messaging
from broadwick.web import expose_genshi, expose_json

from appserver.dashboard import config
import appserver.common.model

def resource_path(f):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resource')
    if f:
        path = os.path.join(path, f)
    return path

class View(object):
    assert config.static_path is not None, 'This module must be loaded *after* config.static_path is set'

    controller = None
    static = twisted.web.static.File(config.static_path)
    resource = twisted.web.static.File(resource_path(None))

    @expose_genshi(template=resource_path('index.genshi'))
    def index(self, selected = None, row_id = None):
        return {
            'dojo' : config.dojo,
            'selected' : selected,
            'row_id' : row_id,
            'content' : { 'href' : None if selected is None else \
            "form_content.html?table=%s&amp;row_id=%s" % (selected, row_id) }
        }

    @expose_json
    def menu_data(self, table):
        t = getattr(appserver.common.model, table)
        m = {'label' : 'name', 'identifier' : 'id' }
        items = []
        for row in config.Session().query(t).order_by('name').all():
            items.append({'id' : row.id, 'name' : row.name})
        m['items'] = items
        return m

    @expose_genshi(template=resource_path('menu.genshi'))
    def menu(self, table):
        logging.info ("Serving menu for table %s" % table)
        return {
            'table' : table
            }
        
    
    @expose_genshi(template=resource_path('form_content.genshi'))
    def form_content(self, table, row_id):
        session = config.Session()
        tableClass = getattr(appserver.common.model, table)
        if row_id == 'new':
            row  = None
        else:
            #row = session.query(tableClass, row_id)
            row = session.query(tableClass).filter_by(id=row_id).one()
        logging.info ("Row: %s" % row)
        return {'row' : row, 
                'tableClass': tableClass, 
                'session' : session,
                'table' : table}
    
    @expose_genshi(template=resource_path('group_content.genshi'))
    def group_content(self, table, row_id):
        session = config.Session()
        tableClass = getattr(appserver.common.model, table)
        if row_id == 'new':
            row  = None
        else:
            #row = session.query(tableClass, row_id)
            row = session.query(tableClass).filter_by(id=row_id).one()
        logging.info ("Row: %s" % row)
        return {'row' : row, 
                'tableClass': tableClass, 
                'session' : session,
                'table' : table}
    
    @expose_genshi(template=resource_path('server_content.genshi'))
    def server_content(self, table, row_id):
        session = config.Session()
        tableClass = getattr(appserver.common.model, table)
        error = None
        if row_id == 'new':
            row  = None
        else:
            #row = session.query(tableClass, row_id)
            row = session.query(tableClass).filter_by(id=row_id).one()
        if row is None:
            logging.info ("New server")
            supervisor_info = None
            error = "Please note that creating a server here only stores the server information in the database. You will still need to install supervisor on the actual host if it is not already there"
        else:
            logging.info ("Getting server info for %s" % row.name)
        
            try:
                supervisor_info = self.controller.getServerInfo(row.name)
            except socket.error:
                error = "Can't get to server XMLRPC  http://%s:%s, please check if supervisor is running" % (row.host, row.port)
                supervisor_info = None
            
            
            
        db_info = None if row is None else row.applications
        if db_info is not None:
            db_info = dict([(item.name, item) for item in db_info])
        model = appserver.common.model.Server
        # there are some things we have to work out here because
        # they can't be done in the template
        # first, check for last updated time on appserver
        # as well as database
        if supervisor_info is not None:
            # supervisor event listener processes will be listed here,
            # and we should ignore them
            for name, item in supervisor_info.iteritems():
                if name not in db_info:
                    logging.info ("Process %s is not in the database. Ignoring" % name)
                    continue
                has_starttime = (item.get('start') is not None and
                                 item.get('start') != 0)
            
                appserver_start_time = datetime.datetime.fromtimestamp(item['start']) \
                                     if has_starttime else None
                should_update = (appserver_start_time is not None and 
                                 (appserver_start_time < db_info[name].last_updated))
                #logging.info ("Start time %s, last updated %s, start time < last_updated %s" %
                #              (appserver_start_time, db_info[name].last_updated,
                #               appserver_start_time < db_info[name].last_updated))
                item['start_datetime'] = appserver_start_time
                item['should_update'] = should_update
                logging.info (item)

        return {
            'error' : error,
            'server' : row, 
            'supervisor_info' : supervisor_info,
            'db_info'         : db_info,
            'model' : model,
        }
    

    @expose_json
    def save_content(self, *args, **kwargs):
        """
        For some changes we want to restart the error checker process.
        
        If a new application is added
        If user mappings to server or application change
        """
        session = config.Session()
        session.begin()
        logging.info ("kwargs:\n%s" % pprint.pformat(kwargs))
        # do different things depending on whether we get a row ID or not
        row_id = kwargs.pop('row_id')
        tablename = kwargs.pop('table')
        isnew = False
        table = getattr(appserver.common.model, tablename)
        if type(row_id) is str and row_id.lower() == 'new':
            isnew = True
            logging.info ("Creating new row of type %s" % tablename)
            row = eval("appserver.common.model.%s()" % tablename)
        else:
            row_id = int(row_id)
            #row = session.query(table, row_id)
            row = session.query(table).filter_by(id=row_id).one()
        

        #for column in row.__table__._columns:
        for column in table.__table__.columns:
            value = kwargs.get('input_%s' % column.name)
            if column.name == 'last_updated':
                setattr(row, column.name, datetime.datetime.now())
                continue
            if column.type.__class__.__name__ == 'Boolean':
                # checkboxes are handled differently.
                if value is None and getattr(row, column.name) is True:
                    # set it to False
                    setattr(row, column.name, False)
                elif value is not None:
                    setattr(row, column.name, True)
            elif column.primary_key is False:
                setattr(row, column.name, value)
                
        
        # will contain a list of servers which we want to update
        # the current changes that we want to capture are
        # user --> application
        # user --> server
        # application --> server
        ec_servers_to_update = set()
                
        if hasattr(table, '_many_to_many'):
            for other_table_name, relation_attr in table._many_to_many:
                prefix = 'cb_%s_' % relation_attr
                checked = set()
                logging.info ("Checked: %s" % checked)
                for key, value in kwargs.iteritems():
                    if key.startswith(prefix):
                        checked.add(int(key[len(prefix):]))

                relation = getattr(row, relation_attr)
                already_checked = set((i.id for i in relation))
                logging.info ("Already checked: %s" % already_checked)

                to_set = checked - already_checked
                to_remove = already_checked - checked
                logging.info ("To set: %s" % to_set)
                logging.info ("To remove: %s" % to_remove)
                
                other_table = getattr(appserver.common.model, other_table_name)
                for i in to_set:

                    rel = session.query(other_table).filter_by(id=i).one()
                    if other_table_name == 'Server':
                        logging.info ("%s was added to a server, will restart error checker for %s" %
                                      (tablename, rel.name))
                        ec_servers_to_update.add(rel.name)
                    elif tablename == 'User' and other_table_name == 'Application':
                        servers = rel.servers
                        for server in servers:
                            logging.info ("User was added to an application %s, will restart error checker for %s" %
                                          (rel.name, server.name))
                            ec_servers_to_update.add(server.name)
                            
                    
                    #relation.append(session.query(other_table, i))
                    relation.append(rel)
                for i in to_remove:
                    rel = session.query(other_table).filter_by(id=i).one()
                    relation.remove(rel)
                    #relation.remove(session.query(other_table, i))
                    
        if isnew is True:
            session.save(row)
        session.commit()
        

        self.update_error_checkers(ec_servers_to_update)
        
        #logging.info ("\n\n\nSaved: %s %s" % (tablename, row.name))
        # if it's a new item, we need the new row ID
        #if isnew is True:
        m = {'label' : 'name', 'identifier' : 'id' }
        row = session.query(table).filter_by(name=row.name).one()
        items = [ {
            'name' : row.name,
            'id'   : row.id,
        }
                  ]
        m['items'] = items
        logging.info (m)
        return m
        
        
        
    def update_error_checkers(self, servers):
        for serverName in servers:
            proxy = self.controller.getProxy(serverName)
            proxy.supervisor.stopProcess("%s:error_checker" % serverName)
            proxy.supervisor.startProcess("%s:error_checker" % serverName)
        
    @expose_json
    def update_appserver(self, *args, **kwargs):
        # check which server(s) has had details changed
        # execute these remotely
        prefix = 'update_'
        checked = set()
        # this will contain all of the app names to update
        # on this server
        to_update = [] 
        logging.info ("kwargs:\n%s" % pprint.pformat(kwargs))
        for key, value in kwargs.iteritems():
            if key.startswith(prefix):
                # if the key exists at all, it means it was checked
                # if the checkbox isn't checked, it wont' be in kwargs
                # i verified this in the kwargs
                name = key[len(prefix):]
                to_update.append(name)
        
        try:
            self.controller.updateServer(kwargs.pop('input_name'), to_update=to_update)
        except Exception, e:
            logging.exception ("Died trying to set up server")
            return { 'data' : str(e) }
        

