from broadwick.workflow import *
import logging


class Sample(object):
    
    @process_def(name='sample', context={'greeting': 'hello world', 'complete': False })
    def __init__(self):
        "a process of steps"
        pass
    
    @init_def(name='sample.start', automatic=True)
    def _start(self, context):
        "begins a stepped process"
        logging.info('start %s' % context.workItemId)
        logging.info('start: %s' % context['greeting'])
        
    @activity_def(name='sample.step', precondition=['sample.start'], postcondition=['sample.end'], automatic=True)
    def _step(self, context):
        "steps a stepped process"
        logging.info('step %s' % context.workItemId)
        if context.get('complete') == False:
            logging.info('completed prematurely.')
            context.complete()
        logging.info('step: %s' % context['greeting'])
    
    @activity_def(name='sample.end', automatic=False)
    def _end(self, context):
        "ends a stepped process"
        logging.info('end: %s' % context['greeting'])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    quickstart_stomp(Sample())
