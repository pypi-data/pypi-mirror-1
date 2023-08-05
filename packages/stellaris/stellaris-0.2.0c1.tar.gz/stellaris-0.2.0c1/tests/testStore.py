# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest, time
from tempfile import mkdtemp
from shutil import rmtree

from utils import file_to_str
from stellaris.store import Store
from stellaris.graph import Graph

from stellaris.store.exceptions import GraphNotFound

class TestStore(unittest.TestCase):

    def setUp(self):
        self.db_path = mkdtemp()
        self.store_path = mkdtemp()
            
        config = {'store':{'db_path': self.db_path}}        
        config['store']['version_store_path'] = self.store_path
        
        self.store = Store(config)

    def tearDown(self):
        self.store.close()
        rmtree(self.db_path)
        rmtree(self.store_path)
        
    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """
        g = Graph('./tests/data/add.rdf', 'test')
        self.store.create_graph(g, user='few')

    def testTTL(self):
        """
        Test to set and remove the TTL for a graph.
        """      
        g = Graph('./tests/data/add.rdf', 'test')
        user = 'test'
        
        self.store.create_graph(g, user=user, version=0)
        self.store.assign_ttl(g, 1.0, user=user, version=1)
        time.sleep(1.5)
        self.assertRaises(GraphNotFound, self.store.retrieve_graph, g.name, {'user': user, 'version':2})
        
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestStore('testCreateGraph'))
    suite.addTest(TestStore('testTTL'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
