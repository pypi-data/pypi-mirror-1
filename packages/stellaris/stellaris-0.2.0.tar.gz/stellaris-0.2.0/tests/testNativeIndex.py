# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, os

from testIndex import TestIndex
from stellaris.index.native import MemoryIndex, BerkeleyDBIndex, MySQLIndex
from tempfile import mkdtemp

class TestMemoryIndex(TestIndex):
    
    def setUp(self):
        self.context = "http://test.org/foo"
        self.store = MemoryIndex()
        print self.store

    def tearDown(self):
        self.store.close()

class TestBDBIndex(TestIndex):
    
    def setUp(self):
        self.context = "http://test.org/foo"
        self.store_path = mkdtemp()
        self.store = BerkeleyDBIndex(self.store_path)
        print self.store

    def tearDown(self):
        if os.path.exists(self.store_path):
            for f_path in os.listdir(self.store_path):
                os.remove(os.path.join(self.store_path, f_path))
            
            os.rmdir(self.store_path)

        self.store.close()

class TestMySQLIndex(TestIndex):
    
    def setUp(self):
        self.context = "http://test.org/foo"
        self.store = MySQLIndex()

    def tearDown(self):
        self.store.close()
                    
if __name__ == '__main__':
    mem_suite = unittest.TestSuite()
    mem_suite.addTest(TestMemoryIndex('testInsertGet'))
    mem_suite.addTest(TestMemoryIndex('testUpdate'))
    mem_suite.addTest(TestMemoryIndex('testDelete'))
    mem_suite.addTest(TestMemoryIndex('testListUpdate'))
    mem_suite.addTest(TestMemoryIndex('testGetFormats'))    
    mem_suite.addTest(TestMemoryIndex('testInsertGraph'))
    mem_suite.addTest(TestMemoryIndex('testGetGraph'))
    mem_suite.addTest(TestMemoryIndex('testUpdateGraph'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
#    unittest.TextTestRunner(verbosity=2).run(mem_suite)

    bdb_suite = unittest.TestSuite()
    bdb_suite.addTest(TestBDBIndex('testInsertGet'))
    bdb_suite.addTest(TestBDBIndex('testUpdate'))
    bdb_suite.addTest(TestBDBIndex('testDelete'))
    bdb_suite.addTest(TestBDBIndex('testListUpdate'))
    bdb_suite.addTest(TestBDBIndex('testGetFormats'))    
    bdb_suite.addTest(TestBDBIndex('testInsertGraph'))
    bdb_suite.addTest(TestBDBIndex('testGetGraph'))
    bdb_suite.addTest(TestBDBIndex('testUpdateGraph'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
#    unittest.TextTestRunner(verbosity=2).run(bdb_suite)

    mysql_suite = unittest.TestSuite()
    mysql_suite.addTest(TestMySQLIndex('testInsertGet'))
    mysql_suite.addTest(TestMySQLIndex('testUpdate'))
    mysql_suite.addTest(TestMySQLIndex('testDelete'))
    mysql_suite.addTest(TestMySQLIndex('testListUpdate'))
    mysql_suite.addTest(TestMySQLIndex('testGetFormats'))    
    mysql_suite.addTest(TestMySQLIndex('testInsertGraph'))
    mysql_suite.addTest(TestMySQLIndex('testGetGraph'))
    mysql_suite.addTest(TestMySQLIndex('testUpdateGraph'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestIndex)
    unittest.TextTestRunner(verbosity=2).run(mysql_suite)
