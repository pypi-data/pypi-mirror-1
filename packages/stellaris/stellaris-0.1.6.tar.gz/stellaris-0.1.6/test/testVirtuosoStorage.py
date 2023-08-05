# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, time, os, selector

from testStorage import TestStorage
from stellaris.storage.virtuoso import VirtuosoStorage
from httpserver.wsgiserver import CherryPyWSGIServer
from threading import Thread
from stellaris.service.wsgi import MemProxyWSGI
from tempfile import mkdtemp, mktemp

class TestVirtuosoStorage(TestStorage):
    
    def setUp(self):
        self.context = "http://test.org/foo" + mktemp()
        service = "localhost:8889"
        self.data_path = mkdtemp()
        memproxy = MemProxyWSGI()
        self.store = VirtuosoStorage(self.data_path, memproxy, memproxy_endpoint='http://localhost:8070/memproxy/', service=service)
        
        wsgiapp = selector.Selector()
        wsgiapp.slurp(memproxy.selectorMappings())
        self.service = CherryPyWSGIServer(('localhost', 8070), wsgiapp)
        self.service_t = Thread(target=self.service.start)
       
        self.service_t.start()
        # allows the server to start and avoids tearDown being called directly
        time.sleep(0.5)
        
    def tearDown(self):
        time.sleep(0.5)
        self.service.stop()
        self.service_t.join()
        self.store.close()

        # clean up data
        for f in os.listdir(self.data_path):
            os.remove(os.path.join(self.data_path, f))

        os.rmdir(self.data_path)
                
                    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestVirtuosoStorage('testInsertGet'))
    suite.addTest(TestVirtuosoStorage('testDelete'))   
    suite.addTest(TestVirtuosoStorage('testUpdate'))
    suite.addTest(TestVirtuosoStorage('testListUpdate'))
    suite.addTest(TestVirtuosoStorage('testGetFormats'))
    
#    suite.addTest(TestVirtuosoStorage('testInsertGraph'))
#    suite.addTest(TestVirtuosoStorage('testGetGraph'))
#    suite.addTest(TestVirtuosoStorage('testUpdateGraph'))

    #suite = unittest.TestLoader().loadTestsFromTestCase(TestStorage)
    unittest.TextTestRunner(verbosity=2).run(suite)
