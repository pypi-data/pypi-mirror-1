# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris
log = stellaris._logger

class SecurityWSGI:

    def __init__(self, app, security, host=None, port=None):
        self.app = app
        self.security = security
        self.host = host
        self.port = port
        
    def __call__(self, env, response):
        if env['REQUEST_METHOD'] == 'GET':
            return self.app(env, response)
        
        #print env
        if not self.host:
            host = env['HTTP_HOST'].split(':')[0]

        port = self.port
        
        client_dn = 'HTTP_SSL_CLIENT_S_DN'
        
        try:
            env[client_dn]
        except KeyError:
            client_dn = 'SSL_CLIENT_S_DN'
            
        
        if not client_dn in env:
            response('401 UNAUTHORIZED', [('Location', 'https://' + host + ':' + str(port))])
            return ['%s is only allowed via HTTPS\r\n' %(env['REQUEST_METHOD'])]
        
        if client_dn in env and self.security.isAuthorized(env[client_dn]):
            return self.app(env, response)
        
        log.debug('User %s was not allowed to %s', env[client_dn], env['REQUEST_METHOD'])
        # user is not allowed to access the service using this certificate
        response('401 UNAUTHORIZED', [])
        return ['User %s is not authorized to access the service.\r\n' %(env[client_dn])]
            
