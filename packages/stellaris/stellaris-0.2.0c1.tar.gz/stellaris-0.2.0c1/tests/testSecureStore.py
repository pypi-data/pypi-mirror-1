# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest

from stellaris.store import Store
from stellaris.store import SecureStore
from stellaris.store.exceptions import Unauthorized
from stellaris.graph import Graph

from testStore import TestStore
from utils import fileToStr, remove_dirs
from tempfile import mkdtemp

class TestSecureStore(unittest.TestCase):

    def setUp(self):
        self.db_path = mkdtemp()
        self.store_path = mkdtemp()
        
        config = {'store':{'db_path': self.db_path}}
        config['store']['version_store_path'] = self.store_path
        
        self.store = SecureStore(config)
        
#        self.test_store = Store(config)
#        self.store = StageStore(self.test_store, timeout=5.0)

    def tearDown(self):
        self.store.close()
        remove_dirs(self.db_path)
        remove_dirs(self.store_path)

    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """
        g = Graph('./tests/data/add.rdf', 'test')        
        self.store.create_graph(g, user='public')

    def testAcl(self):
        """
        Associate an ACL with a graph and checks that it allows the user to 
        write and read the graph. Other users should be denied modification
        of the graph.
        """
        user = 'test'
        user2 = 'test2'
        graph_id = 'test'
        g = Graph('./tests/data/add.rdf', graph_id)
                
        self.store.create_graph(g, user=user)
        self.store.associate_acl(g, [(user, 'w')], user=user)
        self.assertRaises(Unauthorized, self.store.create_graph, g, user=user2)

if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestSecureStore('testCreateGraph'))
    suite.addTest(TestSecureStore('testAcl'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
       
