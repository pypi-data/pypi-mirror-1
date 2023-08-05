# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, time, os, sys

from urlparse import urljoin
from stellaris.view.view import View
from stellaris.storage import ContextNotFound, ReplacedNotFoundContext
from datetime import datetime

from rdflib import URIRef, Literal
from rdflib.Graph import Graph

STELLARIS = stellaris.STELLARIS
XSD = stellaris.XSD
log = stellaris._logger

# a view must implement:
# get - retrieving information
# insert - adding metadata
# update - changeing/updateing metadata
# delete - removeing metadata

class System:
    """The system-view is used in conjunction with the context-view to provide
       system-related metadata.
    """
    def __init__(self, view, baseuri, contextprefix='/context/', ttl=600):
        self.prefix = '/system/'
#        View.__init__(self, store, baseuri, prefix=self.prefix)
        self.ttl = ttl
        self.contextprefix = contextprefix
        self.view = view
        # the base uri is needed to construct
        # correct subject uris for the system graph
        self.baseuri = baseuri
               
#    def get(context, format='xml'):
#        return self.store.get(context, format=format)

    def _context(self, context):
        if context[0] == '/':
            context = context[1:]
        
        return os.path.join(self.prefix, context)
    
    def get(self, request):
        tmpreq = request.copy()
        tmpreq['context'] = request['context']
        tmpreq['view'] = 'system'
        log.debug('GET /system/ %s', tmpreq)
        return self.view.get(tmpreq)
            
    def insert(self, request):
        context = request['context']
            
        g = Graph()
        subj = urljoin(urljoin(self.baseuri, self.contextprefix), context)
        
        g.add((URIRef(subj), STELLARIS['ttl'], Literal(self.ttl)))
        ts = datetime.now()
        
        # dont change the original request (its a reference and used by other views)
        tmpreq = {}
        tmpreq['context'] = self._context(request['context'])
        tmpreq['view'] = request['view']
        tmpreq['input'] = g
        tmpreq['format'] = request['format']

        syscontext = self._context(context) #self.store.contextURI(self.prefix + context)
        #urljoin(urljoin(self.baseuri, self.prefix), context)

        # this has a potential race condition. If syscontext is in the
        # store when the if is run and another thread deletes the context
        # before the update is executed
        # should be:
        # try:
        #   update
        # except ContextNotFound:
        #    insert
        
        if syscontext in self.view:
            g.add((URIRef(subj), STELLARIS["updatets"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))        
            return self.view.update(tmpreq)

        g.add((URIRef(subj), STELLARIS["creationts"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))
                        
        return self.view.insert(tmpreq)

    def replace(self, request):
        try:
            return self.update(request)
        except ContextNotFound:
            return self.insert(request)
        except:
            raise
        
    def update(self, request):
        context = request['context']
        
        g = Graph()
        subj = urljoin(urljoin(self.baseuri, self.contextprefix), context)

        g.add((URIRef(subj), STELLARIS['ttl'], Literal(self.ttl)))
        ts = datetime.now()
        g.add((URIRef(subj), STELLARIS["updatets"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))

        tmpreq = {}
        tmpreq['context'] = self._context(request['context'])
        tmpreq['view'] = request['view']
        tmpreq['input'] = g
        tmpreq['format'] = request['format']
        
        return self.view.update(tmpreq)
        
    def delete(self, request):
        tmpreq = request.copy()
        tmpreq['context'] = self._context(request['context'])
        tmpreq['view'] = 'system'
        return self.view.delete(tmpreq)
