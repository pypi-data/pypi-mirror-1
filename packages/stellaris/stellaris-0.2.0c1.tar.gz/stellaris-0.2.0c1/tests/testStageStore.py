# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import unittest
from tempfile import mkdtemp

from stellaris.store import SecureStore
from stellaris.store import StageStore
from stellaris.graph import Graph

from testStore import TestStore
from utils import fileToStr, remove_dirs

class TestStageStore(TestStore):

    def setUp(self):
        self.db_path = mkdtemp()
        self.store_path = mkdtemp()
            
        config = {'store':{'db_path': self.db_path}}        
        config['store']['version_store_path'] = self.store_path

        self.test_store = SecureStore(config)
        self.store = StageStore(self.test_store, timeout=5.0)

    def tearDown(self):
        self.store.close()
        self.test_store.close()
        remove_dirs(self.db_path)
        remove_dirs(self.store_path)
        
    def testCreateGraph(self):
        """
        Creates a graph with different parameters.
        """
        g = Graph('./tests/data/add.rdf', 'test')
        self.store.create_graph(g, user='test_user', version=0)
                      
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestStageStore('testCreateGraph'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
       
