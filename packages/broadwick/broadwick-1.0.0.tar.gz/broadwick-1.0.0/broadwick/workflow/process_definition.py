from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import tostring
import pickle, logging
    
class ProcessDefinition(object):
    class Condition(object):
        def __init__(self, activity, condition):
            self.activity = activity
            self.condition = condition
                
    class PostCondition(Condition):
        def __init__(self, activity, condition, choice=False):
            ProcessDefinition.Condition.__init__(self, activity, condition)
            self.choice = choice
            
        def toXML(self, process):
            ePostCondition = Element('postcondition')
            ePostCondition.attrib['activity']=self.activity
            ePostCondition.attrib['choice']=str(self.choice)
            if self.condition:
                for actName in self.condition:
                    eActivity = Element('result')
                    eActivity.attrib['activity']=actName
                    ePostCondition.append(eActivity)
            process.append(ePostCondition)
            
            
    class PreCondition(Condition):
        def __init__(self, activity, condition=None, join=False):
            ProcessDefinition.Condition.__init__(self, activity, condition)
            self.join = join

        def toXML(self, process):
            ePreCondition = Element('precondition')
            ePreCondition.attrib['result'] = self.activity
            ePreCondition.attrib['join'] = str(self.join)
            if self.condition:
                for actName in self.condition:
                    eActivity = Element('condition')
                    eActivity.attrib['activity']=actName
                    ePreCondition.append(eActivity)
            process.append(ePreCondition)
            
    class InitCondition(PreCondition):
        
        def toXML(self, process):
            eInits = Element('init')
            eInits.attrib['activity']=self.activity
            process.append(eInits)
            
    
    class Process(object):
        def __init__(self, name, context, notes):
            self.name = name
            self.context = context
            self.notes = notes
            self.preconditions = []
            self.postconditions = []
            
    def __init__(self):
        self.processes = []
        self.targets = []
        self.activities = {}
        
    def activity_names(self):
        return self.activities.keys()
        
    def wfprocess(self, name=None, context=None, notes=None):
        self.processes.append(ProcessDefinition.Process(name, context, notes))
    
    def wfinit(self, func=None, name=None, postcondition=None, 
               choice=False, automatic=False, process=None, display=None,
               perform=None, context=None):
        assert process or self.processes, 'wfinit needs a process passed either here or via a previous wfprocess call'
        process = process or self.processes[-1]
        self.addActivity(name, automatic, func, display, perform=perform, context=context)
        if postcondition is not None:
            process.postconditions.append(ProcessDefinition.PostCondition(name, postcondition, choice))
        process.preconditions.append(ProcessDefinition.InitCondition(name))
        
    
    def wfactivity(self, func=None, name=None, 
                   precondition=None, postcondition=None, choice=None,
                   automatic=False, join=False, process=None, display=None, 
                   perform=None, context=None):
        assert not (postcondition is not None and choice is not None)
        process = process or (len(self.processes) > 0 and self.processes[-1] or None)
        self.addActivity(name, automatic, func, display, perform=perform, context=context)
        if process is not None:
            if postcondition or choice:
                process.postconditions.append(ProcessDefinition.PostCondition(name, postcondition or choice, 
                                                                           choice and True or False))
            if precondition is not None:
                process.preconditions.append(ProcessDefinition.PreCondition(name, precondition, join))
    
    def addActivity(self, name, automatic=False, func=None, display=None, notes=None, 
                    perform=None, context=None):
        if not self.activities.has_key(name):
            self.activities[name] = (name,automatic,func,display,notes,perform,context)
            logging.debug(self.activities[name])
        
    def getTarget(self, activityName):
        return self.activities[activityName][2]
    
    def toElement(self):
        root = Element('define')
        for local in self.processes:
            process = Element('process')
            process.attrib['name']=local.name
            root.append(process)
            if local.context is not None:
                eContext = Element('context')
                for key,value in local.context.items():
                    eValue = Element('value')
                    eValue.attrib['key']=key
                    eValue.text = pickle.dumps(value)
                    eContext.append(eValue)
                process.append(eContext)
            if local.notes is not None:
                eNotes = Element('notes')
                eNotes.text = local.notes
                process.append(eNotes)
            for postcondition in local.postconditions:
                postcondition.toXML(process)
            for precondition in local.preconditions:
                precondition.toXML(process)
        for key, value in self.activities.items():
            eAct = Element('activity')
            eAct.attrib['name']=key
            if value[1]==True:
                eAct.attrib['automatic']='True'
            if value[3] is not None:
                eAct.attrib['display']=value[3]
            if value[4] is not None:
                eNotes = Element('notes')
                eNotes.text = value[4]
                eAct.append(eNotes)
            if value[5] is not None:
                eAct.attrib['perform']=value[5]
            if value[6] is not None:
                eContext = Element('context')
                for key,value in value[6].iteritems():
                    eValue = Element('value')
                    eValue.attrib['key']=key
                    eValue.text = pickle.dumps(value)
                    eContext.append(eValue)
                eAct.append(eContext)
            root.append(eAct)
        return root
    
    
    def toXML(self):
        return tostring(self.toElement())
    
    
    def addTarget(self, inst, context=None):
        self.targets.append(inst)
        obj = inst.__class__
        mapping = {}
        for methodName in dir(obj):
            method = getattr(obj, methodName)
            target = getattr(inst, methodName)
            automatic = hasattr(method,'automatic') and getattr(method,'automatic') is True
            display = hasattr(method,'display') and getattr(method,'display') or None
            perform = hasattr(method,'perform') and getattr(method,'perform') or None
            _context = hasattr(method,'context') and getattr(method,'context') or None
            if hasattr(method,'wfp') and getattr(method,'wfp') is True:
                name = _getAttr(method, 'name', obj.__name__)
                context = _getAttr(method, 'context', context)
                self.wfprocess(name, context, notes=method.__doc__)
            if hasattr(method,'wfi') and getattr(method,'wfi') is True:
                name = _getAttr(method, 'name', methodName)
                mapping[methodName] = name
                self.addActivity(name, automatic=automatic, func=target, display=display, 
                                 notes=method.__doc__, perform=perform, context=_context)
            if hasattr(method,'wfa') and getattr(method,'wfa') is True:
                name = _getAttr(method, 'name', methodName)
                mapping[methodName] = name
                self.addActivity(name, automatic=automatic, func=target, display=display,
                                 notes=method.__doc__, perform=perform, context=_context)
        for methodName in dir(obj):
            method = getattr(obj, methodName)
            target = getattr(inst, methodName)
            automatic = hasattr(method,'automatic') and getattr(method,'automatic') is True
            display = hasattr(method,'display') and getattr(method,'display') or None
            perform = hasattr(method,'perform') and getattr(method,'perform') or None
            _context = hasattr(method,'context') and getattr(method,'context') or None
            if hasattr(method,'wfi') and getattr(method,'wfi') is True:
                name = _getAttr(method, 'name', methodName)
                if hasattr(method,'choice') and getattr(method,'choice') is not None:
                    activityNames = getattr(method,'choice')
                    self.wfinit(func=target, name=_getName(name, mapping),
                                postcondition=[_getName(n, mapping) for n in activityNames],
                                choice=True,
                                automatic=automatic, display=display,
                                perform=perform, context=_context)
                elif hasattr(method,'postcondition') and getattr(method,'postcondition') is not None:
                    activityNames = getattr(method,'postcondition')
                    self.wfinit(func=target, name=_getName(name, mapping), 
                                postcondition=[_getName(n, mapping) for n in activityNames], 
                                automatic=automatic, display=display,
                                perform=perform, context=_context)
                else:
                    self.wfinit(func=target, name=name,automatic=automatic)
            if hasattr(method,'wfa') and getattr(method,'wfa') is True:
                name = _getAttr(method, 'name', methodName)
                join = getattr(method,'join')
                if join is None:
                    join = False
                if hasattr(method,'choice') and getattr(method,'choice') is not None:
                    activityNames = getattr(method,'choice')
                    self.wfactivity(func=target, name=_getName(name, mapping), 
                                    choice=[_getName(n, mapping) for n in activityNames], 
                                    automatic=automatic, join=join, display=display,
                                    perform=perform, context=_context)
                    if hasattr(method,'precondition') and getattr(method,'precondition') is not None:
                        activityNames = getattr(method,'precondition')
                        self.wfactivity(func=target, name=_getName(name, mapping), 
                                        precondition=[_getName(n, mapping) for n in activityNames],
                                        automatic=automatic, join=join, display=display,
                                        perform=perform, context=_context)
                elif hasattr(method,'postcondition') and getattr(method,'postcondition') is not None:
                    activityNames = getattr(method,'postcondition')
                    self.wfactivity(func=target, name=_getName(name, mapping), 
                                    postcondition=[_getName(n, mapping) for n in activityNames],
                                    automatic=automatic, join=join, display=display,
                                    perform=perform, context=_context)
                    if hasattr(method,'precondition') and getattr(method,'precondition') is not None:
                        activityNames = getattr(method,'precondition')
                        self.wfactivity(func=target, name=_getName(name, mapping), 
                                        precondition=[_getName(n, mapping) for n in activityNames],
                                        automatic=automatic, join=join, display=display,
                                        perform=perform, context=_context)
                elif hasattr(method,'precondition') and getattr(method,'precondition') is not None:
                    activityNames = getattr(method,'precondition')
                    self.wfactivity(func=target, name=_getName(name, mapping), 
                                    precondition=[_getName(n, mapping) for n in activityNames],
                                    automatic=automatic, join=join, display=display,
                                    perform=perform, context=_context)
                else:
                    self.wfactivity(func=target, name=_getName(name, mapping),
                                    automatic=automatic, join=join, display=display,
                                    perform=perform, context=_context)
        
    
            
