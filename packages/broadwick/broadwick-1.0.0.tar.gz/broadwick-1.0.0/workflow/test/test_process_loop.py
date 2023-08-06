from broadwick.workflow import *
from broadwick.workflow.process_definition import to_xml
import logging


class LoopSample(object):
    
    @process_def(name='loop_sample', context={'greeting': 'hello loop world'})
    def __init__(self):
        "a process of loop steps"
        pass
    
    @init_def(name='sample.loop_start', automatic=True)
    def _start(self, context):
        "begins a loop process"
        logging.info('start: %s' % context['greeting'])
        
    @activity_def(name='sample.loop', precondition=['sample.loop_start'], automatic=True)
    def _loop(self, context):
        "steps a looped process"
        if context.setdefault('times', 1) < 3:
            logging.info('looping: %s' % context['times'])
            context['times']=context['times']+1
            context.callAgain()
        logging.info('looped: %s' % context['times'])
    
    @activity_def(name='sample.loop_end', precondition=['sample.loop'], join=True, automatic=True)
    def _end(self, context):
        "ends a loop process"
        logging.info('end: %s' % context['greeting'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    control = LoopSample()
    to_xml(control, 'split_sample.xml')
    quickstart_stomp(control)