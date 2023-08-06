import logging
from broadwick.utils import log, mail, uriparse

def quickstart(view, port=8080, log_level=logging.INFO, *args, **kwargs):
    import broadwick.utils.log
    broadwick.utils.log.initialise_logging(log_level)

    import broadwick.web.utils
    broadwick.web.utils.listen(view, port, *args, **kwargs)

    from twisted.internet import reactor
    reactor.run()
