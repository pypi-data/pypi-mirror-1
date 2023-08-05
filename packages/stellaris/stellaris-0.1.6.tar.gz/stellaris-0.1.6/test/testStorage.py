# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest
from stellaris.storage import ContextNotFound

from rdflib import plugin, URIRef, BNode, Literal, Namespace
from rdflib.Graph import Graph
from rdflib.store import Store

from StringIO import StringIO

class TestStorage(unittest.TestCase):
    
    store = None

    def readdata(self, path):
        f = open(path)
        s = []
        for l in f:
            s.append(l)
        return "".join(s)

    def insert(self, datapath):
        rdf = self.readdata(datapath)
        self.store.insert(rdf, self.context)

    def update(self, datapath):
        rdf = self.readdata(datapath)
        self.store.update(rdf, self.context)
    
    def testEmptyGet(self):
        """Retrieves a non-existing context."""
        self.failUnlessRaises(ContextNotFound, self.store.get, self.context)

    def testInsertGet(self):
        """Insert data and then verify that the inserted data is correct.
        """
        g1 = Graph()
        test_file = "./test/data/add.rdf"
        g1.parse(file(test_file))
        self.insert(test_file)
        
        data = self.store.get(self.context)

        g2 = Graph()
        g2.parse(StringIO(data))
        
        self.failUnless(len(g2) == 2, "Insert failed, retrieved graph is not the same size as the inserted")
        g2 -= g1
        self.failUnless(len(g2) == 0, "Insert failed, subtraction of original from inserted graph did not remove all triples")

    def testGetFormats(self):
        """Test if the different formats (rdf/xml, n3) are returned correctly"""
        self.testInsertGet()
        
        rdf_xml = self.store.get(self.context, format='xml')
        
        try:
            g1 = Graph()
            g1.parse(StringIO(rdf_xml), format='xml')
        except Exception, e:
            self.fail(msg='Could not parse the returned XML, %s' % (str(e)))
        
        rdf_n3 = self.store.get(self.context, format='n3')
        
        try:
            g1 = Graph()
            g1.parse(StringIO(rdf_n3), format='n3')
        except Exception, e:
            self.fail(msg='Could not parse the returned N3, %s' % (str(e)))

        self.failUnlessRaises(ContextNotFound, self.store.get, 'empty', format='xml')
        self.failUnlessRaises(ContextNotFound, self.store.get, 'empty', format='n3')
        
    def testUpdate(self):
        """Tests if changing data in an existing context works."""
        self.testInsertGet()
        
        self.update("./test/data/update.rdf")
        
        g = Graph()
        g.parse(StringIO(self.store.get(self.context)))

        ns = Namespace("http://www.example.org/terms/")
        old_triple = (URIRef("http://www.example.org/index.html"), ns['creation-date'], 'August 16, 1999')
        new_triple = (URIRef("http://www.example.org/index.html"), ns['creation-date'], 'July 15, 1894')

        self.failUnless(old_triple not in g and new_triple in g, msg=g.serialize(format='n3'))
        
    def testListUpdate(self):
        self.insert('./test/data/addlist.rdf')

        ns = Namespace("http://www.example.org/terms/")
        date_t1 = (URIRef("http://www.example.org/index.html"), ns['creation-date'], 'August 16, 1999')
        date_t2 = (URIRef("http://www.example.org/index.html"), ns['creation-date'], 'September 12, 2005')
        g = Graph()
        g.parse(StringIO(self.store.get(self.context)))

        self.failUnless(date_t1 in g and date_t2 in g)
        
        self.update('./test/data/updatelist.rdf')

        date_t3 = (URIRef("http://www.example.org/index.html"), ns['creation-date'], 'July 30, 2042')
        date_t4 = (URIRef("http://www.example.org/index.html"), ns['creation-date'], 'December 1, 1934')
        g = Graph()
        g.parse(StringIO(self.store.get(self.context)))
        
        self.failUnless(date_t1 not in g and date_t2 not in g and date_t3 in g and date_t4 in g, msg=g.serialize(format='n3'))

    def testDelete(self):
        """Remove an existing context from the storage."""
        self.testInsertGet()
        self.store.delete(self.context)
        self.failUnlessRaises(ContextNotFound, self.store.get, self.context)

    def testGetGraph(self):
        self.failUnlessRaises(ContextNotFound, self.store.get, self.context)
        self.insert("./test/data/add.rdf")
        graph = self.store.get(self.context, format='system')
        # make sure that the contexts are identical
        self.failUnless(graph.identifier != self.context, "Getting from non-empty store failed")

    def testInsertGraph(self):
        """Test insert of a graph"""
        size = len(self.store)
        memstore = plugin.get('IOMemory',Store)(identifier="http://stellaris.org/memstore")
        g = Graph(store=memstore, identifier=URIRef(self.context))
        g.add((BNode(), URIRef("http://s.org/few"), Literal(1)))
        self.store.insert(g, self.context)
        self.failUnless(len(self.store) > size)
        
    def testUpdateGraph(self):
        size = len(self.store)
        self.insert("./test/data/add.rdf")    
        addsize = len(self.store)
        self.failUnless(len(self.store) > size, "Insert failed during update")

        memstore = plugin.get('IOMemory',Store)(identifier="http://reaktor.org/memstore")
        g = Graph(store=memstore, identifier=URIRef(self.context))
        g.add((URIRef("http://www.example.org/index.html"), URIRef("http://www.example.org/terms/creation-date"), Literal("August 17, 1999")))

        self.store.update(g, self.context)
        self.failUnless(len(self.store) == addsize, "Update failed, store is bigger than before")
