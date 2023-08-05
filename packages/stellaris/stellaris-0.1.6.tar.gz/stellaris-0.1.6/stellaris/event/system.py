# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from __future__ import with_statement
from stellaris.event.pubsub import Subscriber
from stellaris.utils import contextPath

from rdflib import Literal, URIRef
from rdflib.Graph import Graph
from datetime import datetime

import stellaris

STELLARIS = stellaris.STELLARIS
XSD = stellaris.XSD
log = stellaris._logger

class System(Subscriber):

    def __init__(self, store, lifetime, lockmanager):
        self.store = store
        self.viewname = 'system'
        self.lifetime = lifetime
        # use this before making any operations on the store
        self.lockmanager = lockmanager

    def _event_default(self, request):
        """Unhandled events."""
        log.debug('event not handled: %s', request)
    
    def _event_delete(self, request):
        #log.debug('delete event: %s', request)
        ctx = contextPath(self.viewname, request['context'])

#        with self.lockmanager.write(ctx):
        del self.store[ctx]

        del self.lifetime[request['context']]
        
    def _event_insert(self, request):
        #log.debug('insert event: %s', request)    
        self._event_replace(request)

    def _event_update(self, request):
        #log.debug('update event: %s', request)    
        self._event_replace(request)
        
    def _event_replace(self, request):
        # retrieve the system graph and just update the updatets
        
        # do not allow any updates if the replace was made on a system
        # view
        if request['view'] == self.viewname:
            return

        ttl = -1
        ctx = self.store.contextURI(contextPath(request['view'], request['context']))
        if 'ttl' in request:
            ttl = int(request['ttl'])
            self.lifetime[request['context']] = ttl
            log.debug("Added lifetime %s s for context %s." %(ttl, ctx))
            
        subj = URIRef(ctx)
        sys_ctx = contextPath(self.viewname, request['context'])                
        ts = datetime.now()
        #with self.lockmanager.write(ctx):
        try:
            g = self.store[sys_ctx]
        except:
            log.debug('replace event, context not found inserting new graph: %s', sys_ctx)
            g = self.store.makeGraph(sys_ctx)
            g.add((subj, STELLARIS["creationts"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))
            g.add((subj, STELLARIS['ttl'], Literal(ttl)))
            g.add((subj, STELLARIS["updatets"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))
            self.store[sys_ctx] = g
        else:
            g.set((subj, STELLARIS["updatets"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))
        
        #log.debug('replace event finished for context %s, request: %s', ctx, request)
        
    def notify(self, event, value):
        f = getattr(self, '_event_%s' % event, self._event_default)
        f(value)
                
