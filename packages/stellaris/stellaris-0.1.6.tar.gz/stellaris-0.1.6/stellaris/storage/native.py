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
from stellaris.storage import Storage, ParseError, InvalidContext, ContextNotFound, ReplacedNotFoundContext, InsertException, UpdateException, GetException, DeleteException, QueryException

import os, urllib, time, sys

log = stellaris._logger

class RDFLibStorage(Storage):

    def __init__(self, datapath, memory=False, baseuri="http://stellaris.gac-grid.org/"):
#		self.store = sparqlGraph.SPARQLGraph(Graph(backend='default'))
        self.datapath = datapath
        
        Storage.__init__(self, datapath, baseuri)
        
        if memory == True:
            self.store = plugin.get('IOMemory',Store)(identifier=self.baseuri)
        else:                
            self.store = plugin.get('Sleepycat',Store)(configuration=datapath, identifier=self.baseuri)
            
#            config = 'user=rdflib,password=rdflibdev,host=localhost,port=3306,db=rdflib'
#            self.store = plugin.get('MySQL', Store)(configuration=config, identifier=self.baseuri)
            self.store.open(datapath, create=False)

        # contexts make a mapping between context name and a graph instance
        # this is used to lookup graphs for serialization and querying
        self.contexts = {}
        
        # this schema should be general: http://www.gac-grid.org/schema/stellaris#
        #stellaris_schema = urllib.basejoin(self.baseuri, "/schema/")
        
        self.store.bind("stellaris", STELLARIS)

        self.graph = ConjunctiveGraph(self.store)

        log.debug("Initializing store with size %s", len(self.store))
        
        # initialize contexts        
        def add_graph(g):
            # remove "#context" since it is not part of the stellaris id
            self.contexts[g.identifier.replace("#context","")] = g
        
        map(add_graph, self.graph.contexts())
       
    def close(self):
        self.store.close()
#        self.gc.stop()
    
    def _parseData(self, input_data, context=None, format='xml', graph=None):
        parseCtx = None
        
        if graph == None:
            graph = self.graph
            
        if isinstance(input_data, str) or isinstance(input_data, unicode):
            try:
                parseCtx = graph.parse(StringIO(input_data), publicID=context, format=format)
            except Exception, e:
                raise ParseError(sys.exc_info())
        else:
            try:
                parseCtx = graph.parse(input_data, publicID=context, format=format)
            except Exception, e:
                raise ParseError(sys.exc_info())
    
        return parseCtx

    def delete(self, context):
        """Remove the given context from the store
           context - a context
        """                
        context = self.contextURI(context)
        
        try:
            URIRef(context)
        except:
            raise InvalidContext(context + " is not a valid URI")

        if context in self.contexts:
            log.debug("deleting context %s", context)
            self.store.remove((None, None, None), context=self.contexts[context])
            del self.contexts[context]
        else:
            raise ContextNotFound('Context %s not found', context)
            
        # True indicates successful operation
        return (True, context)
    
    def remove(self, graph, context):
        context = self.contextURI(context)
        log.debug('removing from: %s', context)
        if context in self.contexts:
            self.contexts[context] -= graph
#            for (s,p,o) in graph:
#                self.store.remove((s,p,o), context=self.contexts[context])
    
    def replace(self, graph, context, format='xml'):
        """Deletes the graph stored at the context and then inserts the given
           graph. Returns a (bool, context)-tuple. The bool is True if
           the context was newly created.
        """
        context = self.contextURI(context)        
        try:
            self.delete(context)
            self.insert(graph, context, format=format)
            return (False, context)
        except ContextNotFound, e:
            #sys.exc_clear()
            try:
                log.debug('Context %s not found, replacing graph', context)
                self.insert(graph, context, format=format)        
            except:
                raise
            
            return (True, context)
            #raise ReplacedNotFoundContext(e)
        except Exception, e:
            log.debug('Got other exception in replace: %s', str(sys.exc_info()))        
            raise e
        
#        return (True, context)
        
    def insert(self, graph, context, format='xml'):
        """Adds the graph to the context."""

        log.debug("insert graph into context: " + context)
        
        context = self.contextURI(context)
        try:
            URIRef(context)
        except:
            raise InvalidContext(context + " is not a valid URI")
     
        # a context is added with the extra '#context'-string 
        # when publicID is specified in parse
        
        # parse the graph using the given format
        dt = time.clock()
        if not isinstance(graph, Graph):            
            if not context in self.contexts:
                graph = self._parseData(graph, context, format)
                self.contexts[context] = graph
            else:
                # add data to the context
                self._parseData(graph, context, format, graph=self.contexts[context])
        else:
            if not context in self.contexts:
                self.contexts[context] = Graph(self.store, identifier=URIRef(context))

            self.contexts[context] += graph
        # calculating the storage size takes time for each request.
