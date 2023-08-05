# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urllib, sys, base64, hashlib, os

from stellaris.storage import ContextNotFound, ReplacedNotFoundContext
from stellaris.view import View, Context, System, Introspection, Synchronized, Event
from stellaris.service.utils import parseQueryString

from stellaris.event.system import System as SystemSubscriber
from stellaris.event.introspection import Introspection as IntrospectionSubscriber

from stellaris.service.wsgi import QueryWSGI
from stellaris.service.wsgi.introspectionwsgi import IntrospectionWSGI
from stellaris.lockmanager import LockHandler

#from stellaris.service.hayai import Client as HayaiClient

log = stellaris._logger

class StellarisWSGI:
    """Stellaris is a compound view used directly by the implementing
       service interface. It is a WSGI app.
    """
    def __init__(self, store, tmpl, lifetime, atomic=True):
        """
        The given backend store will be used for context storage.
        
        @param store - An instance of a store
        @param tmpl - An instance of the kid template engine
        @param lifetime - An instance of a lifetime object
        @param atomic - True if changes of contexts should be atomic. When using
                        other stores such as virtuoso this is taken care of
                        internally in that store.
        """
        self.store = store
        self.tmpl = tmpl
        
        lockmngr = LockHandler()       
        baseview = View(store)
        eventview = Event(baseview)
        
        if atomic:
            synched = Synchronized(eventview, lockmngr)
        else:
            synched = eventview

        ctx = Context(synched)
        
        def lifetime_delete(context):
            log.debug('lifetime delete %s' % context)
            request = {}
            request['context'] = context
            request['view'] = 'context'
            synched.delete(request)
            
        lifetime.change_callback(lifetime_delete)
        systemsub = SystemSubscriber(self.store, lifetime, lockmngr)
        introspectionsub = IntrospectionSubscriber(self.store, lockmngr, '/context')        

        eventview.subscribe(systemsub)
        eventview.subscribe(introspectionsub)
                       
        self.view = synched

        
        # this contains a list with additional apps used by Stellaris
        self.apps = [QueryWSGI(synched, self.tmpl), IntrospectionWSGI(self.view, self.tmpl)]

