# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, time

from testCherryPy import TestCherryPy

class TestLifetime(TestCherryPy):

    def testInsertTTL(self):
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context, ttl=1)
        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '200', msg=resp_get['status'] + ' ' + content_get)
        
        time.sleep(2)

        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '404', msg=resp_get['status'] + ' ' + content_get)

    def testUpdateTTL(self):
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)
        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '200', msg=resp_get['status'] + ' ' + content_get)

        # change ttl and check that the context is removed        
        resp_put, content_put = self.insert(data, self.context, ttl=1)
        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '200', msg=resp_get['status'] + ' ' + content_get)

        time.sleep(2)
        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '404', msg=resp_get['status'] + ' ' + content_get)

        # insert context with time limit and then change it to infinite
        resp_put, content_put = self.insert(data, self.context, ttl=2)
        resp_put, content_put = self.insert(data, self.context, ttl=-1)

        time.sleep(3)
        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '404', msg=resp_get['status'] + ' ' + content_get)

    def testDeleteTTL(self):
        data = self.readdata(open('./test/data/add.rdf'))    
        resp_put, content_put = self.insert(data, self.context, ttl=2)
        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '200', msg=resp_get['status'] + ' ' + content_get)

        resp_del, content_del = self.delete(self.context)
        
        time.sleep(3)

        resp_get, content_get = self.get(self.context)
        self.failUnless(resp_get['status'] == '404', msg=resp_get['status'] + ' ' + content_get)
                        
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestLifetime('testDeleteTTL'))
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()

