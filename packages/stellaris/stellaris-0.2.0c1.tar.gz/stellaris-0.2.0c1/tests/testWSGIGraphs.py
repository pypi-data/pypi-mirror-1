# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time
from tempfile import mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file, StellarisServerThread as Server
from benri.client.client import NotFound

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import GraphClient as Client
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

class TestWSGIGraphs(unittest.TestCase):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/test_graphs/'
        
        self.bind = '127.0.0.1:9090'
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                               'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'graphs_prefix': self.graph_col}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}
                
        self.client = Client('http://%s' % self.bind, graphs_prefix=self.graph_col)
        
        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
        rmtree(self.env_path)

    def graph_op(self, name, file_name, op='create', ttl=None):
        f = file(file_name, 'r')
        mime, _ = guess_type(file_name)
        stat, resp = getattr(self.client, op)(name, f, mime)
        f.close()
        return stat, resp
                    
    def testUpDown(self):
        pass

    def testCreateGraph(self):
        graph_name = 'test'
        file_name = './tests/data/add.rdf'
        stat, resp = self.graph_op(graph_name, file_name, op='create')
                
        correct_location = urljoin(urljoin('http://%s/' % self.bind, self.graph_col), graph_name)
        
        self.failUnlessEqual(stat['location'], correct_location)

    def testCreateAndRetrieveGraph(self):
        graph_name = 'test'
        file_name = './tests/data/add.rdf'

        stat, resp = self.graph_op(graph_name, file_name, op='create')
        stat, resp = self.client.retrieve(graph_name)
        
        g_in = FileGraph(graph_name, file_name)
        
        if stat['status'] == '200':
            g_out = Graph(graph_name, resp)
        else:
            raise Exception(resp)
        
        self.failUnless(g_in.graph.isomorphic(g_out.graph))

    def testModifyGraph(self):
        """
        Tries the different graph modification operations.
        """
        def modify(op):        
            name = 'test_%s' % op
            self.graph_op(name, './tests/data/add.rdf', op='create')

            self.graph_op(name, './tests/data/%s.rdf' % op, op='graph_%s' % (op))
            
            stat, resp = self.client.retrieve(name)
            g_updated = Graph(name, resp)
            g_cmp = FileGraph(name, './tests/data/add_after_%s.rdf' % op)
#            self.failUnlessEqual(g_updated.version, 2)
            self.failUnless(g_updated.graph.isomorphic(g_cmp.graph), msg = 'Graphs are not isomorphic.\nCorrect:\n%s\nFrom store:\n%s' % (g_cmp.serialized, g_updated.serialized))
        
        modify('remove')
        modify('update')
        modify('append')
        modify('replace')

    def testRetrieveVersion(self):
        graph_name = 'test'
        file_name = './tests/data/add.rdf'    
        stat, resp = self.graph_op(graph_name, file_name, op='create')
        stat, resp = self.graph_op(graph_name, './tests/data/update.rdf', op='graph_update')
        
        # first version is add.rdf
        stat, resp = self.client.retrieve(graph_name, version=1)
        g_retr = Graph(graph_name, resp)
        g_cmp = FileGraph(graph_name, './tests/data/add.rdf')
        self.failUnless(g_cmp.graph.isomorphic(g_retr.graph))
        
        # latest version is after the update
        stat, resp = self.client.retrieve(graph_name)
        g_retr = Graph(graph_name, resp)
        g_cmp = FileGraph(graph_name, './tests/data/add_after_update.rdf')
        self.failUnless(g_cmp.graph.isomorphic(g_retr.graph))

        self.assertRaises(NotFound, self.client.retrieve, graph_name, version=3)
        
    def testDeleteGraph(self):
        graph_name = 'test'
        file_name = './tests/data/add.rdf'
        stat, resp = self.graph_op(graph_name, file_name, op='create')
        stat, resp = self.client.delete(graph_name)
        
        self.failUnlessRaises(NotFound, self.client.retrieve, graph_name)

    def testAtomicOps(self):
        """
        Test the atomic operations.
        """                        
        graph_name = 'test'
        file_name = './tests/data/add.rdf'
        stat, resp = self.graph_op(graph_name, file_name, op='create')
        ops = [('append', './tests/data/append.rdf'),
               ('remove', './tests/data/remove.rdf'),
               ('update', './tests/data/update.rdf')]
        
        stat, resp = self.client.graph_atomic_operations(graph_name, ops)

        stat, resp = self.client.retrieve(graph_name)

        g_new = Graph(graph_name, resp)
        g_cmp = FileGraph(graph_name, './tests/data/update.rdf')
        self.failUnless(g_new.graph.isomorphic(g_cmp.graph))

    def testTTL(self):
        """
        Test to set and remove the TTL for a graph.
        """      
        graph_name = 'test'
        file_name = './tests/data/add.rdf'        
        stat, resp = self.graph_op(graph_name, file_name, op='create')
        stat, resp = self.client.graph_update_ttl(graph_name, 1.0)
        time.sleep(3.0)
        self.assertRaises(NotFound, self.client.retrieve, graph_name)
        
    def testExists(self):
        graph_name = '/a/b/c'
        file_name = './tests/data/add.rdf'
        stat, resp = self.graph_op(graph_name, file_name, op='create')

        def test_exists(name):
            stat, resp = self.client.retrieve(name)
            if stat['status'] == '200':
                return True
            return False

        self.failUnlessEqual(test_exists('/a/b/c'), True)            
        self.failUnlessEqual(test_exists('/a/b/c/d'), True)
        self.failUnlessRaises(NotFound, test_exists, '/a/b')
                                
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestWSGIGraphs('testUpDown'))    
#    suite.addTest(TestWSGIGraphs('testCreateGraph'))
#    suite.addTest(TestWSGIGraphs('testCreateAndRetrieveGraph'))
#    suite.addTest(TestWSGIGraphs('testModifyGraph'))
#    suite.addTest(TestWSGIGraphs('testDeleteGraph'))
#    suite.addTest(TestWSGIGraphs('testAtomicOps'))
#    suite.addTest(TestWSGIGraphs('testExists'))
#    suite.addTest(TestWSGIGraphs('testTTL'))
#    suite.addTest(TestWSGIGraphs('testRetrieveVersion'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()        

