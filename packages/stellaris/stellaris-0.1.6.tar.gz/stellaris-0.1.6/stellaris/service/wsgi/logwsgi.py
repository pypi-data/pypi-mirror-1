# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, os
log = stellaris._logger

from stellaris.service.utils import objectPath
from datetime import datetime


class LogWSGI:

    def __init__(self, app, logfile):
        if not os.path.exists(logfile):
            self.logfile = file(logfile, "w")
        else:
            self.logfile = file(logfile, "w+")
        self.app = app
        
    def __call__(self, env, response):
        # output log lines in the Common Log Format
        # note that we dont know the response size and status code here
        # http://httpd.apache.org/docs/2.0/logs.html

#        try:
#            referer = env['HTTP_REFERER']
#        except:
#            referer = '-'
        
        # Extended Common Log Format
        #        self.logfile.write('%s - - [%s] "%s %s %s" - - "%s" "%s"\n' % (env['REMOTE_ADDR'], str(datetime.now()), env['REQUEST_METHOD'], env['PATH_INFO'], env['SERVER_PROTOCOL'], env['HTTP_REFERER'], env['HTTP_USER_AGENT']))
            
#        log.info('%s %s -> %s', env['REQUEST_METHOD'], env['REMOTE_ADDR'], env['PATH_INFO'])
        # Common Log Format
        
        try:
            remote_addr = env['HTTP_X_FORWARDED_FOR']
        except:
            remote_addr = env['REMOTE_ADDR']

        self.logfile.write('%s - - [%s] "%s %s %s" - -\n' % (remote_addr, str(datetime.now()), env['REQUEST_METHOD'], objectPath(env), env['SERVER_PROTOCOL']))
        self.logfile.flush()
         
        return self.app(env, response)
