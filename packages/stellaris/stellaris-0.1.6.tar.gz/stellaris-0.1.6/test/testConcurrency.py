# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import unittest, glob, time, threading, simplejson, random, sys

from stellaris.storage import ParseError
#from test.testConcurrentStore import ConcurrentStoreTest

from testCherryPy import TestCherryPy

from rdflib import ConjunctiveGraph as Graph, plugin
from cStringIO import StringIO
from Queue import Queue, Empty

class TestConcurrency(TestCherryPy):

    def testInsertGet(self):
        """Test Insert and then get directly and get after
           the insert finished."""
        context = '/context/insert'
        rdf = self.readdata(open('./test/data/gluece.rdf'))

        g1 = Graph()
        g1.parse(StringIO(rdf))

        #print "RDF: ", rdf
        # concurrent write and read, the read should return
        # the old context
        #self.insert(rdf, context)
        t = threading.Thread(target=self.insert, args=(rdf, context))
        t.start()
        
        #time.sleep(0.1)
        (stat, content) = self.get(context)
        self.failUnless(stat['status'] == '404', msg="Insert did probably finish before the 1st GET")
        t.join()
        
        #print stat, content
        #time.sleep(2.0)
        (stat, content) = self.get(context)
        self.failUnless(stat['status'] == '200', msg="Expected 200, got %s" % stat['status'])
        g2 = Graph()
        g2.parse(StringIO(content))
        self.failUnless(len(g1) == len(g2), msg='Retrieved graph does not have the same size as the inserted graph. G1: ' + str(len(g1)) + ', G2: ' + str(len(g2)))

    def testInsertUpdate(self):
        """Test Insert and then sends an update directly after that is
           concurrent to the write."""
        context = '/context/insert'
        put_data = self.readdata(open('./test/data/cactus_put.rdf'))
        post_data = self.readdata(open('./test/data/cactus_post.rdf'))
        
        g1 = Graph()
        g1.parse(StringIO(put_data))

        g2 = Graph()
        g2.parse(StringIO(post_data))
        
        #print "RDF: ", rdf
        # concurrent write and read, the read should return
        # the old context
        #self.insert(rdf, context)
        #t = threading.Thread(target=self.insert, args=(put_data, context))
        #t.start()
        
        #time.sleep(0.1)
        # concurrent update
        for i in range(10):
            (stat, content) = self.insert(put_data, context)
            self.failUnless(stat['status'] == '201', msg="Create failed.")
            
            (stat, content) = self.update(post_data, context)
            self.failUnless(stat['status'] == '200', msg="Update did probably finish before the insert.")
            #t.join()
            
            #print stat, content
            #time.sleep(2.0)
            (stat, content) = self.get(context)
            self.failUnless(stat['status'] == '200', msg="Expected 200, got %s" % stat['status'])
            g3 = Graph()
            g3.parse(StringIO(content))
            
    #        for (s,p,o) in g2:
    #            if not (s,p,o) in g3:
    #                self.fail('Update graph content not in full graph')
            
            g4 = Graph()
            g4 += g1
            g4 += g2
            
    #        print g2.serialize()
    #        print g3.serialize()
            self.failUnless(len(g4) == len(g3), msg='Retrieved graph does not have the same size as the inserted graph + updated graph. G1: %s, G2: %s, G3: %s' % (str(len(g1)), str(len(g2)), str(len(g3))))

            self.delete(context)
            sys.stdout.write("Iteration: %s\r" % (str(i)))
            sys.stdout.flush()

        print 
                            
    def testConcurrentInsertDiffContexts(self):
        """Test that two inserts to different contexts are
           executed simultaneously."""
        context = "/context/insert"
        rdf = self.readdata(file('./test/data/cactus_large.rdf'))

        context2 = "/context/insert2"
        rdfupdate = self.readdata(file('./test/data/update.rdf'))
        t = threading.Thread(target=self.insert, args=(rdf, context))
        t.start()
        
        # let the thread start writing
        time.sleep(0.05)
        
        self.insert(rdfupdate, context2)
        (stat2, content2) = self.get(context2)
        (stat1, content1) = self.get(context)
        
        t.join()
        self.failUnless(stat1['status'] == '404' and stat2['status'] == '200',
                        msg="Context1: %s, context2: %s" % (stat2['status'], stat1['status']))
                
    def testInsertInsertConcurrentGet(self):
        context = "/context/insert"
        rdf = self.readdata(file('./test/data/gluece.rdf'))

        # spawn a new thread executing the update
        t = threading.Thread(target=self.insert, args=(rdf, context))
        t.start()
        (stat, content) = self.insert(rdf, context)
        time.sleep(0.1)

        # read the fresh insert read
        (stat, content) = self.get(context)
        self.failUnless(stat['status'] == '200', msg=stat['status'] + ' ' + content + ' First insert did not finish')
        self.failUnless(content.find("mintaka2.aip.de") == -1, msg="First insert done already")
        t.join()
                        
    def testInsertGetUpdated(self):
        context = "/context/insert"
        rdf = self.readdata(file('./test/data/gluece.rdf'))
        rdfupdate = self.readdata(file('./test/data/gluece_update.rdf'))
        
        # insert data, wait until done
        (stat, content) = self.insert(rdf, context)
        #print "INSERT! ", stat, content
        
        # spawn a new thread executing the update
        t = threading.Thread(target=self.insert, args=(rdfupdate, context))
        t.start()
        # read the fresh insert read
        (stat, content) = self.get(context)
        self.failUnless(stat['status'] == '200', msg=stat['status'] + ' ' + content + ' First insert did not finish')
        self.failUnless(content.find("mintaka2.aip.de") == -1, msg="First insert done already")

        time.sleep(2)
        # make a concurrent read, context should be updated
        (stat, content) = self.get(context)
