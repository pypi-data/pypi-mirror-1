# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import os, urllib, time, sys, logging

from urllib import urlencode
from urlparse import urljoin
from hashlib import md5

from datetime import datetime, timedelta
from benri.client.client import Client, NotFound

from stellaris.index import Index
from stellaris.index.exceptions import IndexReplaceFailed, IndexDeleteFailed, IndexQueryFailed, IndexNotAvailable

log = logging.getLogger(__name__)

class VirtuosoClient(object):

    def __init__(self, dav_url, sparql_url, user, password, log=None):
        self.__dav = Client(dav_url, user=user, password=password)
        self.__sparql = Client(sparql_url, user=user, password=password)
        
        try:
            self.__dav.get('')
        except NotFound, e:
            raise IndexNotAvailable('Could not find the Virtuoso DAV repository at URL: %s' % dav_url)

        try:
            self.__sparql.get('')
        except NotFound, e:
            raise IndexNotAvailable("Could not use Virtuoso's SPARQL endpoint at URL: %s" % dav_url)

        self.log = log
        
    def replace_context(self, context, data):
        headers = {}
        headers['Content-Type'] = 'application/rdf+xml'
        
        self.__dav.put('/%s' % context, data, headers=headers)

    def delete_context(self, context):
        # remove all data stored at the context by inserting an empty graph
        self.__dav.delete(context)
        
    def query(self, query, format='xml'):
        headers = {}
        headers['Accept'] = 'application/sparql-results+%s' % format
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        data = urlencode({'query': query})
        stat, resp = self.__sparql.post('/', data, headers=headers)
        return resp

class VirtuosoIndex(Index):

    def __init__(self, dav_url, sparql_url, user, password, baseuri="http://stellaris.gac-grid.org/", log=None):
        """
        Uses a Virtuoso database for indexing graphs.
        
        ``dav_url`` - URL to a DAV repository supporting RDF indexing. Ex:
                      http://example.org:8890/DAV/home/rdf_sink/
        """
        Index.__init__(self, baseuri)
        
        # mapping from graph name to the indexed graph 
        self.contexts = {}
        
        # non-opened store
        self.log = log
        self.__client = VirtuosoClient(dav_url, sparql_url, user, password, log=log)

    def init_store(self):
        pass
#        self.store.bind("stellaris", STELLARIS)

        # initialize contexts        
#        for g in self.store.contexts():
#            self.contexts[g.identifier] = g

        if self.log:
            self.log.debug("Initializing store complete.")
           
    def close(self):
        pass
#        self.gc.stop()

    def delete(self, graph_uri):
        """
        Deletes the graph with the given ``graph_uri`` from the index.
        
        ``graph_uri`` - uri of the graph to delete.
        """
            
        if not graph_uri in self.contexts:
            # graph is not stored, just return
            return

        # remove from the store and then remove from the local contexts
        self.__client.delete_context(context=self.contexts[graph_uri])
        del self.contexts[graph_uri]
            
    def replace(self, graph_uri, graph):
        """
        Overwrites the graph stored at ``graph_uri`` with the given ``graph``.
        
        ``graph_uri`` - overwrite graph with this name
        ``graph`` - use this graph to overwrite the graph
        """

        try:
            context = md5(graph_uri).hexdigest()            
            self.__client.replace_context(context, graph.serialized)
            self.contexts[graph_uri] = context
        except Exception, e:
            raise IndexReplaceFailed(e)

    def query(self, query, format="xml"):
        """
        Exectues the given query over the index.
        """
        return self.__client.query(query, format=format)
        
    def close(self):
        pass
 
    def __delitem__(self, graph_uri):
        """Alias for delete."""
        self.store.delete(graph_uri)
                
    def __setitem__(self, graph_uri, graph):
        """Alias for replace."""
        self.replace(graph_uri, graph)
        
    def __contains__(self, graph_uri):
        return graph_uri in self.contexts

if __name__ == '__main__':
#    import hotshot, psyco

    from stellaris.graph import FileGraph
    dav_url = 'http://localhost:8890/DAV/home/dav/rdf_sink/'
    sparql_url = 'http://localhost:8890/sparql/'    
    store = VirtuosoIndex(dav_url, sparql_url, 'dav', 'dav')

    graph_name = 'http://test.org/hello'
    g = FileGraph(graph_name, './tests/data/add.rdf')
    store.replace(graph_name, g)

    graph_name = 'http://test.org/hello2'
    g = FileGraph(graph_name, './tests/data/update.rdf')
    store.replace(graph_name, g)

    graph_name = 'http://test.org/hello3'
    g = FileGraph(graph_name, './tests/data/replace.rdf')
    store.replace(graph_name, g)

    query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                   SELECT ?date ?lang
                   FROM NAMED <http://local.virt/DAV/home/dav/rdf_sink/81dd9250bf5a53338f888fa79719fb57>
                   #FROM <http://stellaris.zib.de:24000/context/test>
                   #FROM NAMED <http://test.org/hello>
                   #FROM NAMED <http://test.org/hello2>                   
                   WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                           <http://www.example.org/index.html> dc:language ?lang . }
                """

    query = """
    select ?s ?p ?o
    from named <http://local.virt/DAV/home/dav/rdf_sink/81dd9250bf5a53338f888fa79719fb57>
    where { ?s ?p ?o }
    """
    
    query = """
select distinct ?s ?p ?o where { graph <http://local.virt/DAV/home/dav/rdf_sink/81dd9250bf5a53338f888fa79719fb57> { ?s ?p ?o } }
    """

    print store.contexts
    print store.query(query, format='json')
    
    store.replace(graph_name, g)
    store.delete(g.uri)
    
    try:
        print store.contexts[g.uri]
    except KeyError, e:
        pass
        
    store.close()
    
#    psyco.full()
#    prof = hotshot.Profile("hotshot_query_stats_psyco")
#    prof.runcall(main)
#    prof.close()
#    main()
