# Example usage:
#    python -m appserver.dashboard.main --verbose --static=~/Development/thirdparty/ --appserver_adaptor=appserver.adaptors.supervisor mysql://appserver:appserver@localhost/appserver 

import os
import logging
from optparse import OptionParser

from twisted.internet import reactor
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker


import broadwick.web.utils
import broadwick.utils.log

from appserver.dashboard import config
from appserver.common import model

class App(object):
    def __init__(self, database_uri, static_path, dojo, appserver_adaptor, web_port, verbose):
        static_path = os.path.abspath(os.path.expanduser(static_path))
        config.static_path = static_path
        config.dojo = dojo
        config.appserver_adaptor = appserver_adaptor
        engine = create_engine(database_uri, echo=verbose, pool_recycle=3600)

        model.Base.metadata.create_all(engine)
        config.Session = sessionmaker(engine, autoflush=True, autocommit=True)
        
        from appserver.dashboard import dashboard


        view = dashboard.View()
        
        exec "import %s as sp" % config.appserver_adaptor
        view.controller = sp.AppserverProxy(database_uri) 
        
        broadwick.web.utils.listen(view, web_port)

def main():
    
    parser = OptionParser(usage='%prog: [options] database_uri')
    parser.add_option('--dojo', default='/static/dojo', help='URL for dojo toolkit. default: %default')
    parser.add_option('--static', help='Location to map /static to. default: %default', default=None)

    parser.add_option('--port', help='Port to expose our web interface: %default', type='int', default='16000')
    parser.add_option('--verbose', help='Be really noisy', action='store_true')
    parser.add_option('--appserver_adaptor', help='fully qualified class that implements the actions for the appserver', default="appserver.adaptors.supervisor")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Incorrect number of arguments passed')

    broadwick.utils.log.initialise_logging(log_level = logging.DEBUG if options.verbose else logging.INFO)
    app = App(args[0], options.static, options.dojo, options.appserver_adaptor,  options.port, options.verbose)
    reactor.run()



if __name__ == '__main__':
    main()

