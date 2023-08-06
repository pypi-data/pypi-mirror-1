"""
  Author:     Peter Bunyan
  Program:    process_utils

  Date:       Mar. 21, 2008

  Description:    All sorts of Process Goodies
"""
from UserDict import UserDict
import inspect
import base64
import pickle
import types
import sys
import logging
    

def SyncContext(source, context):
    for key, value in context.items():
        try:
            if source[key] != value:
                source[key] = value
                logging.debug('updated %s:%s' % (key, value))
        except KeyError:
            source[key] = value
            logging.debug('added %s:%s' % (key, value))


class WaitException(Exception):
    pass
    
class AlreadyDoneException(Exception):
    pass

class SplitException(Exception):
    pass

class CompleteException(Exception):
    pass

class ChoiceException(Exception):
    def __init__(self, choice, **kw):
        Exception.__init__(self, **kw)
        self.choice = choice

class CallAgainException(Exception):
    def __init__(self, when, **kw):
        Exception.__init__(self, **kw)
        self.when = when
        
        
def process_def(func=None, name=None, context=None):
    def wfpdecorate_(func):
        func.wfp = True
        func.name = name
        func.context = context
        return func

    if isinstance(func, (types.FunctionType, types.MethodType)):
        # called directly, before the method has been bound
        return wfpdecorate_(func)
    else:
        # called as a decorator
        return wfpdecorate_


def init_def(func=None, name=None, postcondition=None, choice=None,
         automatic=False, display=None, perform=None, context=None):
    assert not isinstance(postcondition, (str, unicode)), 'postcondition should be a list of strings or None'
    def wfidecorate_(func):
        func.wfi = True
        func.name = name
        func.postcondition = postcondition
        func.choice = choice
        func.automatic = automatic
        func.display = display
        func.perform = perform
        func.context = context
        return func

    if isinstance(func, (types.FunctionType, types.MethodType)):
        # called directly, before the method has been bound
        return wfidecorate_(func)
    else:
        # called as a decorator
        return wfidecorate_


def activity_def(func=None, name=None,
             precondition=None, postcondition=None, choice=None,
             automatic=False, join=None, display=None, perform=None, context=None):

    assert not isinstance(choice, (str, unicode)), 'choice should be a list of strings or None'
    assert not isinstance(precondition, (str, unicode)), 'precondition should be a list of strings or None'
    assert not isinstance(postcondition, (str, unicode)), 'postcondition should be a list of strings or None'

    def decorate_(func):
        func.wfa = True
        func.name = name
        func.precondition = precondition
        func.postcondition = postcondition
        func.choice = choice
        func.join = join
        func.automatic = automatic
        func.display = display
        func.perform = perform
        func.context = context
        return func

    assert postcondition is None or choice is None
    if isinstance(func, (types.FunctionType, types.MethodType)):
        # called directly, before the method has been bound
        return decorate_(func)
    else:
        # called as a decorator
        return decorate_
    
    
def localMethodDict(obj):
    result = {}
    for methodName in dir(obj):
        try:
            method = getattr(obj, methodName)
            if hasattr(method,'wfi') and getattr(method,'wfi') is True:
                name = _getAttr(method, 'name', methodName)
                result[name] = method
            if hasattr(method,'wfa') and getattr(method,'wfa') is True:
                name = _getAttr(method, 'name', methodName)
                result[name] = method
        except AttributeError:
            logging.exception('looking for: %s' % methodName)
            pass
    return result
    
    
def _getAttr(obj, attr, default):
    if hasattr(obj,attr)and getattr(obj,attr) is not None:
        return getattr(obj,attr)
    return default

  
def StompToContext(body):
    return pickle.loads(body)

def ContextToStomp(context):
    return pickle.dumps(context)


def dictFromClass(module, *args):
    params = {}
    for name in args:
        obj = getattr(module, name, None)
        for attr in dir(obj):
            if not attr.startswith('_'):
                val = getattr(obj, attr)
                if not callable(val):
                    params[attr] = val
    return params



class ClientContext(UserDict):
    
    def __init__(self, dict=None, workItemId=None, activity=None, perform=None, 
                 replyTo=None, success=None, service=None, **kwargs):
        UserDict.__init__(self, dict, **kwargs)
        self.workItemId = workItemId
        self.activity = activity
        self.perform = perform or activity
        self.replyTo = replyTo
        self.success = success
        self.service = service
        self._err = self._msg = self._choice = self._when = self._result = None
    
    def __setitem__(self, key, item):
        if key.startswith("grid.") and key.endswith(".script") and (type(item) not in (str, unicode)):
            # We need to marshal a function to the grid
            # Make sure they passed a function object and not an instance method
            if type(item) != types.FunctionType:
                raise Exception("you can not marshal a grid function of type %s" % type(item))
            source = inspect.getsource(item)
            self.data["grid.scriptSource"] = source 
            self.data["grid.scriptEntrypoint"] = item.__name__
            self.data[key] = "<marshaled code>"
        else:
            self.data[key] = item
            
    def _set_result(self, result, choice=None, when=None, err=None, msg=None):
        self._result = result
        self._choice = choice
        self._when = when
        self._err = err
        self._msg = msg
        
    def _result_dict(self):
        return { 'result' : self._result, 'err': self._err, 'msg': self._msg, 
                 'choice': self._choice, 'when': self._when,
                 'context': self.data, 'correlation-id':  self.workItemId }
    
    def context(self):
        return {
                'dict':self.data,
                'workItemId':self.workItemId,
                'activity': self.activity,
                'replyTo': self.replyTo,
                'success': self.success
                }
        
    def complete(self):
        """
This will set the workItem to done but not spawn and conditions.
If the workflow has no further items it will be completed
        """
        raise CompleteException()
    
    def choose(self, choice):
        """
This will perform the post-condition of the choice
        """
        raise ChoiceException(choice)
    
    def callAgain(self, when=0):
        """
This will perform no conditions and call the workItem again
after when seconds.
        """
        raise CallAgainException(when)
    
    def split(self):
        """
This will perform all conditions and call the workItem again
immmediately
        """
        raise SplitException()


def DisplayToContext(display):
    return ClientContext(**pickle.loads(base64.decodestring(display)))

def ContextToDisplay(context):
    return base64.encodestring(pickle.dumps(context.context()))

    
