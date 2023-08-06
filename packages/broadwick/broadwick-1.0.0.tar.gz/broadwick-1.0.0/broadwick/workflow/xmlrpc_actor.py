from broadwick.web.xmlrpc import expose_xmlrpc, DocXMLRPC
from twisted.internet import defer
from twisted.python import failure
from broadwick.workflow.base_actor import BaseActor
from broadwick.workflow.process_utils import *
import logging
import xmlrpclib


class XMLRpcActor(BaseActor):
    
    def __init__(self, process_host='localhost', process_port=8081):
        BaseActor.__init__(self)
        self.host=process_host
        self.port=process_port        
        self.url = "http://%s:%s/RPC2" % (self.host, self.port)
        self.process = xmlrpclib.ServerProxy(self.url)
        
    @expose_xmlrpc
    def describe(self):
        return BaseActor.describe(self)
    
    @expose_xmlrpc
    def perform(self, workItemId, activity, context, perform=None ):
        cc = ClientContext(dict=context,
                           workItemId = workItemId,
                           activity = activity,
                           perform = perform,
                           service = self)
        try:
            self.doWork(cc)
            self.doneWork(None, cc)
        except Exception, ex: 
            self.errorInWork(failure.Failure(), cc)
            logging.exception(ex)
        result = cc._result_dict()
        logging.debug(result)
        return result
                    
                    
    def startProcess(self, processName, context):
        self.process.startProcess(processName, context)



def quickstart_xmlrpc(target, port, title=None, documentation=None, process_host='localhost', process_port=8081):
    from twisted.internet import reactor
    import broadwick.web.utils  
    
    actor = XMLRpcActor()
    actor.addTarget(target)
    title = title if title is not None else 'process actor %s' % target.__class__.__name__
    documentation = documentation if documentation is not None else target.__class__.__doc__
    xmlrpc_view = DocXMLRPC(actor,
                     allow_none = True, 
                     server_title = title,
                     server_name = title,
                     server_documentation = documentation,                     
                     )
    broadwick.web.utils.listen(xmlrpc_view, port)
    reactor.run()
    