#        print stat, content
        self.failUnless(stat['status'] == '200', msg='Second insert did not finish')
#        print content
        self.failUnless(content.find("mintaka2.aip.de") != -1, msg="Did not find the updated value")
        t.join()

#    def testInsertDiffContexts(self):
#        """Test that two inserts to different contexts are
#           executed simultaneously."""
#        context1 = "http://example.org/insert1"
#        context2 = "http://example.org/insert2"
#        rdf = self.readdata('./test/data/gluece.rdf')
#        rdfupdate = self.readdata('./test/data/update.rdf')

#        self.insert(rdf, context1)
#        self.insert(rdfupdate, context2)
        
#        time.sleep(2)

        # just check the output and see if both threads are running...
        #self.failUnless(t2 > (t1-delta) and t2 < (t1+delta))
        

    def testInsertManySmall(self):
        context = '/context/tmp'
        rdf = self.readdata(file('./test/data/add.rdf'))

        def _insert(rdf, context):
            (stat, content) = self.insert(rdf, context+str(time.time()))
            try:
                self.failUnless(stat['status'] in ['200', '201'], 'Failed insert, context already existed ' + str(stat['status']) + ' ' + str(content))
            except:
                raise
            
        threads = []
        
        for i in range(0, 20):
#            (stat, content) = self.insert(rdf, context)
            threads.append(threading.Thread(target=_insert, args=(rdf, context)))
            #self.failUnless(stat['status'] != (200 or 201), 'Failed retrieval of data')

        [t.start() for t in threads]
        
        [t.join() for t in threads]

    def testReplaceInsertMany(self):
        context = '/context/tmp'
        rdf = self.readdata(file('./test/data/doap.rdf'))
        run = True
        
        def _insert(data, context):
            prevyear = "2005"
            year = "1999"
            while run:
                while year != "1999" and year != prevyear:
                    year = str(random.randint(0,9999))
                    
                data = data.replace(prevyear, year)
                prevyear = year
                try:
                    self.insert(data, context)
                    (stat, content) = self.get(context)
                    #print content
                except:
                    pass
        
        for i in range(0, 5):
            threading.Thread(target=_insert, args=(rdf, context)).start()

        
        def _get(context):
            while True:
                try:
                    (stat, content) = self.get(context)
                    #print content
