# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

# integration tests using the client and the WSGI frontend

import unittest, time, os
from tempfile import mkdtemp, mktemp
from shutil import rmtree
from mimetypes import guess_type
from urlparse import urljoin
from utils import file_to_str, dump_to_file, StellarisServerThread as Server
from testWSGIGraphs import TestWSGIGraphs
from benri.client.client import NotFound

from stellaris.store.exceptions import GraphNotFound, Unauthorized
from stellaris.client import GraphClient as Client
from stellaris.graph import Graph, FileGraph
from stellaris.env import Environment

class TestWSGISecureGraphs(TestWSGIGraphs):

    def setUp(self):
        self.env_path = mktemp()
        env = Environment(self.env_path, create=True)

        self.baseuri = 'http://example.org/'
        self.graph_col = '/test_graphs/'
        
        self.bind = '127.0.0.1:9091'
        
        env.config = {'store':{'db_uri': 'sqlite:///%s' % (env.db_dir + '/tmp.db'),
#                              'data_path': env.data_dir,
                               'num_workers': '2',
                               'gc_interval': 2.0}}
        env.config['server'] = {'bind': self.bind}
        env.config['service'] = {'baseuri': self.baseuri,
                                 'graphs_prefix': self.graph_col,
                                 'security': 'enabled'}
        env.config['security'] = {'enabled': 'true',
                              'data_path': os.path.join(env.db_dir, 'security')}
        env.config['index:test'] = {'type':'rdflib-memory'}
        env.config['logging'] = {'type': 'console', 'level': 'debug'}
                
        self.client = Client('http://%s' % self.bind, base_path=os.path.join(self.env_path, '.cache'), graphs_prefix=self.graph_col)
        
        self.server = Server(env)
        self.server.start()
        
        # let server start
        time.sleep(1.0)
    
    def tearDown(self):
        self.server.stop()
        rmtree(self.env_path)
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
#    suite.addTest(TestWSGIGraphs('testUpDown'))
    suite.addTest(TestWSGISecureGraphs('testCreateGraph'))
#    suite.addTest(TestWSGIGraphs('testCreateAndRetrieveGraph'))
#    suite.addTest(TestWSGIGraphs('testModifyGraph'))
#    suite.addTest(TestWSGIGraphs('testDeleteGraph'))
#    suite.addTest(TestWSGIGraphs('testAtomicOps'))
#    suite.addTest(TestWSGIGraphs('testExists'))
#    suite.addTest(TestWSGIGraphs('testTTL'))
#    suite.addTest(TestWSGIGraphs('testAcl'))
#    suite.addTest(TestWSGIGraphs('testQuery'))
    
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestBackend)
    unittest.TextTestRunner(verbosity=2).run(suite)
#    unittest.main()        

