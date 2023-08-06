from workflow import model


class BaseDirector(object):
    
    def __init__(self, control):
        self.control = control
        control.register_director(self)
        
        
    def perform(self, context):
        return False
    
    def describe(self, name):
        pass

    def actors(self):
        return []

    def _with_item(self, item_id, func, *args, **kwargs):
        session = self.control.session()
        item = session.query(model.WorkItem).get(int(item_id))
        result = func(item, *args, **kwargs)
        session.commit()
        session.close()
        return result
