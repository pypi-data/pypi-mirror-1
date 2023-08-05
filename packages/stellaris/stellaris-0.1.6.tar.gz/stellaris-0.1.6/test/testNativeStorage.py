# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, os

from testStorage import TestStorage
from stellaris.storage.native import RDFLibStorage
from tempfile import mkdtemp

class TestNativeStorage(TestStorage):
    
    def setUp(self):
        self.context = "http://test.org/foo"
        self.store_path = mkdtemp()
        self.store = RDFLibStorage(self.store_path)
        print self.store

    def tearDown(self):
        if os.path.exists(self.store_path):
            for f_path in os.listdir(self.store_path):
                os.remove(os.path.join(self.store_path, f_path))
            
            os.rmdir(self.store_path)

        self.store.close()
                    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestNativeStorage('testInsertGet'))
    suite.addTest(TestNativeStorage('testUpdate'))
    suite.addTest(TestNativeStorage('testDelete'))
    suite.addTest(TestNativeStorage('testListUpdate'))
    suite.addTest(TestNativeStorage('testGetFormats'))    
    suite.addTest(TestNativeStorage('testInsertGraph'))
    suite.addTest(TestNativeStorage('testGetGraph'))
    suite.addTest(TestNativeStorage('testUpdateGraph'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestStorage)
    unittest.TextTestRunner(verbosity=2).run(suite)
