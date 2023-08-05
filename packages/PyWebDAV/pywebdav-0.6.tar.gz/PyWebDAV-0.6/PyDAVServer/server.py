#!/usr/bin/env python

"""
Python WebDAV Server.
Copyright (C) 1999-2005 Christian Scholz (cs@comlounge.net)

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Library General Public
    License as published by the Free Software Foundation; either
    version 2 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Library General Public License for more details.

    You should have received a copy of the GNU Library General Public
    License along with this library; if not, write to the Free
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

This is an example implementation of a DAVserver using the DAV package.

"""

import getopt, sys, os
import BaseHTTPServer

try:
    import DAV
except ImportError:
    print 'DAV package not found! Please install into site-packages or set PYTHONPATH!'
    sys.exit(2)

try:
    from xml.dom import ext
except ImportError:
    print 'PyXML not found! Get it from http://pyxml.sourceforge.net/'
    sys.exit(2)

from DAV.utils import VERSION, AUTHOR
__version__ = VERSION
__author__  = AUTHOR

from fileauth import DAVAuthHandler
from fshandler import FilesystemHandler
from daemonize import startstop

def runserver(
         port = 8008, host='localhost',
         directory='/tmp',
         verbose = False,
         noauth = False,
         user = '',
         password = '',
         handler = DAVAuthHandler,
         server = BaseHTTPServer.HTTPServer):

    directory = directory.strip()
    host = host.strip()
   
    if not os.path.isdir(directory):
        print >>sys.stderr, '>> ERROR: %s is not a valid directory!' % directory
        return sys.exit(233)
    
    # basic checks against wrong hosts
    if host.find('/') != -1 or host.find(':') != -1:
        print >>sys.stderr, '>> ERROR: Malformed host %s' % host
        return sys.exit(233)

    # no root directory
    if directory == '/':
        print >>sys.stderr, '>> ERROR: Root directory not allowed!'
        sys.exit(233)
        
    # dispatch directory and host to the filesystem handler
    handler.IFACE_CLASS = FilesystemHandler(directory, 'http://%s:%s/' % (host, port), verbose )

    # put some extra vars
    handler.verbose = verbose
    if noauth:
        print >>sys.stderr, '>> ATTENTION: Authentication disabled!'
        handler.DO_AUTH = False

    else:
        handler.auth_user = user
        handler.auth_pass = password
    
    print >>sys.stderr, '>> Serving data from %s' % directory
   
    # initialize server on specified port
    runner = server( (host, port), handler )
    print >>sys.stderr, '>> Listening on %s (%i)' % (host, port)

    if verbose:
        print >>sys.stderr, '>> Verbose mode ON'

    print ''

    try:
        runner.serve_forever()
    except KeyboardInterrupt:
        print >>sys.stderr, '\n>> Killed by user'

usage = """PyWebDAV server (version %s)
Standalone WebDAV server based on python

Usage: ./server.py [OPTIONS]
Parameters:
    -D, --directory Directory where to serve data from
                    The user that runs this server must have permissions
                    on that directory. NEVER run as root!
                    Default directory is /tmp

    -H, --host      Host where to listen on (default: localhost)
    -P, --port      Port to bind server to  (default: 8008)
    -u, --user      Username for authentication
    -p, --password  Password for given user
    -n, --noauth    Pass parameter if server should not ask for authentication  
    -d, --daemon    Make server act like a daemon. That means that it is going
                    to the background mode. All messages are redirected to
                    logfiles (default: /tmp/pydav.log and /tmp/pydav.err).
                    You need to pass one of the following values to this parameter
                        start   - Start daemon
                        stop    - Stop daemon
                        restart - Restart complete server
                        status  - Returns status of server
                        
    -v, --verbose   Be verbose
    -h, --help      Show this screen
    
Please send bug reports and feature requests to %s
""" % (__version__, __author__)

if __name__ == '__main__':

    verbose = False
    directory = '/tmp'
    port = 8008
    host = 'localhost'
    noauth = False
    user = ''
    password = ''
    daemonize = False
    daemonaction = 'start'
    
    # parse commandline
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'P:D:H:d:u:p:nvh', 
                ['host=', 'port=', 'directory=', 'user=', 'password=','daemon=', 'noauth', 'help', 'verbose'])     
    except getopt.GetoptError, e:
        print usage
        print '>>>> ERROR: %s' % str(e)
        sys.exit(2)
    
    for o,a in opts:
        if o in ['-D', '--directory']:
            directory = a

        if o in ['-H', '--host']:
            host = a

        if o in ['-P', '--p']:
            port = a

        if o in ['-v', '--verbose']:
            verbose = True

        if o in ['-h', '--help']:
            print usage
            sys.exit(2)
    
        if o in ['-n', '--noauth']:
            noauth = True

        if o in ['-u', '--user']:
            user = a

        if o in ['-p', '--password']:
            password = a

        if o in ['-d', '--daemon']:
            daemonize = True
            daemonaction = a

    print >>sys.stderr, 'Starting up PyWebDAV server (version %s)' % __version__
    if not noauth and daemonaction != 'status':
        if not user:
            print >>sys.stderr, '>> ERROR: Please specify an username or pass parameter --noauth'
            sys.exit(3)
  
    if daemonaction == 'status':
        print >>sys.stdout, 'Checking for status...'
   
    if type(port) == type(''):
        port = int(port.strip())
   
    if daemonize:
        startstop(stdout='/tmp/pydav.log', 
                    stderr='/tmp/pydav.err', 
                    pidfile='/tmp/pydav.pid', 
                    startmsg='>> Started PyWebDAV (PID: %s)',
                    action=daemonaction)
  
    # start now
    runserver(port, host, directory, verbose, noauth, user, password)
