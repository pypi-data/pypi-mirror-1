from broadwick.workflow import *
from broadwick.workflow.process_definition import to_xml
import logging


class SplitSample(object):
    
    @process_def(name='split_sample', context={'greeting': 'hello world', 'left-work': [1,2,3,4]})
    def __init__(self):
        "a process of split steps"
        pass
    
    @init_def(name='sample.split_start', automatic=True)
    def _start(self, context):
        "begins a stepped process"
        logging.info('start: %s' % context['greeting'])
        
    @activity_def(name='sample.step_right', precondition=['sample.split_start'], automatic=True)
    def _step_right(self, context):
        "steps a stepped process"
        logging.info('step right: %s' % context['greeting'])
    
    @activity_def(name='sample.step_left', precondition=['sample.split_start'], automatic=True)
    def _step_left(self, context):
        "splits left-work"
        index = context.setdefault('work-index',0)
        work_length = len(context['left-work'])
        if index < work_length:
            context['work']=context['left-work'][index]
            context['work-index']=index+1
            if index+1 < work_length:
                context.split()
        logging.info('step left: %s' % context['greeting'])
    
    @activity_def(name='sample.left_work', precondition=['sample.step_left'], automatic=True)
    def _left_work(self, context):
        "performs left-work"
        context['result:%s' % context['work-index']]= float(context['work'])/2.0
        logging.info('work: %s' % context['work'])
    
    @activity_def(name='sample.split_end', precondition=['sample.step_left', 'sample.step_right', 'sample.left_work'], join=True, automatic=True)
    def _end(self, context):
        "ends a stepped process"
        logging.info('end: %s' % context['greeting'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    control = SplitSample()
    to_xml(control, 'split_sample.xml')
    quickstart_stomp(control)