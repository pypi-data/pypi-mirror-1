"""
Go to database
Get all processes that should be running
"""
import broadwick.utils.mail as bwmail
import appserver.adaptors.supervisor as supervisor

import socket, os, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from optparse import OptionParser
from appserver.common import model
import logging

from broadwick.utils import log
from broadwick.utils import network_utils as nu

class Setup(object):
    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.engine = create_engine(self.db_uri)
        self.SessionCls = sessionmaker(self.engine, autoflush=True, autocommit=True)
        self.proxy = supervisor.AppserverProxy(self.db_uri) #self.SessionCls)

    def setup(self):
        session = self.SessionCls()
        servers = session.query(model.Server).filter_by(host=socket.gethostname().lower()).all()
        if not servers: # try fqdn
            servers = session.query(model.Server).filter_by(host=socket.getfqdn(socket.gethostname()).lower()).all()
        if not servers: # try IP address
            servers = session.query(model.Server).filter_by(host=nu.get_ip_address()).all()

        for server in servers:
            logging.info ("Checking server: %s" % server.name)
            # get all the applications that ought to be running on this server
            try:
                self.proxy.updateServer(server.name)
            except socket.error, e:
                # find out who the admin is
                
                adminlist = []
                for admin in server.server_admins:
                    adminlist.append(admin.email)
                
                
                bwmail.sendmail(to=adminlist, 
                                subject="Can't set up supervisor %s  on %s" %  (server.name, socket.gethostname()),
                                message="Because of %s" % e,
                                email_from="Appserver@%s" % socket.gethostname(),
                                mail_server=os.environ.get('SMTP_SERVER'))
                raise                                                                


def main():
    log.initialise_logging()

    parser = OptionParser(usage='%prog: [options] database_uri')
    
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Incorrect number of arguments passed. I need a database uri')
        
    db_uri = args[0]
    setup = Setup(db_uri)
    setup.setup()

if __name__ == '__main__':
    main()
