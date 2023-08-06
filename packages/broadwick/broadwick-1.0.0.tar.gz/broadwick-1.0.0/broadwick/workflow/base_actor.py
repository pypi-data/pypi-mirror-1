from broadwick.workflow.process_definition import ProcessDefinition
from broadwick.workflow.process_utils import *


class BaseActor(object):

    def __init__(self):
        self.meta = ProcessDefinition()

    def addTarget(self, target):
        self.meta.addTarget(target)
#        logging.debug(self.describe().replace('\n',''))

    def errorInWork(self, error, context):
        try:
            if isinstance(error.value, SplitException):
                self.split(context)
            elif isinstance(error.value, CallAgainException):
                self.callAgain(context, error.value.when)
            elif isinstance(error.value, ChoiceException):
                self.choice(context, error.value.choice)
            elif isinstance(error.value, CompleteException):
                self.complete(context)
            else:
                msg = err = '???'
                try:
                    err = str(error.value)
                    msg = str(error.tb)
                except:
                    logging.exception(
                            "An exception occurred in your activity however we "
                            "were unable to get a string representation of the exception. "
                            "If your exception is derived from Exception, did you remember to call Exception.__init__ ?"
                            )

                self.error(context, err, msg)
                logging.error('failed:\n%s' % error.getTraceback())
        except:
            logging.exception('Error in errorInWork!')
            raise
    
    def describe(self):
        return self.meta.toXML()
    
    def activities(self):
        return self.meta.activity_names()
    
    def displayToContext(self, display):
        if display is None:
            result = ClientContext()
        result = DisplayToContext(display)
        result.service = self
        return result


    @classmethod
    def contextToDisplay(cls, context):
        return ContextToDisplay(context)


    def doWork(self, context):
        # NOTE: context.perform is usually the same as context.activity.
        # The only time it's different is when someone renames a generic activity
        # e.g. <activity name="calc_squares" perform="runGridJob"/>
        worker = self.meta.getTarget(context.perform)
        return worker(context)

    def doneWork(self, reason, context):
        context._set_result('__done__')
        
    def split(self, context):
        context._set_result('__split__')
        
    def callAgain(self, context, when):
        context._set_result('__call_again__', when=when)
    
    def choice(self, context, choice):
        context._set_result('__choice__', choice=choice)
        
    def complete(self, context):
        context._set_result('__complete__')
        
    def error(self, context, err, msg):
        context._set_result('__error__', err=err, msg=msg)
                            
    def startProcess(self, processName, context):
        raise NotImplemented()

