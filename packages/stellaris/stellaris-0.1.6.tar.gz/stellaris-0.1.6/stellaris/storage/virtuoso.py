# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import os, urllib, httplib2, simplejson, rdflib

from rdflib.Graph import Graph
from tempfile import mktemp

import stellaris
from stellaris import RDF, XSD, STELLARIS
from stellaris.storage import Storage, ParseError, InvalidContext, ContextNotFound, ReplacedNotFoundContext, InsertException, UpdateException, GetException, DeleteException, QueryException, RemoveException

log = stellaris._logger

class VirtuosoStorage(Storage):

    def __init__(self, datapath, memproxy, memproxy_endpoint="http://localhost:24000/memproxy/", service="localhost:8889", baseuri="http://stellaris.gac-grid.org/"):
#		self.store = sparqlGraph.SPARQLGraph(Graph(backend='default'))
        self.__service = service
        self.__memproxy = memproxy
        self.__memproxy_endpoint = memproxy_endpoint

        if not os.path.exists(datapath):
            os.mkdir(datapath)
        
        Storage.__init__(self, datapath, baseuri)

    def __tmp_name(self):
        return mktemp()[1:]
        
    def __callret_values(self, res):
        """Returns a list of {variable name: value}-mappings for each binding
           for each row/binding in the results
           
           @param res - JSON encoded query results in python-format. Typically
                        generated with simplejson.loads(str)
        """
        
        def val(binding):
            ret = {}
            for var in [var for var in res['head']['vars']]:
                ret[var] = binding[var]['value']
            
            return ret

        return [val(b) for b in res['results']['bindings']]
        
    def close(self):
        pass
            
    def delete(self, context):
        delete_query = """
        DROP GRAPH <%s>
        """ % (self.contextURI(context))

        try:        
            json_res = simplejson.loads(self.query(delete_query, format='json'))
        except Exception, e:
            raise DeleteException("Could not delete context %s: %s" %(context, str(e)))

        results = self.__callret_values(json_res)
        
        try:
            results[0]['callret-0']
        except:
            raise DeleteException("Results from virtuoso backend could not be parsed by the JSON parser. %s" % (json_res))

        correct_res = 'Clear <%s> -- done' % (self.contextURI(context))
        
        if results[0]['callret-0'] == correct_res:
            return (True, context)
            
        raise DeleteException("Deletion of %s failed, due to virtuoso backend error: %s" % (context, results[0]['callret-0']))
                    
    def remove(self, graph, context):
        # load into a temporary graph, execute a query selecting all from that
        # graph removing it from the given context and then remove graph

        tmp_name = self.__tmp_name()
        
        # graph should be an instance of rdflib.Graph.Graph
        
        if not isinstance(graph, Graph):
            raise TypeError('graph must be an rdflib.Graph.Graph')
            
        self.insert(graph.serialize(), tmp_name)
            
        remove_query = """
        DELETE FROM GRAPH <%s>
        { ?s ?p ?o }
        WHERE { 
        GRAPH  <%s> {
          ?s ?p ?o
        } } 
        """ % (self.contextURI(context), tmp_name)

        try:
            query_res = self.query(remove_query, format='json')
            print query_res
            json_res = simplejson.loads(self.query(remove_query, format='json'))
        except Exception, e:
            raise RemoveException("Could not remove context %s: %s" %(context, str(e)))

        results = self.__callret_values(json_res)
        self.delete(tmp_name)
        
        try:
            results[0]['callret-0']
        except:
            raise RemoveException("Results from virtuoso backend could not be parsed by the JSON parser. %s" % (json_res))

        #correct_res = 'Delete from <%s>' % (self.contextURI(context))
        # result contains a number depending on how many triples, can't check
        # results
        
        if results[0]['callret-0'].find('done') > -1:
            return (True, context)
            
        raise RemoveException("Removal of %s failed, due to virtuoso backend error: %s" % (context, results[0]['callret-0']))
        
    def replace(self, graph, context, format='xml'):
        # first delete and then insert
        try:
            self.get(context)
            self.delete(context)
            self.insert(graph, context, format=format)
            return (True, context)
        
        except ContextNotFound, e:
            self.insert(graph, context, format=format)
            return (False, context)
        except:
            raise
                            
    def insert(self, graph, context, format='xml'):
        tmp_name = self.__tmp_name()
        
        self.__memproxy.add(tmp_name, graph)
        
        tmp_url = urllib.basejoin(self.__memproxy_endpoint, tmp_name)
        insert_query = """
        LOAD <%s> INTO GRAPH <%s>
        """ % (tmp_url, self.contextURI(context))

        try:
            query_res = self.query(insert_query, format='json')
            json_res = simplejson.loads(query_res)
        except Exception, e:
            self.__memproxy.remove(tmp_name)
            raise InsertException("Could not insert data into %s: %s, %s" %(context, str(e), query_res))

        results = self.__callret_values(json_res)
        self.__memproxy.remove(tmp_name)
        
        try:
            results[0]['callret-0']
        except:
            raise InsertException("Results from virtuoso backend could not be parsed by the JSON parser. %s" % (json_res))

        correct_res = 'Load <%s> into graph <%s> -- done' % (tmp_url, self.contextURI(context))
        
        if results[0]['callret-0'] == correct_res:
            return (True, context)
            
        raise InsertException("Insertion of data into %s failed, due to virtuoso backend error: %s" % (context, results[0]['callret-0']))
        
    def update(self, graph, context, format='xml'):
        tmp_name = self.__tmp_name()
        
        # graph should be an instance of rdflib.Graph.Graph
        
        tmp_graph = graph
        
        if isinstance(graph, Graph):
            tmp_graph = graph.serialize()
            
        self.insert(tmp_graph, tmp_name)
        
        update_query = """
modify graph <%s>
delete {?s ?p ?any_o}
insert { ?s ?p ?o }
where {
{ GRAPH <%s> {?s ?p ?any_o} }
{ GRAPH <%s> {?s ?p ?o} }
}
        """ % (self.contextURI(context), self.contextURI(context), self.contextURI(tmp_name))
        
        try:        
            query_res = self.query(update_query, format='json')
            json_res = simplejson.loads(query_res)
        except Exception, e:
            raise RemoveException("Could not remove context %s: %s, %s" %(context, str(e), query_res))

        results = self.__callret_values(json_res)
        self.delete(tmp_name)
        
        try:
            results[0]['callret-0']
        except:
            raise RemoveException("Results from virtuoso backend could not be parsed by the JSON parser. %s" % (json_res))

        #correct_res = 'Delete from <%s>' % (self.contextURI(context))
        # result contains a number depending on how many triples, can't check
        # results
        
        if results[0]['callret-0'].find('done') > -1:
            return (True, context)
            
        raise RemoveException("Removal of %s failed, due to virtuoso backend error: %s" % (context, results[0]['callret-0']))
        
    def query(self, query, format="xml"):
        format_map = {'xml': 'application/sparql-results+xml',
                      'json': 'application/sparql-results+json',
                      'rdfxml': 'application/rdf+xml',
                      'rdfn3': 'text/rdf+n3'}
                      
        h = httplib2.Http()
        
        headers = {}
        endpoint = 'http://' + self.__service + '/sparql/'
        
        # http://localhost:8889/sparql/?default-graph-uri=&should-sponge=&query=SELECT+*+WHERE+%7B%3Fs+%3Fp+%3Fo%7D&format=text%2Fhtml
        
        req_uri = "%s?query=%s&format=%s" % (endpoint, urllib.quote_plus(query), urllib.quote_plus(format_map[format.lower()]))
        
        stat, resp = h.request(req_uri, 'GET',  headers=headers)
        
        return resp
        
    def get(self, context, format='xml'):
        get_query = """
        CONSTRUCT {?s ?p ?o} WHERE
        { GRAPH <%s> { ?s ?p ?o }}
        """ % (self.contextURI(context))

        if format == 'xml':
            res = self.query(get_query, format='rdfxml')
            
            #print res
            
            if res == """<?xml version="1.0" encoding="utf-8" ?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
</rdf:RDF>""":
                raise ContextNotFound('Context %s does not exist.' % (context))
        elif format == 'n3':
            res = self.query(get_query, format='rdfn3')
            if res.find("# Empty TURTLE") > -1:
                raise ContextNotFound('Context %s does not exist.' % (context))            
        
        return res
                
    def clear(self):
        pass

    def close(self):
        pass
 
    def __len__(self):
        len_query = """
        SELECT count(?s)
        WHERE {
        ?s ?p ?o
        }
        """
        
        len_res = simplejson.loads(self.query(len_query, format='json'))
        
        # this should return a single result
        ret = self.__callret_values(len_res)
        
        return int(ret[0]['callret-0'])
        
    def makeGraph(self, context):
