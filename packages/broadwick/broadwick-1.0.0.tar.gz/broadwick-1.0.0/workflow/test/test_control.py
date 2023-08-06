from unittest import TestCase
from workflow.control import Control
from broadwick.workflow.process_utils import dictFromClass
from workflow import model, config
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)

class TestModel(TestCase):
    
    control = Control(**dictFromClass(config, 'sql'))
    
    def setUp(self):
        self.session = self.control.session()
        
    def tearDown(self):
        self.session.close()
        
    def test_person(self):
        peterb = model.Person(forename='Peter', surname='Bunyan', dob=datetime.date(1960,5,6),
                              email='pete@blueshed.co.uk', password='daisya')
        self.session.add(peterb)
        admin = model.Role(name='admin')
        self.session.add(admin)
        peterb.roles.append(admin)
        self.session.commit()
        
        
    def test_activity(self):
        login = model.Activity(name='login')
        self.session.add(login)
        flds = ['email', 'password']
        login['flds'] = flds
        self.session.add(login)
        model.Activity.find_or_create(self.session,'logout')
        self.session.commit()
        self.assertEquals(flds, login['flds'])
        
    
    def perform(self, session, item):
        self.control.begun(item)
        self.control.done(item, {})
        logging.info('worked %r' % item)
        session.commit()
        
    def test_process(self):
        self.control.register_director(self)
        login = model.Activity.find_or_create(self.session, 'login')
        logout = model.Activity.find_or_create(self.session, 'logout')
        process = model.Process(name='process')
        self.session.add(process)
        process['test']='value'
        process.defineInitActivities([login])
#        process.definePreCondition(logout, [login])
        process.definePostCondition(login, [logout])
        process['test']='value2'
        self.control.start(self.session, process, {})
        self.assertEquals(process['test'],'value2')
        self.assertEquals(process.context(),{'test':'value2'})
        self.session.commit()
        
        