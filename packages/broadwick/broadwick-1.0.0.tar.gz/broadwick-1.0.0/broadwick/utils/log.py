import logging
import logging.handlers
import sys
import os
import time

DEFAULT_FORMAT_STRING = "%(asctime)s %(levelname)-8s: %(module)-11s (%(process)d|%(thread)x): %(message)s"

def initialise_logging(
    log_level = logging.INFO, 
    format_string = DEFAULT_FORMAT_STRING,
    logfile = None,
    nt_event_log = False,
    nt_event_appname = None,
    nt_event_log_level = None,
):
    """
    The logfile argument SHOULD NOT BE USED for anything that is to be run
    under supervisor / broadwick application server.
    It is only here because we now have windows processes that have to sort out
    their own logfiles

    On unix, the nt_event_log and nt_event_appname arguments are ignored. 
    """
    if logfile is None:
        logging.basicConfig(level=log_level, format=format_string)
    else:
        logging.basicConfig(level=log_level, format=format_string, filename=logfile)
        
    if sys.platform == 'win32' and nt_event_log:
        handler = logging.handlers.NTEventLogHandler(nt_event_appname)
        handler.setFormatter(logging.Formatter(format_string))
        handler.setLevel(nt_event_log_level if nt_event_log_level else log_level)
        
        logging.getLogger('').addHandler(handler)

def add_smtp_handler(sender,
                     throttle_period = 10 * 60,
                     throttle_max = 5,
                     level = logging.ERROR,
                     format_string = DEFAULT_FORMAT_STRING,
                     ):
    smtp_handler = LoggingSMTPHandler(sender)
    smtp_handler.setFormatter(logging.Formatter(format_string))
    smtp_handler.setLevel(level)
    smtp_handler.addFilter(MailFilter(level, throttle_period, throttle_max))
    logging.getLogger('').addHandler(smtp_handler)

class LoggingSMTPHandler(logging.Handler):
    """Emit an email using Twisted if twisted is running,
    otherwise use default smtp send"""

    def __init__(self, sender):
        logging.Handler.__init__(self)
        self.sender = sender

    def emit(self, record):
        self.sender(self.format(record))
    

class MailFilter(object):
    """Throttles mail logging so that users are not inundated with mails"""
    def __init__(self, min_level, throttle_period, throttle_max):
        self.period = throttle_period
        self.max_mails = throttle_max
        self.mail_times = []
        self.min_level = min_level
        
    def filter(self, record):
        now = time.time()
        if record.levelno >= self.min_level:
            while self.mail_times and self.mail_times[0] + self.period < now:
                del self.mail_times[0]
            
            if len(self.mail_times) < self.max_mails:
                self.mail_times.append(now)
            
                if len(self.mail_times) == self.max_mails:
                    record.msg += '''
*** %s mails have been sent in the last %s seconds.
*** Mailing of errors is now temporarily suspended''' % (self.max_mails, self.period)

                return True
        return False
    