#        log.debug("add to context %s, storage size: %s", context, len(self.store))

        log.debug("add to context %s finished after %s seconds", context, str(time.clock()-dt))
        return (True, context)

    # Updates existing statements by matching (subject, predicate)
    # of the new statements
	
	# this has to be atomic?, what happens if something crashes in the 
	# middle of an update?
    def update(self, graph, context, format='xml'):
        """Updates the context with the graph. An update means replacing 
           existing (s,p)-tuples from the new graph."""
        context = self.contextURI(context)
        
        try:
            URIRef(context)
        except:
            raise InvalidContext(context + " is not a valid URI")
        log.debug("update graph in context: " + context)
        
        if not isinstance(graph, Graph):        
            tmp_graph = ConjunctiveGraph(plugin.get('IOMemory', Store)())
            parseCtx = self._parseData(graph, context, format, graph=tmp_graph)
            graph = tmp_graph

        # use the graph.set(self, (s,p,o)) method (convenience method for
        # updates)
        
        try:
            g = self.contexts[context]	
        except KeyError,e:
            log.debug('Could not find context %s', context)
            raise ContextNotFound('Could not find context %s', context)
        except:
            raise

        lists = {}
        for (s,p,o) in graph:
            if (s,p) not in lists:
                lists[(s,p)] = []
            
            lists[(s,p)].append((s,p,o))
                                    
        # if there is a list of triples
        # replace the current list by setting
        # graph.set() replaces triples with (s,p)
        # then add the rest of the list to the graph
        for sppair in lists:
            toptriple = lists[sppair].pop()
            
            g.set(toptriple)
            
            for t in lists[sppair]:
                g.add(t)
                
        return (True, context)
                        
    # fine-grained locking on queries is not possible yet since we don't know
    # which context will be used...    
    def query(self, query, format="xml"):
        try:
            # assume that if the query is neither of str or unicode
            if isinstance(query, unicode) or isinstance(query, str):
                query = Parse(query)
            elif not isinstance(query, Query):
                raise SyntaxError("query is not a valid query object")
            dt = time.time()
            results = self.graph.query(query)
            log.debug("query execution took %s seconds" % (str(time.time()-dt)))
        except SyntaxError, e:
            raise e
        
        #log.debug('query results: %s', results.serialize(format='python'))
        if format == 'xml':
            return serializeXML(results)
        
        return results.serialize(format=format)
			
    def get(self, context, format='xml'):
        #log.debug("get " + context + str(self.contexts))
        context = self.contextURI(context)
        try:
            URIRef(context)
        except:
            raise InvalidContext(context + " is not a valid URI")

        if context in self.contexts:
            # this is a special format to get the internal graph
            if format == 'system':
                return self.contexts[context]
            
            # otherwise just return the serialized version    
            return self.contexts[context].serialize(format=format)

        # Could not find the graph
        raise ContextNotFound("Context not found.")
#       return (False, "Context not found.")
        
    def clear(self):
        """This removes the directory where the data is stored. Warning, use 
           will clean all persistent data"""
        self.store.close()
        
        if self.datapath != None and os.access(self.datapath, os.F_OK) == 1:
            for f in os.listdir(self.datapath):
                os.remove(self.datapath + os.sep + f)
            os.rmdir(self.datapath)

    def close(self):
        self.store.close()
 
    def __len__(self):
        # should this return number of contexts or the size of the
        # internal store?
        return len(self.store)

    def makeGraph(self, context):
        return Graph(self.store, self.contextURI(context))
                
    def __getitem__(self, key):
        """Retrieves the graph stored at the given key."""
        #log.debug('__getitem__ key: %s, store key: %s', key, self.contextURI(key))
        return self.contexts[self.contextURI(key)]

    def __delitem__(self, key):
        """Removes the graph stored at the given key."""
        self.store.remove((None, None, None), context=self.contexts[self.contextURI(key)])
        
    def __setitem__(self, key, graph):
        """Assigns a graph to the given key."""
        #log.debug('__getitem__ key: %s, store key: %s', key, self.contextURI(key))
        if not isinstance(graph, Graph):
            raise TypeError('The graph was not of type rdflib.Graph.Graph')
        
        self.contexts[self.contextURI(key)] = graph
        
    def __contains__(self, key):
        return self.contextURI(key) in self.contexts
                                                            
def main():
#    store = Storage()
    store = RDFLibStorage(datapath='/tmp/store/')
    context = 'http://localhost/context/benchmark/'
    rdf = ''.join([l for l in file('../stellaris/test/benchmark/benchmark.rdf')])
    query = ''.join([l for l in file('../stellaris/test/benchmark/benchmark.rq')])
	
    #for i in range(0,1000):
    #    store.insert(rdf, context + str(i))

#    store.query(query)
    #store.query(query)    

#    f = open("./flum.rdf")
	
#    flum_str = ""
	
#    for line in f:
#        flum_str += line
		
#    store.add(flum_str, "blub")

if __name__ == "__main__":
    import hotshot, psyco

#    psyco.full()
#    prof = hotshot.Profile("hotshot_query_stats_psyco")
#    prof.runcall(main)
#    prof.close()
    main()
