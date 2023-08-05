import unittest, httplib2, os, urllib, time, subprocess, sys
from StringIO import StringIO

from rdflib import plugin, Namespace, URIRef
from rdflib.store import Store
from rdflib.Graph import ConjunctiveGraph

from stellaris.service.serve import ServeStellaris

from testCherryPy import TestCherryPy

class IntrospectionTest(TestCherryPy):
        
    def testSingleContext(self):
        """Insert a single context and retrieve the introspection graph."""

        h = httplib2.Http()        
        context = '/context/foo'        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

        resp_get, content_get = h.request(self.remotehost + '/introspection/', 'GET')
        
        #print content_get
        self.failUnless(content_get.find("/context/foo") > -1)
        # clean up the mess
        (resp_del, content_del) = self.delete(context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])

    def testCollection(self):
        """Insert a single collection and retrieve the introspection graph."""

        h = httplib2.Http()        
        context = '/context/foo/blub'       
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/', 'GET')
        
        #print content_get
        self.failUnless(content_get.find("/context/foo/blub") > -1)
        # clean up the mess
        (resp_del, content_del) = self.delete(context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/', 'GET')
        #print content_get
        self.failUnless(content_get.find("/context/foo/") == -1)

    def testDeepCollection(self):
        """Insert contexts with different tree depth."""

        h = httplib2.Http()        
        context1 = '/context/foo/blub'       
        context2 = '/context/foo/bar/test/blub'
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, context1)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

        resp_put, content_put = self.insert(data, context2)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/', 'GET')
        self.failUnless(content_get.find("/context/foo/blub") > -1)

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/bar/', 'GET')
        self.failUnless(content_get.find("/introspection/foo/bar/test/") > -1)

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/bar/test/', 'GET')
        self.failUnless(content_get.find("/context/foo/bar/test/blub") > -1)
                
        # clean up the mess
        (resp_del, content_del) = self.delete(context1)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/', 'GET')
        #print content_get
        self.failUnless(content_get.find("/context/foo/blub") == -1)
        self.failUnless(content_get.find("/introspection/foo/bar/") > -1)

        (resp_del, content_del) = self.delete(context2)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])

        resp_get, content_get = h.request(self.remotehost + '/introspection/foo/', 'GET')
        #print content_get
        self.failUnless(content_get.find("/introspection/foo/bar/") == -1)
       
def main():
    unittest.main()
        
if __name__ == '__main__':
    main()
