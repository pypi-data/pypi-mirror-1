"""
This is provided as a utility, it's up to you to schedule it yourself using cron or equivalent. 

This will look for things called *.log.*  and zip up anything that has 
st_mtime older than days_to_leave_unzipped. You can define a different log file regexp
if you like

This will create a new zip file for every month. It will not create a new log file for every 
different file name- so if you have TDS.log.20081013 and TalonGUI.log.20081013 these will both go into
logs.zip.200810

Also, note that on Unix this uses ST_MTIME which sometimes uses the creation time of the file.
Thus if your file starts off named TDS.log on 20080929 and is renamed on 20081003 to TDS.log.20081003, 
the latter file will be included in here. 

It's up to you to decide what to do with old zipfiles. 

"""

import zipfile
import datetime
import os
import sys
import logging
import subprocess
import shutil
from broadwick.utils import log
import re
import stat
import pprint
from optparse import OptionParser

class FileZipper(object):
    def __init__(self, src_dir, target_dir, days_to_leave_unzipped=7, logfile_re = r'.*\.log.*', testing=None):
        self.src_dir = src_dir
        self.target_dir = target_dir
        self.days_to_leave_unzipped = days_to_leave_unzipped
        self.regexp = re.compile(logfile_re)
        self.testing = testing is not None

    def do_zip(self):
        threshold = datetime.date.today() - datetime.timedelta(self.days_to_leave_unzipped)
        logging.info ("Ignoring files newer than %s" % threshold)
        # I don't like glob, so we are not using glob. 
        to_include = []
        done = []
        for filename in os.listdir(self.src_dir):
            month_file = None       
            if self.regexp.match(filename):
                fullpath = os.path.join(self.src_dir, filename)
                thestat = os.stat(fullpath)
                mtime = datetime.datetime.fromtimestamp(thestat[stat.ST_CTIME])
                if mtime.date() < threshold:
                    if thestat[stat.ST_SIZE] == 0:
                        logging.info ("Ignoring zero-length file %s" % fullpath)
                        # got to mark it as done so it will be deleted
                        done.append(fullpath)
                        continue
                    month_file = "logs.%s.zip" % mtime.date().strftime("%Y%m")
                    month_file = os.path.join(self.target_dir, month_file)
                    to_include.append((filename, month_file))
                else:
                    logging.info ("Ignoring %s, it is too new: %s" % (fullpath, mtime))
            else:
                logging.info ("Ignoring %s, it doesn't match the pattern" % fullpath)
        logging.info ("I would archive the following: \n%s" % pprint.pformat(to_include))
        # I don't care if we have to iterate twice
        distinct = {}
        for filename, zfname in to_include:
            fullpath = os.path.join(self.src_dir, filename)
            logging.info ("%s -> %s (%s)" % (fullpath, zfname, filename))
            if self.testing is False:
                if os.path.exists(zfname):
                    f = zipfile.ZipFile(zfname, 'a', zipfile.ZIP_DEFLATED)
                else:
                    f = zipfile.ZipFile(zfname, 'w', zipfile.ZIP_DEFLATED)
            
                f.write(fullpath, filename)
                distinct[zfname] = zfname
                f.close()
            done.append(fullpath)
        if done != []:
            for filename in done:
                if self.testing is True:
                    logging.info ("Would remove %s" % filename)
                else:
                    logging.info ("Removing %s" % filename)
                    os.unlink(filename)
                
def main():
    log.initialise_logging()
    parser = OptionParser(usage='%prog: [options]')
    parser.add_option('--src_dir', help='Source directory')
    parser.add_option('--target_dir', help='Destination directory')
    parser.add_option('--days_to_leave_unzipped', default=7, help='Number of days files to not zip')
    parser.add_option('--logfile_regexp', default='.*\.log', help='Python regular expression that says what logfiles to match')
    parser.add_option('--testing', action="store_true", help="Print out everything but don't do anything")
    options, args = parser.parse_args()
    fz = FileZipper(src_dir = options.src_dir,
                    target_dir = options.target_dir,
                    days_to_leave_unzipped = int(options.days_to_leave_unzipped),
                    logfile_re = r'%s' % options.logfile_regexp,
                    testing = options.testing)

    fz.do_zip()

if __name__ == '__main__':
    main()
