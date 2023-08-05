# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urlparse, os
from stellaris.utils import contextPath

log = stellaris._logger

# a view must implement:
# get - retrieving information
# insert - adding metadata
# update - changeing/updateing metadata
# delete - removeing metadata

class View:
    """The View-view is supporting Creation, Retrival, Update and Delete
       based on a prefix.
    """
    def __init__(self, store):
        self.store = store

    def _storecontext(self, context):
        if len(context) > 0 and context[0] == '/':
            context = context[1:]
#            return self.store.contextURI(self.prefix)
            
#        return self.store.contextURI(os.path.join(self.prefix, context))
        return self.store.contextURI(context)
        
        
    # a request object is a dictionary with:
    # - context
    # - view
    # - user
    # - query (this is mostly empty, why pass it around?)
    # - format
    # - input (file-like object, or an rdflib.Graph.Graph)
    
    def get(self, request):
        #print "view get: ", self._storecontext(request['context'])
        log.debug('GET %s', str(request))
        #return self.store.get(self._storecontext(request['context']), format=request['format'])
        return self.store.get(contextPath(request['view'], request['context']), format=request['format'])
        
    def insert(self, request):
        # check if this graph should replace any existing graph stored at the context
        ctx = self._storecontext(request['context'])

#        if ctx in self.store:
#            return self.store.replace(request['input'], ctx), format=request['format'])
        
#        log.debug('Insert: %s', str(request))    
        return self.store.insert(request['input'], contextPath(request['view'], request['context']), format=request['format'])

    def replace(self, request):
        return self.store.replace(request['input'], contextPath(request['view'], request['context']), format=request['format'])

    def remove(self, request):
        return self.store.remove(request['input'], contextPath(request['view'], request['context']))
        
    def update(self, request):
        return self.store.update(request['input'], contextPath(request['view'], request['context']), format=request['format'])

    def delete(self, request):
        log.debug('DELETE %s', str(request['context']))
        return self.store.delete(contextPath(request['view'], request['context']))


    def __contains__(self, key):
        return key in self.store
        
    # the rollback mechanism only supports one operation
    # this operation is rollbacked by maintaining an in-memory graph
    # of the previous state and reverting to this state on failure. 
    # This has one significant drawback, since if the storage is stopped 
    # uncleanly, the changes have been committed already and the state is 
    # inconsistent.
    # TODO: implement/come up with a better solution
    
    def rollback(self):
        """Rollbacks one previous operation."""
        pass

    def commit(self):
        """Commits the current operation to the database."""
        pass
                        
    def query(self, request):
        res = self.store.query(request['query'], format=request['format'])
        #log.debug('view query results: %s', res)
        return res

