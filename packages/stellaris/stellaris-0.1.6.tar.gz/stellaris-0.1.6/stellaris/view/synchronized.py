# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from __future__ import with_statement

import stellaris, urlparse, time, threading, sys

from rdflib.Graph import Graph
from rdflib.sparql.bison import Parse

from stellaris.lockmanager import LockHandler
from stellaris.view.view import View
from stellaris.scheduler import Scheduler, TaskFactory
from stellaris.storage import ContextNotFound
from stellaris.utils import contextPath

log = stellaris._logger

# a view must implement:
# get - retrieving information
# insert - adding metadata
# update - changeing/updateing metadata
# delete - removeing metadata

class MethodNotAllowed(Exception): pass
            
class Synchronized:
    """The Synchronized-view is supporting Creation, Retrival, Update, Delete 
       and Query on another view. Implements a variant of single-writer/many 
       readers that does not block reads to a single context. If a writer 
       executes concurrently, the previously commited graph is returned. 
       Queries over all contexts blocks any concurrent writer to the database.
    """
    # pass the scheduler, to make someone else responsible for stopping it
    def __init__(self, view, lockmanager):
        self.view = view
#        self.store = store
        self.cache = {}
        self.lockhandler = lockmanager

    def _prepareCache(self, request, context):
        self.cache[context] = {}
        fakereq = {}
        fakereq['context'] = request['context']
        fakereq['view'] = request['view']
        fakereq['format'] = 'system'

        g = None
        
        try:
            g = self.view.get(fakereq)
        except ContextNotFound:
            self.cache[context]['n3'] = None
            self.cache[context]['xml'] = None
        
        if g != None:
            self.cache[context]['n3'] = g.serialize(format='n3')
            self.cache[context]['xml'] = g.serialize(format='xml')

    def _read(self, request, func):
        """Handles a read request and calls the appropriate
           method in the wrapped view.
        """
        #context = self._context(request)
        context = contextPath(request['view'], request['context'])
        log.debug('read of context %s, %s', context, func)
        
        with self.lockhandler.read(context) as read:
            if read == True:
                # the cache stores serialized copies of
                # the graph.
                # no reads can occur when the cache is prepared since then
                # the read will fail...
                log.debug('concurrent write/read of context %s', context)
                with self.lockhandler.cacheread(context):
                    return self.cache[context][request['format']]
            else:
                try:

                    return func(request)
                except:
                    raise

    def _write(self, request, func):
        """Handles a write request and calls the appropriate
           method in the wrapped view.
        """    
        #context = self._context(request)
        log.debug("serialized write of %s", request['context'])        
        context = contextPath(request['view'], request['context'])
        

        with self.lockhandler.write(context):
            # prepare cached versions of the graph
            # both xml and n3 
            with self.lockhandler.cachewrite(context):
                self._prepareCache(request, context)
                
            try:
                return func(request)
            except:
                log.debug('write to %s failed: %s', context, sys.exc_info())
                raise 

    def _query(self, request, func):
        """Handles a query request and calls the appropriate
           method in the wrapped view.
        """    
        # dont lock queries since this will have very bad performance impacts
        #with self.lockhandler.queryall():
        return func(request)
                                        
    # this is a dynamic way to make execution of any
    # method in the underlying view possible
    # If the name is get make a read, if it is a query call the query method,
    # otherwise make a write
    def __getattr__(self, name):
        try:
            func = getattr(self.view, name)
        except AttributeError:
            raise MethodNotAllowed('Method %s is not allowed', name)

        log.debug('synch dispatcher: %s', name)
        if name == 'get':
            return lambda req: self._read(req, func)
        elif name == 'query':
            return lambda req: self._query(req, func)
        elif name in ['insert', 'remove', 'replace', 'delete', 'update']:
            return lambda req: self._write(req, func)
        else:
            return func
