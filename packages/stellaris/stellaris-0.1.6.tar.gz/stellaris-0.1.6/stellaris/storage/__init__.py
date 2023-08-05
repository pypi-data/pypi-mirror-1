# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from rdflib import plugin
from rdflib import URIRef, Literal, BNode, Namespace
from rdflib import RDF
from rdflib import sparql
from rdflib.store import Store
from rdflib.Graph import ConjunctiveGraph, Graph
from rdflib.sparql import sparqlGraph
from rdflib.sparql.bison import Parse
from rdflib.sparql.bison.Query import Query
#from rdflib.sparql.bison.SPARQLEvaluate import Evaluate
from rdflib.syntax.parsers import Parser
from urlparse import urljoin

from datetime import datetime, timedelta

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import stellaris, timeit
from stellaris import RDF, XSD, STELLARIS
from stellaris.serialize import serializeXML

import os, urllib,time

log = stellaris._logger

# The storage has system statements:
# ttl - time in seconds a context should be available
# ts  - timestamp when the context was created

class ParseError(Exception): pass

# a valid context is a URIRef
class InvalidContext(Exception): pass
class ContextNotFound(Exception): pass
class ReplacedNotFoundContext(Exception): pass

class InsertException(Exception): pass
class RemoveException(Exception): pass
class UpdateException(Exception): pass
class GetException(Exception): pass
class DeleteException(Exception): pass
class QueryException(Exception): pass

class Storage:

    def __init__(self, data_path, baseuri="http://stellaris.gac-grid.org/"):
        """
        @param data_path - path to the persistent state
        @param baseuri   - Prefix used for entries 
        """

        if not os.path.exists(data_path):
            os.mkdir(data_path)
        
        self.data_path = data_path
        self.baseuri = baseuri
               
    def close(self):
        """Closes an open store."""
            
    def baseURI(self):
        """Returns the baseuri for this store"""
        return self.baseuri
           
    def contextURI(self, context):
        """Returns the context URI which is a join of the base URI and context
           name. If context is a URI, then context is returned.
           
           @param context - name of the context.
        """
        return urljoin(self.baseuri, context)

    def delete(self, context):
        """Remove the given context from the store
           
           @param context - removes this context from the store
        """                
    
    def remove(self, graph, context):
        """Removes a set of triples represented as a graph from the context.
           
           @param graph - remove these triples from the context
           @param context - remove triples from this context
        """
    
    def replace(self, graph, context, format='xml'):
        """Deletes the graph stored at the context and then inserts the given
           graph. Returns a (bool, context)-tuple. The bool is True if
           the context was newly created.
           
           @param graph - replace the graph at context with this graph
           @param context - context to be replaced
           @param format - indicates the graph format ('xml' or 'n3')
        """
        
    def insert(self, graph, context, format='xml'):
        """Appends the graph to the graph stored at context.
        
           @param graph - add this graph to context
           @param context - add the graph to this context
           @param format - indicates the graph format ('xml' or 'n3')
        """
        
    # Updates existing statements by matching (subject, predicate)
    # of the new statements
	
	# this has to be atomic?, what happens if something crashes in the 
	# middle of an update?
    def update(self, graph, context, format='xml'):
        """Updates the context with the graph. An update means replacing 
           existing (s,p)-tuples in context with triples from the new graph.

           @param graph - update context with triples from this graph
           @param context - update this context
           @param format - indicates the graph format ('xml' or 'n3')           
           """

    def query(self, query, format="xml"):
        """Execute a `query` and returns the result as a string formatted 
           according to `format`. The query is SPARQL string. The return string
           is either in the standard SPARQL XML format or JSON.
           
           @param query - The query as a SPARQL string
           @param format - indicates the graph format ('xml' or 'json')           
        """   
			
    def get(self, context, format='xml'):
        """Retrieves the graph stored at context
        
           @param context - retrive the graph stored at this context
           @param format - 
        """
        
    def clear(self):
        """Removes all stored data. Use with caution!"""

    def close(self):
        """Closes an open store."""
 
    def __len__(self):
        """Returns the total number of stored triples."""

    def makeGraph(self, context):
        """Creates a new rdflib.Graph.Graph named by `context`. 
        
           @param context - name of the new graph
        """

    def __getitem__(self, context):
        """Retrieves the graph stored at the given context. The returned graph
           is an RDFLib Graph-instance.
           
           @param context - return graph stored at this context 
        """

    def __delitem__(self, context):
        """Removes the graph stored at the given context.
           
           @param context - return graph stored at this context 
        """

    def __setitem__(self, context, graph):
        """Assigns the graph to be stored at the given context. Replaces the 
           existing graph.
           
           @param context - insert graph at this context 
           @param graph - store this graph, must be an instance of 
                          rdflib.Graph.Graph
        """
        
    def __contains__(self, context):
        """Returns `True` if the context exists in the store.

           @param context - check if this context exists in the store.        
        """
