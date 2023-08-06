"""
This is just a model for an application server. There still needs to be something
to implement that application server. 

The default implementation that runs this model is supervisord, which is available at 
http://supervisord.org 

supervisord runs only on Unix. We use something called supervisor-twiddler to control it with
XMLRPC. Apparently supervisor can run on Windows under Cygwin, but I haven't tried it.

Unfortunately since there isn't a cross-platform application server, we can't include it
here. 


"""


from sqlalchemy import Table, Index, Column, ForeignKey, \
        Integer, String, Boolean, Numeric, Float, Date, DateTime, Text
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import datetime

Base = declarative_base()

_ApplicationServer = Table('application_server', Base.metadata, 
    Column('application_id', String(32), ForeignKey('application.id')),
    Column('server_id', String(32), ForeignKey('server.id')),
                           )
_ServerAdmin = Table('server_admin', Base.metadata,
                     Column('server_id', String(32), ForeignKey('server.id')),
                     Column('user_id', String(32), ForeignKey('user.id')),
                     )
_ApplicationGroup = Table('application_group', Base.metadata,
                          Column('application_id', String(32), ForeignKey('application.id')),
                          Column('group_id', String(32), ForeignKey('group.id'))
                          )
_ApplicationUser = Table('application_user', Base.metadata,
                          Column('application_id', String(32), ForeignKey('application.id')),
                          Column('user_id', String(32), ForeignKey('user.id'))
                          )


"""
Most of the fields in this table are taken directly from the supervisord configuration at
http://supervisord.org/manual/current/configuration.html#programx

Not all fields have been added here. 

These concepts should be applicable across all application servers. 
"""

class Application(Base):
    __tablename__ = 'application'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(32), nullable=False, index=True, unique=True)
    cmd = Column('cmd', String(1024), nullable=False) 
    environment = Column('environment', Text, nullable=True) # TODO, need to create a TEXT column in mysql???
    last_updated = Column('last_updated', DateTime, nullable=False, default=datetime.datetime.now())
    uid = Column('uid', String(32), nullable=True) # unix user to run as

    # start configuration items from supervisor.
    # Things that are not obvious will be documented here but for full documentation,
    # please go to http://supervisord.org/manual/current/configuration.html
    # higher value indicates start up last and shut down first
    priority = Column('priority', Integer, nullable=True, default=999)
    autostart = Column('autostart', Boolean, nullable=False, default=False)
    autorestart = Column('autorestart', Boolean, nullable=False, default=True)
    # number of seconds which program needs to stay up for to consider start successful.
    startsecs = Column('startsecs', Integer, nullable=False, default=5)
    # if this is True, then the same as running 2>&1
    redirect_stderr = Column('redirect_stderr', Boolean, nullable=False, default=True)
    # this controls the restart behaviour for an application. 
    job = Column('job', Boolean, nullable=False, default=False)
    
    servers = relation('Server', secondary=_ApplicationServer, backref='applications')
    # This is to help the auto gui generator
    # admins is intentionally not in this because we do not want to have to manage
    # users here. We will manage the user --> application mappings on the user screen. 
    _many_to_many = [('Server', 'servers'), ]#('User', 'admins')]
    
    


class Server(Base):
    __tablename__ = 'server'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(32), nullable=False, index=True, unique=True)
    host = Column('host', String(64), nullable=False, index=True)
    port = Column('port', Integer, nullable=False) # in supervisor - the XMLRPC port
    root = Column('root', String(1024), nullable=False) # root directory of the server 
    uid  = Column('uid', String(32), nullable=True)
    mail_server = Column('mail_server', String(100), nullable=False)
    environment = Column('environment', Text, nullable=True)
    

    
class User(Base):
    __tablename__ = 'user'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(32), nullable=False)
    email = Column('email', String(128), nullable=False) 
    servers = relation('Server', secondary=_ServerAdmin, backref='server_admins')
    applications = relation('Application', secondary=_ApplicationUser, backref='app_admins')

    _many_to_many = [('Server', 'servers'), ('Application', 'applications')]

class Group(Base):
    # This is a process group not a user group! 
    __tablename__ = 'group'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(32), nullable=False)
    applications = relation('Application', secondary=_ApplicationGroup, backref='group')
    
def setup(session):
    #a = Application(name='testenv', cmd='python testenv.py')
    a3 = Application(name='TDS', cmd="python -u tds/tds_service.py")

    #session.save(a)	
    #session.save(a2)
    session.save(a3)
    #session.save(a4)
    #s = session.query(Server).filter_by(name='Ethelred')
    s = Server(name='Ethelred', host='ldndev01', port=9001, 
               root='/mnt/GLCDEV/appservers/Ethelred')
    #s2 = Server(name='Ethelfleda', host='localhost', port=9001,
    #            root='/home/mog/appservers/Ethelfleda')    
    #s2 = Server(name='Cynric', host='ldnapp11', port=9001,
    #            root='/mnt/GLCDEV/appservers/Cynric')    
    
    session.save(s)
    #a.servers.append(s2)
    #a2.servers.append(s)
    #a3.servers.append(s)
    a3.servers.append(s)
    #a4.servers.append(s2)
    session.commit()
    """
    print 'winkle'

    session = Session()
    a = session.query(Application).filter_by(name='STP').one()
    s = Server(name='Wulfnoth', host='localhost', port=9002)
    
    a.servers.append(s)
    
    session.commit()

    session = Session()
    a = session.query(Application).filter_by(name='Risk').one()
    s = session.query(Server).filter_by(name='Wulfnoth').one()
    a.servers.append(s)
    session.commit()    
    """
if __name__ == '__main__':
    from sqlalchemy import create_engine, and_, or_
    #engine = create_engine('mysql://root:broadwick@ldnapp10/appserver', echo=True)
    #engine = create_engine('mysql://root:broadwick@localhost/appserver', echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(engine, autoflush=True, transactional=True)
    
    session = Session()
    setup(session)
    
