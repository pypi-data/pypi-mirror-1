# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urllib, sys
from urlparse import urlsplit

from rdflib.Graph import Graph
from cStringIO import StringIO

from stellaris.storage import ContextNotFound
from stellaris.service.utils import parseQueryString, objectPath
from stellaris.service.template import Template

RDF = stellaris.RDF

log = stellaris._logger

class IntrospectionWSGI:
    """Stellaris is a compound view used directly by the implementing
       service interface. It is a WSGI app.
    """
    def __init__(self, view, tmpl):
        """The given view will be used to access the introspection-view and must 
           therefore also contain this view in its view-chain."""
        self.view = view
        self.tmpl = tmpl

    def selectorMappings(self):
        # urls.add("/{view}/{context:any}", GET=app.get, POST=app.insert, DELETE=app.delete, PUT=app.update)
        # urls.add("/query/query", GET=app.query)
        # ('/query/query', dict(GET=self.query)),
        return [('/introspection/{context:any}', dict(GET=self.get)), ('/introspection/', dict(GET=self.get))]
    
    def _parseView(self, path):
        return path[1:path[1:].find("/")+1]
            
    def get(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        
        context = ''
        
        if 'context' in args:
            context = args['context']
            
        view = self._parseView(objectPath(env))
        
#        log.debug('Received request for /' + view + '/' + context)

        queryargs = parseQueryString(env['QUERY_STRING'])
        format = 'xml'
        htmlflag = False
        if 'format' in queryargs:
            format = queryargs['format']
        # some guesswork, if the format is not specified, and it seems like a browser
        # without explicit support for rdf+xml or rdf+n3 connects, pass back html
        elif not 'format' in queryargs and 'HTTP_ACCEPT' in env and not ('application/rdf+xml' in env['HTTP_ACCEPT'] or 'application/rdf+n3' in env['HTTP_ACCEPT']):
            htmlflag = True
    
        valid_formats = ['xml', 'n3', 'html']

        if not format in valid_formats:
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Format " + format + " is not available. Valid formats: " + str(valid_formats)]

        # assume that if not application/rdf+xml or application/rdf+n3 are not
        # explicitly mentioned in the ACCEPT header, then the client is a browser
        # and the result should be HTML.
        # without HTTP_ACCEPT, just send what was requested in the query string
            
        # prepare the request object
        request = {}
        request['context'] = context
        request['format'] = format
        request['view'] = view
        
        try:
            result = self.view.get(request)
        except ContextNotFound, e:
           response("404 NOT FOUND", [('Content-Type', "text/plain")])
           return ["Context " + request['context'] + " not found\n"]
        except Exception, e:
           response("500 INTERNAL SERVER ERROR", [('Content-Type', "text/plain")])
           return [str(e)]

        if result != None:
            if htmlflag == True:
                g = Graph()
                g.parse(StringIO(result))
                # go through all collection triples in the graph
                collections = []
                contexts = []
                
                for (s,p,o) in g:
                    if p != RDF['type'] and o != RDF['Bag']:
                        if s.find('collection') > -1:
                            (_,_,path,_,_) = urlsplit(str(o))
                            path = '/'.join(path.split('/')[2:])
                            collections.append(path)
                        elif s.find('context') > -1 and p != RDF['type']:
                            (_,_,path,_,_) = urlsplit(str(o))
                            context = '/'.join(path.split('/')[2:])
                            contexts.append((context, path))
                            
                # iterate the contexts
                
                #(collections, contexts) = result
                return self.tmpl.render(response, 'introspection.html', {'contexts': sorted(contexts), 'collections': sorted(collections)})
            else:
                response("200 OK", [('Content-Type', 'application/rdf+' + format)])            
                return [result]
           
        response("404 NOT FOUND", [('Content-Type', 'text/plain')])
        return ["Context " + request['context'] + " not found\n"]
