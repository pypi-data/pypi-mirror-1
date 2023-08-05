# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, httplib2, os, urllib, time, subprocess, sys
from StringIO import StringIO

from rdflib import plugin, Namespace, URIRef
from rdflib.store import Store
from rdflib.Graph import ConjunctiveGraph

from stellaris.service.serve import ServeStellaris

class TestCherryPy(unittest.TestCase):

    cfg = "./test/test.cfg"
    
    def setUp(self):
        self.port = 20000
        self.running = subprocess.Popen([sys.executable, "test/servercherrypy.py", self.cfg], stdin=subprocess.PIPE)
        self.remotehost = "http://localhost:9001"
        #self.securehost = "https://localhost:" + str(self.port+1)
        self.context = '/context/' + str(time.time())
        self.system_ns = Namespace("http://www.gac-grid.de/stellaris/system/")

        print "Starting server with pid: ", self.running.pid
        # wait until the server is up and running, 1.0 works but not 0.5
        # 
        time.sleep(1.0)
        
    def tearDown(self):
        time.sleep(0.5)
        self.kill = subprocess.Popen(["/bin/kill", '-9', str(self.running.pid)])
        self.running.wait()
        self.kill.wait()
        
                                
    def readdata(self, f):
        s = []
    
        for l in f:
            s.append(l)
    
        return "".join(s)

    def get(self, context):
        h = httplib2.Http()
        return h.request(urllib.basejoin(self.remotehost, context), 'GET')

    def update(self, data, context, what="add", ttl=None):
        h = httplib2.Http()
        headers = {'content-type':'application/rdf+xml'}

        ttl_str = ''        
        if ttl != None:
            ttl_str = '&ttl=' + str(ttl)
        
        request_str = urllib.basejoin(self.remotehost, context) + "?action=" + what + ttl_str
        
        resp_put, content_put = h.request(request_str, 'POST', 
                                  body=data,headers=headers)
        
        return (resp_put, content_put)

    def insert(self, data, context, ttl=None):
        h = httplib2.Http()
        headers = {'content-type':'application/rdf+xml'}
        
        ttl_str = ''        
        if ttl != None:
            ttl_str = '?ttl=' + str(ttl)
        
        request_str = urllib.basejoin(self.remotehost, context) + ttl_str
                    
        resp_put, content_put = h.request(request_str, 'PUT', 
                                  body=data,headers=headers)

        return (resp_put, content_put)
                
#        self.failUnlessEqual(resp_put['status'], '201')

    def delete(self, context):
        h = httplib2.Http()
        resp_del, content_del = h.request(urllib.basejoin(self.remotehost, context), 'DELETE')
        return (resp_del, content_del)

    def validStatus(self, status):
        invalid = ['400','401','402','403','404','500','501','502']
        return status not in invalid

class RESTTest(TestCherryPy):
        
    def testPut(self):
        """Put new rdf data into the remote storage"""
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(resp_put['status'] == '201', msg=resp_put['status'])

        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)

    def testPutCollection(self):
        """Put RDF-data to a collection, a collection is a context ending with 
           '/'. This should return a 400 BAD REQUEST"""

        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context + '/')
        self.failUnless(resp_put['status'] == '400', msg=resp_put['status'])

    def testUpdateOverwrite(self):
        """Put updated rdf data"""
        h = httplib2.Http()
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'] + content_put)        

        data = self.readdata(open('./test/data/update.rdf'))
        resp_put, content_put = self.update(data, self.context, what="update")
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'] + content_put)        

        resp_get, content_get = h.request(self.remotehost + self.context, 'GET')
        
        self.failUnless(self.validStatus(resp_get['status']), msg=resp_get['status'] + content_get)
        
        self.failUnless(content_get.find("July 15, 1894") > -1 and content_get.find("August 16, 1999") == -1)
                
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)

    def testUpdateNonExisting(self):
        """
        Tries to update a non-existing context which is not allowed.
        """
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.update(data, self.context)
        self.failUnless(resp_put['status'] == '404', msg=resp_put['status'])
        
    def testUpdateAdd(self):
        """Post updated rdf data, keeping the old data."""
        h = httplib2.Http()
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

        data = self.readdata(open('./test/data/update.rdf'))
        resp_put, content_put = self.update(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

        resp_get, content_get = h.request(self.remotehost + self.context, 'GET')
        
#        print content_get
        self.failUnless(self.validStatus(resp_get['status']), msg=resp_get['status'])

        self.failUnless(content_get.find("July 15, 1894") > -1 and content_get.find("August 16, 1999") > -1)
                
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)

#    def testSystemUpdate(self):
#        """Post updated rdf data into the system context"""
#        h = httplib2.Http()   
                
#        data = self.readdata(open('./test/data/add.rdf'))
#        resp_put, content_put = self.insert(data, "/context/blub")
#        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

#        data = self.readdata(open('./test/data/update_system.rdf'))
#        resp_put, content_put = self.insert(data, "/system/")
#        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

#        resp_get, content_get = h.request(self.remotehost + "/system/blub", 'GET')
#        self.failUnless(self.validStatus(resp_get['status']), msg=resp_get['status'])
        
        #print content_get
#        self.failUnless(content_get.find("40.0") > -1 and content_get.find("30.0") == -1)

        # clean up the mess
#        (resp_del, content_del) = self.delete("/context/blub")
#        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])

        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        
    def testSystemGet(self):
        """Retrieve system metadata for a context"""

        h = httplib2.Http()        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'] + content_put)        

        resp_get, content_get = h.request(self.remotehost + self.context.replace("context", "system"), 'GET')
        
        self.failUnless(self.validStatus(resp_get['status']), msg=resp_get['status'] + content_get)

        remote_graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
 
