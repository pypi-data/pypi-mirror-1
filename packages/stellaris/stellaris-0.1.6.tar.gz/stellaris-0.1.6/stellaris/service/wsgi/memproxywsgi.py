# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urllib, sys
from urlparse import urlsplit

from cStringIO import StringIO

log = stellaris._logger

class MemProxyWSGI:
    """MemProxyWSGI is serving data direct via memory from an active file-like
       instance.
    """
    def __init__(self):
        """ """
        self.__contexts = {}
        
    def selectorMappings(self):
        return [('/memproxy/{context:any}', dict(GET=self.get))]

    def add(self, context, data):
        self.__contexts[context] = data

    def remove(self, context):
        del self.__contexts[context]
                            
    def get(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        
        context = ''
        
        if 'context' in args:
            context = args['context']
        
        try:
            result = self.__contexts[context]
        except KeyError, e:
           response("404 NOT FOUND", [('Content-Type', "text/plain")])
           return ["Context " + context + " not found\n"]
        except Exception, e:
           response("500 INTERNAL SERVER ERROR", [('Content-Type', "text/plain")])
           return [str(e)]

        response("200 OK", [('Content-Type', 'text/plain')])
        return StringIO(result)
