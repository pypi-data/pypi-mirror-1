# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, time

from urlparse import urljoin
from stellaris.view.view import View
from datetime import datetime

from rdflib import URIRef, Literal
from rdflib.Graph import Graph

STELLARIS = stellaris.STELLARIS
XSD = stellaris.XSD
RDF = stellaris.RDF

log = stellaris._logger

# a query view must implement:
# query - pass the query to the store

class Query:
    """The system-view is used in conjunction with the context-view to provide
       system-related metadata.
    """
    def __init__(self, store):
        self.store = store
                       
#    def get(context, format='xml'):
#        return self.store.get(context, format=format)

    def query(self, request):
        # request should contain enough to store this query for later use
        # note that internal queries should not be stored,
        # just omit the query string information
        
        if 'queryurl' in request:
            g = Graph()
            queryurl = request['queryurl']
            g.add((URIRef(queryurl), RDF['type'], URIRef(STELLARIS['Query'])))
            ts = datetime.now()
            g.add((URIRef(queryurl), STELLARIS["ts"], Literal(ts.isoformat(), datatype=XSD["dateTime"])))
            
            # this context will contain all queries that have ever been
            # asked through the information service...
            context = self.store.contextURI('/query/stored/')
            self.store.insert(g, context)

        return self.store.query(query=request['query'], format=request['format'])