#        print "Contents from system request ", content_get, resp_get
        remote_graph.parse(StringIO(content_get))
        
        equal = True
        
        if remote_graph.triples((None,self.system_ns["ts"],None)) == None:
            equal = False
               
        self.failUnless(equal)

        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)
       
    def testGet(self):
        """Get data from the remote storage"""
        h = httplib2.Http()

        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)

        self.failUnless(self.validStatus(resp_put['status']), msg="Error when inserting new data: " + resp_put['status'])        
                
        resp_get, content_get = h.request(self.remotehost + self.context, 'GET')
        
        self.failUnless(self.validStatus(resp_get['status']), msg="Retrieving with GET resulted in: " + resp_get['status'])
        
        local_graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
        remote_graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
 
        local_graph.parse(StringIO(data))
        remote_graph.parse(StringIO(content_get))
        
        equal = True
        
        if len(local_graph) != len(remote_graph):
            equal = False
        else:
            for (s,p,o) in local_graph:
                if (s,p,o) not in remote_graph:
                    equal = False
               
        self.failUnless(equal)

        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)

#    def testGetContextRoot(self):
#        """Get the root context."""
#        h = httplib2.Http()
                
#        resp_get, content_get = h.request(self.remotehost + '/context/', 'GET')
#        self.failUnless(self.validStatus(resp_get['status']), msg=resp_get['status'])

    def testDelete(self):
        """Delete a context from the store"""
        h = httplib2.Http()
        
        # add the content
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'] + content_put)
        
        resp_del, content_del = h.request(self.remotehost + self.context, 'DELETE')
        
        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)
        
        # make sure that it is gone
        resp_get, content_get = h.request(self.remotehost + self.context, 'GET')        
        self.failUnless(resp_get['status'] in ['404'], msg=resp_get['status'] + ' ' + content_get)

    def testDoubleInsert(self):
        """Inserts and re-inserts the data in a context. The insert operation
           overwrites data at an existing context."""
        h = httplib2.Http()
        
        # add the content
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'] + ' ' + content_put)        

        data = self.readdata(open('./test/data/bag.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'] + ' ' + content_put)
        
        resp_get, content_get = h.request(self.remotehost + self.context, 'GET')
        print "Double insert content: ", content_get        
        self.failUnless(content_get.find('August 16, 1999') == -1, msg=resp_get['status'] + ' ' + content_get)
        
    def testQuery(self):
        """Send a query to the remote storage"""
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        h = httplib2.Http()
        headers = {}
        query = """PREFIX exterms: <http://www.example.org/terms/>
                 SELECT ?date
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"""

        headers['content-type'] = 'application/x-www-form-urlencoded'
        resp_q, content_q = h.request(self.remotehost + '/query/query?query=' +
                                      unicode(urllib.quote_plus(query), 'utf-8'), 'GET', headers=headers)

        #print "query reply: ", content_q
        self.failUnless(content_q.find("August 16, 1999") > -1, msg=resp_q['status'] + ' ' + content_q)

        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)
                
#        print resp_q, content_q

    def testQueryFromNamed(self):
        """Test query from named."""
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        h = httplib2.Http()
        headers = {}
        query = "PREFIX exterms: <http://www.example.org/terms/>\
                 SELECT ?date \
                 FROM NAMED <http://stellaris.gac-grid.org" + self.context + "#context> \
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"
        headers['content-type'] = 'application/x-www-form-urlencoded'
        resp_q, content_q = h.request(self.remotehost + '/query/query?query=' +
                                      urllib.quote_plus(query), 'GET', headers=headers)

#        print content_q
        self.failUnless(content_q.find("August 16, 1999") > -1)

        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)

    def testQueryFormatXML(self):
        """Check the XML return format."""
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        h = httplib2.Http()
        headers = {}
        query = "PREFIX exterms: <http://www.example.org/terms/>\
                 SELECT ?date \
                 FROM NAMED <http://stellaris.gac-grid.org" + self.context + "#context> \
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"
        headers['content-type'] = 'application/x-www-form-urlencoded'
        resp_q, content_q = h.request(self.remotehost + '/query/query?query=' +
                                      urllib.quote_plus(query) + '&format=xml', 'GET', headers=headers)
        
        #print content_q
        self.failUnless(content_q.find('<?xml version="1.0" encoding="utf-8"?>') > -1)

        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del)

    def testQueryFormatJSON(self):
        """Test the JSON return format."""
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        h = httplib2.Http()
        headers = {}
        query = "PREFIX exterms: <http://www.example.org/terms/> \
                 SELECT ?date \
                 FROM NAMED <http://stellaris.gac-grid.org" + self.context + "#context> \
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date . }"
                 
        headers['content-type'] = 'application/x-www-form-urlencoded'
        print urllib.quote_plus(query)
        resp_q, content_q = h.request(self.remotehost + '/query/query?query=' +
                                      urllib.quote_plus(query) + '&format=json', 'GET', headers=headers)

        content_q = content_q.strip()
        self.failUnless(content_q[0] == '{' and content_q[-1] == '}')

        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'] + ' ' + content_del) 
 
# Add a test for when the user puts a document that cannot be parsed
# by the storage,

# Add a test for when an invalid SPARQL query is submitted
       
def main():
    suite = unittest.TestSuite()
#    suite.addTest(RESTTest('testPutCollection'))
#    suite.addTest(RESTTest('testPut'))
#    suite.addTest(RESTTest('testUpdateNonExisting'))    
#    suite.addTest(RESTTest('testQueryFromNamed'))
#    suite.addTest(RESTTest('testQueryFormatXML'))
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()

if __name__ == '__main__':
    main()
