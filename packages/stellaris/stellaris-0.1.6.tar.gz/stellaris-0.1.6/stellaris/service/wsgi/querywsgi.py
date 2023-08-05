# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urllib, os, sys, time

from stellaris.service.utils import parseQueryString, queryContentType
from stellaris.view import View, Query

from urlparse import urlunsplit
from datetime import datetime

RDF = stellaris.RDF
XSD = stellaris.XSD

log = stellaris._logger

class QueryWSGI:

    def __init__(self, view, tmpl):
        # this view is just a dummy since needs a view for input
#        self.store = store
#        queryview = Query(store)
#        isolation = Isolation(store, scheduler, queryview)
#        blocking = Blocking(isolation)
        self.view = view
        self.tmpl = tmpl

    def selectorMappings(self):
        # urls.add("/", GET=self.stats)
        return [('/query/', dict(GET=self.root)), ('/query/query', dict(GET=self.query))]

    def root(self, env, response):
        #data = {'size': len(self.store)}
        
        #context = self.store.contextURI('/query/stored/')
        #q = """
#PREFIX rdf:<%s>
#PREFIX xsd:<%s>
#PREFIX stellaris:<%s>
               
#SELECT ?query ?ts
#FROM NAMED <%s>
#WHERE {
#?query rdf:type stellaris:Query .
#?query stellaris:ts ?ts .
#} ORDER BY DESC(?ts) LIMIT 10
#""" % (str(RDF), str(XSD), str(ICECORE), context)
        
        #request = {}
        #request['query'] = q
        #request['format'] = 'json'       
        #results = self.view.query(request)
        
        #jsonres = simplejson.loads(results)
        
        #data = {'queries': [(k['query']['value'], k['ts']['value']) for k in jsonres['results']['bindings']]}
        data = {'queries': []}
#        print jsonres['results']['bindings']
        return self.tmpl.render(response, 'query.html', data)

    def query(self, env, response):
        (_, args) = env['wsgiorg.routing_args']
        
        queryargs = parseQueryString(env['QUERY_STRING'])
        if not 'query' in queryargs:
            response("400 BAD REQUEST", [('Content-Type', "text/plain")])
            return ['No query specified. ' + str(env)]            

        format = 'xml'
        if 'format' in queryargs:
            format = queryargs['format']

        valid_formats = ['xml', 'json']

        if not format in valid_formats:
           response("400 BAD REQUEST", [('Content-Type', "text/plain")])
           return ["Format " + format + " is not valid. Available formats: " + str(valid_formats)]
             
        #log.debug("query received " + queryargs['format'] + ", " + queryargs['query'])
        
        request = {}
        request['query'] = queryargs['query']
        request['format'] = format

        # pass info for storing the query
#       request['queryurl'] = urlunsplit((env['wsgi.url_scheme'], env['HTTP_HOST'], env['PATH_INFO'], env['QUERY_STRING'], ''))
                
        res = ""
        
        querytime = 0.0
        try:
            dt = time.clock()        
            res = self.view.query(request)
            querytime = time.clock()-dt
            log.info('Query execution time: %s', querytime)
        except Exception, e:
            response("400 BAD REQUEST", [('Content-Type', "text/plain")])
            log.debug("error: " + str(e))
            return [str(e) + "\n"]
        
        # if the client knows the sparql format return the correct mime-type,
        # otherwise assume that it is something that can handle xml
        if format=='json' or ('HTTP_ACCEPT' in env and 'application/sparql-results+' + format in env['HTTP_ACCEPT']):
            # ensures that the json output is in UTF-8 according to the standard
            # shouldn't this be ensured by rdflib?
            res = res.encode('utf-8')
            headers = [('Content-Length', str(len(res)))]        
            response("200 OK", headers + [('Content-Type', "application/sparql-results+" + format)])
        else:
            #res = str(res).replace('<sparql', '<?xml-stylesheet type="text/xsl" href="/static/sparql-xml-to-html.xsl"?><sparql')
            headers = [('Content-Length', str(len(res)))]            
            response("200 OK", headers + [('Content-Type', "application/xml")])

        #print "query results: ", res
        return [res]
