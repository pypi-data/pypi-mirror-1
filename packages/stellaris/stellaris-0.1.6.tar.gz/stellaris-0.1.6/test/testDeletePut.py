# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from testCherryPy import TestCherryPy
import unittest, httplib2

class TestDeletePut(TestCherryPy):

    def testDeletePut(self):
        """Testing concurrency"""
        h = httplib2.Http()
        
        # this does not work with a small file since the server thread
        # finishes fast
        data = self.readdata(open('./test/data/cactus.rdf'))

        for i in range(0,100):
        # delete the existing data
            self.delete(self.context)
#        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])        
        # insert new data
            self.insert(data, self.context)
#        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        
            resp_get, content_get = self.get(self.context)
            self.failIf(resp_get['status'] == '404', "Failed with status code: " + resp_get['status'])

if __name__ == '__main__':            
    unittest.main()
