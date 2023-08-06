"""
supervisorctl exists, but is a pain because you have to give it the path to the config file.
Broadwick supervisor doesn't use the config file but uses twiddler instead. 
"""
from optparse import OptionParser 

import xmlrpclib

def main():
    parser = OptionParser(usage='%prog: url command processname')
    options, args = parser.parse_args()
    if len(args) != 3:
        parser.error("I need at least 3 arguments: server xmlrpc URL, command, process name (including process group)")

    url, command, processname = args
    proxy = xmlrpclib.ServerProxy(url)
    cmd = getattr(proxy, "supervisor.%s" % command)
    cmd(processname)

if __name__ == '__main__':
    main()
