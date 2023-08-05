import unittest, httplib2, time, sys

from testCherryPy import TestCherryPy

class BenchmarkTest(TestCherryPy):

    def timeListToCSV(self, times, out_path='/tmp/test.csv', header="Time, Count"):
        f = file(out_path, 'w+')
        
        f.write(header + '\n')

        i = 1
        for t in times:
            f.write(str(t) + ", " + str(i) + "\n")
            i += 1              
    
        f.close()
        
    def testInsert(self):
        """Measures the insertion time for a single insert with an increasing 
           number of contexts."""
        
        data = self.readdata(open('./test/data/add.rdf'))
        num_inserts = 100
        results = []
        sys.stdout.write('-'*21 + ']\r[')
        
        for i in range(num_inserts):
            if i % (num_inserts/20) == 0:
                sys.stdout.write('+')
                sys.stdout.flush()
            t = time.time()
            resp_put, content_put = self.insert(data, self.context + '_' + str(i))
            self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])        
            results.append(time.time() - t)
    
        print ''
        
        self.timeListToCSV(results, './insert_bench.csv')
        
def main():
    suite = unittest.TestSuite()
    suite.addTest(BenchmarkTest('testInsert'))    
    unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()

if __name__ == '__main__':
    main()  
