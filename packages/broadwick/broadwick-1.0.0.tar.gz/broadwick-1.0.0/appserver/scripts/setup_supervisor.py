"""
Go to database
Look at what hostname this is
Get all the relevant servers
Generate the configuration

You must have sqlalchemy and broadwick installed 
in order for this script to work. 

"""
import socket
import os
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser
from appserver.common import model
import logging

from broadwick.utils import log
from broadwick.utils import network_utils as nu

from appserver.common import model

class ConfigGenerator(object):

    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     "template.conf")

        self.engine = create_engine(self.db_uri)
        self.SessionCls = sessionmaker(self.engine, autoflush=True, autocommit=True)
        #sa_utils.create_and_upgrade(self.engine, model.Base.metadata)

    def setup_dirs(self, dbserver):
        conf = os.path.join(dbserver.root, "conf")
        log = os.path.join(dbserver.root, "log")
        apps = os.path.join(dbserver.root, "apps")

        dirs = [conf, log, apps]
        for dir in dirs:
            if not os.path.isdir(dir):
                os.makedirs(dir)

    def setup(self):
        session = self.SessionCls()

        # we don't have to lowercase this because SQLAlchemy is smart enough to do it
        servers = session.query(model.Server).filter_by(host = socket.gethostname().lower()).all()
        if not servers: # try fqdn
            servers = session.query(model.Server).filter_by(host=socket.getfqdn(socket.gethostname()).lower()).all()

        if not servers: # try IP address
            servers = session.query(model.Server).filter_by(host=nu.get_ip_address()).all()
            
        logging.info ("Got servers: %s"  % servers)

        for server in servers:
            logging.info ("Checking server: %s" % server.name)
            attr_dict = dict([(attr, getattr(server, attr)) for attr in server.__dict__])
            if 'environment' in attr_dict and attr_dict['environment'] is not None:
                attr_dict['environment'] = attr_dict['environment'].replace("\n",",")
            else:
                attr_dict['environment'] = ''

            self.setup_dirs(server)
            dest = os.path.join(server.root, "conf")

            adminlist = []
            #for admin in server.server_admins:
            #    adminlist.append(admin.email)
            #attr_dict['adminlist'] = ",".join(adminlist)
            attr_dict['db_uri'] = self.db_uri
            attr_dict['server_name'] = server.name
            
            template = open(self.template).read()
    
            genfile = template % attr_dict
    
            filename = os.path.join(dest, "%s.conf" % server.name.lower())
            if (os.path.exists (filename)):
                logging.info ("File exists: %s " % filename)
                os.rename(filename, "%s.%s" 
                          % (filename, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            f = open(filename, "w")
            f.write(genfile)
            f.close()

def main():
    log.initialise_logging()
    parser = OptionParser(usage='%prog: [options] database_uri')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Incorrect number of arguments passed. I need a database uri')
        
    db_uri = args[0]
    cg = ConfigGenerator(db_uri)
    cg.setup()

if __name__ == '__main__':
    main()
