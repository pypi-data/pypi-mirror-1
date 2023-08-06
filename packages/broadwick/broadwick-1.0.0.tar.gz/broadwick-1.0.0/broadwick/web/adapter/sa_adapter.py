import logging


class SARequestAdapter(object):
    def __init__(self, session_func):
        self.session_func = session_func
        
    def before_request(self, request, resource, params):
        request.sa_session = self.session_func()
        logging.debug('sa_session open: %r' % request.sa_session)
        
    def after_request(self, request, result):
        logging.debug('sa_session close: %r' % request.sa_session)
        request.sa_session.close()