#                    time.sleep(0.1)
                except:
                    break

#        for i in range(0,1):
#            threading.Thread(target=_get, args=[context]).start()

        time.sleep(3.0)
        run = False

    def testInsertManyLarge(self):
        """
        Insert many large RDF-files to the same context after each other, 
        make sure that the write is serialized.
        """
        context = '/context/tmp'
        rdf = self.readdata(file('./test/data/cactus_large.rdf'))

        def _insert(rdf, context):
            (stat, content) = self.insert(rdf, context)
            try:
                self.failUnless(stat['status'] in ['200', '201'], 'Failed insert, context already existed ' + str(stat['status']) + ' ' + str(content))
            except:
                raise
            
        threads = []
        
        for i in range(0, 5):
#            (stat, content) = self.insert(rdf, context)
            threads.append(threading.Thread(target=_insert, args=(rdf, context)))
            #self.failUnless(stat['status'] != (200 or 201), 'Failed retrieval of data')

        [t.start() for t in threads]
        
        [t.join() for t in threads]

    def testRandomLoad(self):
        """
        Runs several concurrent threads with different data-sizes and random
        selection of contexts for a longer period of time.
        """

        tasks = 1000
        q = Queue(0)
        num_threads = 5
        threads = []
        
        contexts = ['/context/' + str(s) for s in range(5)]
        data = [self.readdata(open('./test/data/' + f)) for f in ['cactus_large.rdf', 'gluece.rdf', 'doap.rdf', 'update.rdf', 'add.rdf']]

        def _insert(rdf, context):
            (stat, content) = self.insert(rdf, context)
            try:
                self.failUnless(stat['status'] in ['200', '201'], 'Failed insert, context already existed ' + str(stat['status']) + ' ' + str(content))
            except:
                raise

        def _worker():
            try:
                while True:
                    (data, context) = q.get(block=False)
                    _insert(data, context)
                    time.sleep(random.randint(1, 5))
            except Empty, e:
                pass
            except Exception, e:
                print e
                pass                
                
        # create a queue of work
        
        for i in range(tasks):
            q.put((random.choice(data), random.choice(contexts)))
            
        for i in range(num_threads):
#            (stat, content) = self.insert(rdf, context)
            threads.append(threading.Thread(target=_worker))

        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
    def testGetMany(self):
        context = "/context/tmp"
        rdf = self.readdata(file('./test/data/add.rdf'))

        self.insert(rdf, context)
        
        
        for i in range(0, 100):
            (stat, content) = self.get(context)
            self.failUnless(stat['status'] != 200, 'Failed retrieval of data')
            
        #time.sleep(5)        
            
if __name__ == '__main__':
    suite = unittest.TestSuite()

#    suite.addTest(TestConcurrency('testInsertUpdate'))
#    suite.addTest(TestConcurrency('testInsertGet'))
#    suite.addTest(TestConcurrency('testInsertInsertConcurrentGet'))
#    suite.addTest(TestConcurrency('testInsertGetUpdated'))
#    suite.addTest(TestConcurrency('testGetMany'))
#    suite.addTest(TestConcurrency('testInsertManySmall'))
#    suite.addTest(TestConcurrency('testInsertManyLarge'))
#    suite.addTest(TestConcurrency('testRandomLoad'))
#    suite.addTest(TestConcurrency('testReplaceInsertMany'))
#    suite.addTest(TestConcurrency('testConcurrentInsertDiffContexts'))
#    suite = unittest.TestLoader().loadTestsFromTestCase(TestConcurrency)
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
