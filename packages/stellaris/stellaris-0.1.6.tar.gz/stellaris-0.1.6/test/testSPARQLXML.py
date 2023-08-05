# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest
from stellaris.storage import ContextNotFound
from stellaris.storage.native import RDFLibStorage

from rdflib import plugin, URIRef, BNode, Literal
from rdflib.Graph import Graph
from rdflib.store import Store
from tempfile import mkdtemp


class TestSPARQLXML(unittest.TestCase):
    
    def setUp(self):
        self.context = "http://test.org/foo"
        self.store = RDFLibStorage('/tmp/stellaris-test')
        print self.store
        
    def tearDown(self):
        self.store.close()

    def readdata(self, path):
        f = open(path)
        s = []
        for l in f:
            s.append(l)
        return "".join(s)

    def insert(self, datapath):
        rdf = self.readdata(datapath)
        self.store.insert(rdf, self.context)

    def testBasicQuery(self):
        self.insert("./test/data/add.rdf")
        self.insert("./test/data/add2.rdf")
        
        query = """PREFIX exterms: <http://www.example.org/terms/>
                   PREFIX dc: <http://purl.org/dc/elements/1.1/>
                 SELECT ?date ?lang
                 WHERE { <http://www.example.org/index.html> exterms:creation-date ?date .
                         <http://www.example.org/index.html> dc:language ?lang . }"""

        result = """<?xml version="1.0" encoding="utf-8"?><ns0:sparql xmlns:ns0="http://www.w3.org/2005/sparql-results#"><ns0:head><variable name="date" /><variable name="lang" /></ns0:head><ns0:results distinct="False" ordered="False"><ns0:result><ns0:binding name="date"><ns0:literal>August 16, 1999</ns0:literal></ns0:binding><ns0:binding name="lang"><ns0:literal>en</ns0:literal></ns0:binding></ns0:result><ns0:result><ns0:binding name="date"><ns0:literal>May 1, 3232</ns0:literal></ns0:binding><ns0:binding name="lang"><ns0:literal>en</ns0:literal></ns0:binding></ns0:result></ns0:results></ns0:sparql>"""
        
        self.failUnlessEqual(self.store.query(query), result)
                        
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestSPARQLXML('testBasicQuery'))
    unittest.TextTestRunner(verbosity=2).run(suite)