#        return Graph(self.store, self.contextURI(context))
        pass
                        
    def __getitem__(self, key):
        """Retrieves the graph stored at the given key."""
        #log.debug('__getitem__ key: %s, store key: %s', key, self.contextURI(key))
        #return self.contexts[self.contextURI(key)]
        pass

    def __delitem__(self, key):
        """Removes the graph stored at the given key."""
        #self.store.remove((None, None, None), context=self.contexts[self.contextURI(key)])
        pass
        
    def __setitem__(self, key, graph):
        """Assigns a graph to the given key."""
        #log.debug('__getitem__ key: %s, store key: %s', key, self.contextURI(key))
        #if not isinstance(graph, Graph):
        #    raise TypeError('The graph was not of type rdflib.Graph.Graph')
        
        #self.contexts[self.contextURI(key)] = graph
        pass
        
    def __contains__(self, key):
        #return self.contextURI(key) in self.contexts
        pass

if __name__ == "__main__":
    import selector, time
    from httpserver.wsgiserver import CherryPyWSGIServer
    from stellaris.service.wsgi import MemProxyWSGI
    from threading import Thread
    
    virtuoso_endpoint = "localhost:8889"
    memproxy = MemProxyWSGI()
    store = VirtuosoStorage(memproxy, memproxy_endpoint='http://localhost:8070/memproxy/', service=virtuoso_endpoint)
    
    wsgiapp = selector.Selector()
    wsgiapp.slurp(memproxy.selectorMappings())
    service = CherryPyWSGIServer(('localhost', 8070), wsgiapp)
    service_t = Thread(target=service.start)
    
    service_t.start()

    # allows the server to start
    time.sleep(0.5)
    
    context = 'http://fewfew.fwe/few'
#    rdf = ''.join([l for l in file('../stellaris/test/benchmark/benchmark.rdf')])
#    query = ''.join([l for l in file('../stellaris/test/benchmark/benchmark.rq')])

    rdf = ''.join([l for l in file('test/data/add.rdf')])
    rdf_update = ''.join([l for l in file('test/data/update.rdf')])    
    store.insert(rdf, context)

    store.update(rdf_update, context)
    print store.get(context, format='n3')
    
    query = """CONSTRUCT {?s ?p ?o} WHERE
        { GRAPH <test> { ?s ?p ?o }}"""
    print store.query(query, format='rdfn3')
        
    service.stop()
    service_t.join()
    store.close()
    
    #for i in range(0,1000):
    #    store.insert(rdf, context + str(i))

#    store.query(query)
    #store.query(query)    

#    f = open("./flum.rdf")
	
#    flum_str = ""
	
#    for line in f:
#        flum_str += line
		
#    store.add(flum_str, "blub")

