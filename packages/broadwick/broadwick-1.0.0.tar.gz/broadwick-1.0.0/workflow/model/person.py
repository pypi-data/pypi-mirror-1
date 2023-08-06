from sqlalchemy import *
from sqlalchemy.orm import *
from workflow.model.base import Base

person_role = Table('person_role', Base.metadata,
    Column('person_id', Integer, ForeignKey('person.id')),
    Column('role_id', Integer, ForeignKey('role.id')),
    mysql_engine='InnoDB'
    )

class Role(Base):
    __tablename__='role'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    name =  Column(String(80), nullable=False, unique=True)

    @classmethod
    def find_or_create(cls, session, name):
        try:
            return session.query(cls).filter_by(name=name).one()
        except:
            result = cls(name=name)
            session.add(result)
            return result

    
class Person(Base):
    __tablename__ = 'person'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = Column(Integer, primary_key=True)
    forename =  Column(String(80), nullable=False)
    surname =  Column(String(80), nullable=False)
    dob =  Column(Date, nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    password = Column(String(16))
    
    roles = relation(Role, secondary=person_role)
    
    