def _getName(name, map):
    try:
        return map[name]
    except KeyError:
        return name
   
def _getAttr(obj, attr, default):
    if hasattr(obj,attr)and getattr(obj,attr) is not None:
        return getattr(obj,attr)
    return default


def to_xml(control, filename):
    pdef = ProcessDefinition()
    pdef.addTarget(control)
    ElementTree(pdef.toElement()).write(filename)
                
                
if __name__ == '__main__':
    from process_utils import *
    logging.basicConfig(level=logging.DEBUG)
    
    class TestControl(object):
        def __init__(self):
            pass
        process_def(__init__, name='Test')
        
        def do(self, context):
            pass
        init_def(do, name='test.do', automatic=True)
        
        def afterdo(self, context):
            """documentation test"""
            pass
        activity_def(afterdo, name='test.after', 
                   precondition=['do'], postcondition=['afterdo1'], 
                   automatic=True, perform=None,
                   context={'hello':'world','testing':123})
         
        def afterdo1(self, context):
            pass
        activity_def(afterdo1, name='test.after1', automatic=True)
        
        def afterdo2(self, context):
            pass
        activity_def(afterdo2, name='test.after2', precondition=['afterdo'], automatic=True)
        
        def joinafter(self, context):
            pass
        activity_def(joinafter, name='test.join', precondition=['afterdo1','afterdo2'], join=True)

    pdef = ProcessDefinition()
    pdef.wfprocess('Test')
    pdef.wfinit(name='test.do', automatic=True)
    pdef.wfactivity(name='test.after', precondition=['test.do'], postcondition=['test.after1'], automatic=True,
                    perform=None, context={'hello':'world','testing':123})
    pdef.wfactivity(name='test.after1', automatic=True)
    pdef.wfactivity(name='test.after2', precondition=['test.after'], automatic=True)
    pdef.wfactivity(name='test.join', precondition=['test.after1','test.after2'], join=True)

    ElementTree(pdef.toElement()).write('process1.xml')
    
    to_xml(TestControl(), 'process2.xml')
        
    print 'done!'
