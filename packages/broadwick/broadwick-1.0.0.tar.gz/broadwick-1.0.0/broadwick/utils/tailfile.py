# This has been adapted from a number of places
# One version was found on http://0xfe.blogspot.com/2006/03/following-log-file-with-twisted.html
# "Twisted FollowTail by Mohit Muthanna"
# but that only worked on Windows- the file reset mechanism in the above doesn't work on Unix,
# it never detected it
# That in turn was taken from:
#
# A Twisted version of POE::Wheel::FollowTail. Adapted from
# a post by Kragen Sitaker on the Kragen-hacks mailing list.
#
# http://lists.canonical.org/pipermail/kragen-hacks/2005-June/000413.html
# I don't know if this works in Windows. I haven't tested it. 

import broadwick.utils.log as log

from optparse import OptionParser
import logging


from twisted.internet import reactor
from twisted.protocols import basic
import os, stat

class FollowTail(object):
    """
    """

    from os import linesep as newline
    __line_buffer = ""

    def __init__( self, filename = None, seekend = True, delay = 1 ):
        self.filename = filename
        self.delay = delay
        if seekend:
            try:
                self.last_pos = os.stat(self.filename).st_size
            except OSError:
                logging.info ("Can't open %s" % self.filename)
                self.last_pos = 0
        else:
            self.last_pos = 0

        self.keeprunning = False


    def fileIdentity( self, struct_stat ):
        retval = (struct_stat[stat.ST_DEV], struct_stat[stat.ST_INO])
        return retval 

    def start( self ):
        self.keeprunning = True
        self.followTail()

    def stop( self ):
        self.keeprunning = False

    def followTail(self):
        """
        In Unix, there is no way to find the file creation time.
        Thus the only way to check if the file has reset is to see
        if its size now is less than the last time. 

        This will check for new lines every second, and all new lines will be fetched since then.
        However, if the process dies and keeps running on the same files, it won't
        get old lines. 
        """
        fileobj = None
        try:
            fileobj = open(self.filename)
            cur_size = os.stat(self.filename).st_size
            if cur_size < self.last_pos:
                logging.info ("%s was reset. cur_size %s last_pos %s" % (self.filename, cur_size, self.last_pos))
                fileobj.seek(0, os.SEEK_END)
                self.last_pos = fileobj.tell()
                self.fileReset(fileobj)
            else:
                fileobj.seek(self.last_pos, os.SEEK_SET)
            data = fileobj.read(104857600) # Don't read too much at once - don't want to blow our memory usage

            if data: 
                self.last_pos = fileobj.tell()
                self.dataReceived(data)

        except:
            logging.exception("Died trying to read %s. Retrying" % self.filename)

        if fileobj is not None:
            fileobj.close()

        if self.keeprunning: 
            reactor.callLater(self.delay, self.followTail)
  

    def dataReceived( self, data ):
        # Fill buffer
        logging.info ("received %s bytes from %s" % (len(data), os.path.basename(self.filename)))
        self.__line_buffer += data
    
        # Split lines
        lines = self.__line_buffer.splitlines()
    
        if not data.endswith( self.newline ):
            # we only care about the last part-line
            self.__line_buffer = lines.pop()
        else:
            del self.__line_buffer
            self.__line_buffer = ""
    
        for line in lines:
            self.lineReceived( line )

  
    def fileReset( self , fileobj):
        pass

    def lineReceived(self, line):
        """
        override this
        """
        pass
  

if __name__ == '__main__':
    from broadwick.utils import mail as bwmail
    victims = ["petra.chong@glcuk.com"]

    class Test(FollowTail):
        def lineReceived( self, line ):
            logging.info ("I just got: %s" % line)
            # check for ERROR
            errorIndex = line.find("ERROR")
            if errorIndex > -1:
                logging.info ("ARGH: %s" % line)
                bwmail.sendmail(to=victims,
                                subject="error in %s" % self.filename,
                                message=line,
                                mail_server="ldnexc01.glc.com",
                                email_from="petra.chong@glcuk.com")

    import re
    DF_RE = "^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d"

    START_RE = re.compile(r"%s (?=ERROR|FATAL)" % DF_RE)
    #TB_RE = re.compile(r"Traceback \(most recent call last\)")
    DEF_RE = re.compile(r"Unhandled error in Deferred")

    END_RE = re.compile(r'%s ' % DF_RE)

    class ErrorTailer(FollowTail):
        def __init__(self, *args, **kwargs):
            FollowTail.__init__(self, *args, **kwargs)
            self.state = "IDLE" 
            self.stack_trace = []

        def lineReceived( self, line ):
            #logging.info ("Got line: %s" % line)
            if self.state == "IDLE":
                if START_RE.match(line) or DEF_RE.match(line): #or TB_RE.match(line):
                    self.state = "FOUND_ERROR"
                    self.stack_trace.append(line)
            elif self.state == "FOUND_ERROR":
                if END_RE.match(line):
                    self._reset()
                else:
                    self.stack_trace.append(line)

        def _reset(self):
            bwmail.sendmail(to=victims,
                            subject="error in %s" % self.filename,
                            message="\n".join(self.stack_trace),
                            mail_server="ldnexc01.glc.com",
                            email_from="petra.chong@glcuk.com")

            self.state = "IDLE"
            self.stack_trace = []
                    
    def main():
        log.initialise_logging()
        parser = OptionParser(usage='%prog: [options] filename')
        parser.add_option('--no-seekend', action='store_false', default='False')
        options, args = parser.parse_args()
        if len (args) != 1:
            parser.error ("I need one argument which is the full path to the filename")
        
        # ft = Test(args[0], seekend=options.no_seekend)
        ft = ErrorTailer(args[0], seekend=options.no_seekend)
        ft.start()
        reactor.run()

    main()