#        self.hayai = HayaiClient()
        
        # helps with the HTTP caching of graphs
        # key: <context> value: <etag> 
        # GET <context> generates a new cache entry if it doesnt exist
        # In addition, an etag is generated and the cache header is
        # returned. To avoid inconsistencies, the client or intermediary
        # caches must check validity with the server for each request.
        # PUT/POST/DELETE to <context> removes the cache entry
        self.__cache = {}
                
    def selectorMappings(self):
        tmpmap = [('/context/{context:any}', dict(GET=self.get, POST=self.update, DELETE=self.delete, PUT=self.insert)), ('/system/{context:any}', dict(GET=self.get, POST=self.update))]
        for app in self.apps:
            tmpmap += app.selectorMappings()
        return tmpmap

    def _file_input(self, env):
        # 16k
        chunk_size = 2**14
        input_arr = []
        
        size = int(env['CONTENT_LENGTH'])
        file_obj = env['wsgi.input']
        
        if size != -1 and size < chunk_size:
            chunk_size = size
        
        try:
            read_bytes = 0

            while read_bytes < size or size == -1:
                data = file_obj.read(chunk_size)
                if data:
                    read_bytes += len(data)
                    input_arr.append(data)
                else:
                    raise StopIteration   
                
                if chunk_size + read_bytes > size:
                    chunk_size = size - read_bytes
                                  
        except StopIteration, e:
            pass
        
        return ''.join(input_arr) # env['wsgi.input'].read(int(env['CONTENT_LENGTH']))
            
    def _parseView(self, path):
        return path[1:path[1:].find("/")+1]
            
    def get(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        
        context = '/'
        
        if 'context' in args:
            context = args['context']
            
        view = self._parseView(env['SCRIPT_NAME'] or env['PATH_INFO'])
        
        log.debug('GET context %s/%s', view, context)

        queryargs = parseQueryString(env['QUERY_STRING'])
        format = 'xml'
        if 'format' in queryargs:
            format = queryargs['format']
    
        valid_formats = ['xml', 'n3']

        if not format in valid_formats:
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Format " + format + " is not available. Valid formats: " + str(valid_formats)]
        
        # prepare the request object
        request = {}
        request['context'] = context
        request['format'] = format
        request['view'] = view

        # if there is a match in the cache, return a 304 Not Modified
        # allowing the client to use its own cache
        # None doesnt match empty string
        if env.get('HTTP_IF_NONE_MATCH', None) == self.__cache.get(context, ''):
            response('304 NOT MODIFIED', [])
            return []
        
        try:
            result = self.view.get(request)
        except ContextNotFound, e:
            # check with Hayai if the context is registered anywhere else,
            # in that case, redirect the client, otherwise return that it
            # was not found.
            response("404 NOT FOUND", [('Content-Type', "text/plain")])
            return ["Context " + request['context'] + " not found\n"]
        except Exception, e:
            response("500 INTERNAL SERVER ERROR", [('Content-Type', "text/plain")])
            return [str(e) + ' ' + str(sys.exc_info())]

        if result != None:            
            headers = [('Content-Type', 'application/rdf+' + format)]
            
            # add the cache related headers
            etag = base64.encodestring(hashlib.md5(result).digest())[:-1]
            self.__cache[context] = etag
            headers.append(('ETag', etag))
            
            # make sure that the client has to check if the context has
            # changed for each request
            headers.append(('Cache-Control', 'must-revalidate, max-age=0'))
            
            headers.append(('Content-Length', str(len(result))))
            response("200 OK", headers)            
            return [result]
           
        response("404 NOT FOUND", [('Content-Type', 'text/plain')])
        return ["Context " + request['context'] + " not found\n"]

    # an insert (PUT) deletes the given context and then inserts the new 
    # graph.
    def insert(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        context = args['context']
        view = self._parseView(env['SCRIPT_NAME'] or env['PATH_INFO'])

#        log.debug("Env: %s", env)        

        queryargs = parseQueryString(env['QUERY_STRING'])
        format = 'xml'
        if 'format' in queryargs:
            format = queryargs['format']

        if 'ttl' in queryargs:
            try:
                ttl = int(queryargs['ttl'])
            except ValueError, e:
                response("400 BAD REQUEST", [('Content-Type', "text/plain")])
                return ["ttl argument is not a valid integer in base 10.\n"]
        else:
            ttl = None
            
        valid_formats = ['xml', 'n3']

        if not format in valid_formats:
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Format " + format + " is not available. Valid formats: " + str(valid_formats)]

        if context.endswith('/'):
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Uploading RDF-data to a collection is not allowed."]

        request = {}
        request['context'] = context
        request['format'] = format
        request['view'] = view
        if ttl != None:
            request['ttl'] = ttl
        request['input'] = self._file_input(env)
        
        statuscode = "201 CREATED"

        try:
            log.debug("PUT context: " + self.store.contextURI(view + '/' + context))
            
            # request should contain the ttl, if no ttl this means that a default
            # of -1 (persistent) should be used.
            # If this is a replace of an existing context, check if the context
            # has a TTL already and use that.
            
            (stat, ctx) = self.view.replace(request)
            
            # comply with rfc2616 and send a 200 OK when the resource already
            # existed
            if stat == False:
                statuscode = "200 OK"

        except ReplacedNotFoundContext, e:
            # this exception still means that the change was fine
            statuscode = '201 CREATED'
        except Exception, e:
            response("500 INTERNAL SERVER ERROR", [('Content-Type', "text/plain")])
            return [str(sys.exc_info()) + "\n"]
        
        # clean the cache for this context
        if context in self.__cache:
            del self.__cache[context]
            
        response(statuscode, [])         
        return []

    # a POST makes an update if add and update if update in the action query
    # string. POST does not perform the operation if the context does not
    # exist.    
    def update(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        context = args['context']
        view = self._parseView(env['SCRIPT_NAME'] or env['PATH_INFO'])

        # this should not be here, just check for exceptions...
        if not self.store.contextURI(view + '/' + context) in self.store:
            response("404 NOT FOUND", [('Content-Type', 'text/plain')])
            return ["Context " + context + " not found. Modifications are only accepted on existing contexts.\n"]
            
        queryargs = parseQueryString(env['QUERY_STRING'])
        
        format = 'xml'
        if 'format' in queryargs:
            format = queryargs['format']

        if 'ttl' in queryargs:
            try:
                ttl = int(queryargs['ttl'])
            except ValueError, e:
                response("400 BAD REQUEST", [('Content-Type', "text/plain")])
                return ["ttl argument is not a valid integer in base 10.\n"]
        else:
            ttl = None
                            
        valid_formats = ['xml', 'n3']

        if not format in valid_formats:
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Format " + format + " is not available. Valid formats: " + str(valid_formats)]

        # default is to add data using a storage insert
        action = 'add'
        if 'action' in queryargs:
            action = queryargs['action']
        
        valid_actions = ['add', 'update', 'remove']
        if not action in valid_actions:
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Invalid action " + action + ". Valid actions: " + str(valid_actions)]
        
        request = {}
        request['context'] = context
        request['format'] = format
        request['view'] = view
        if ttl != None:
            request['ttl'] = ttl
        
        request['input'] = self._file_input(env)

        log.debug("update context " + context)
        
        try:
            # add == insert
            if action == 'add':
                res = self.view.insert(request)
            elif action == 'update':
                res = self.view.update(request)
            elif action == 'remove':
                res = self.view.remove(request)
        except Exception, e:
            response("500 INTERNAL SERVER ERROR", [('Content-Type', "text/plain")])
            #log.debug("eror: " + str(e))
            return [str(e) + "\n"]

        # clean the cache for this context
        if context in self.__cache:
            del self.__cache[context]
            
        response("200 OK", [])         
        return []
                        
    def delete(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        context = args['context']
        view = self._parseView(env['SCRIPT_NAME'] or env['PATH_INFO'])

        request = {}
        request['context'] = context
        request['view'] = view
        
        log.debug("delete context " + view + '/' + context)
        
        try:
            res = self.view.delete(request)
        except Exception, e:
            response("500 INTERNAL SERVER ERROR", [('Content-Type', "text/plain")])
            #log.debug("eror: " + str(e))
            return [str(e) + "\n"]

        # clean the cache for this context
        if context in self.__cache:
            del self.__cache[context]
            
        response("204 NO CONTENT", [])         
        return []
