# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB

import logging, os

from stellaris.store.backend import BackendStore
from stellaris.exceptions import ConfigAttributeMissing

from hashlib import md5 as graph_hash
from benri.db import DB

log = logging.getLogger('stellaris')

class StoreManager(object):

    def __init__(self, env):
        """
        A StoreManager maintains a set of StoreBackends running in separate
        processes.
        
        ``env`` - The stellaris environment containing the config and logging.
                  The section 'store' in the config can contain the following 
                  attributes:
                     
                  ``num_workers`` - number of backend store workers
                  ``gc_interval`` - time between garbage collection of old 
                                    graphs.
                  ``db_uri``      - configuration for the database backend
                  ``backup_path`` - path to where the backup should be stored
                  ``backup_interval`` - time between each backup
        """
        
        try:
            self.__num_workers = int(env.config['store']['num_workers'])
        except KeyError, e:
            raise ConfigAttributeMissing('store', str(e))

        self.__stores = []
        
        cfg = {}
        
        for key in env.config['store']:
            cfg[key] = env.config['store'][key]

        cfg['log_type'] = env.config['logging']['type']
        cfg['log_level'] = env.config['logging']['level']
        cfg['log_file'] = os.path.join(env.log_dir, 'store.log')
        cfg['db_path'] = env.db_dir

        for i in range(self.__num_workers):
            self.__stores.append(BackendStore(cfg, log=env.log))

    def responsible_store(self, graph_name):
        """
        Returns the store responsible for the given graph name.
        
        ``graph_name`` - Name of a graph.
        """
        # simple hash to decide which store should be responsible for the
        # graph
        
        # by basing this on the graph name, we also accomplish serialization
        # of graph requests assuming that the operations are performed
        # sequentially as received by the worker.
        hashval = int(graph_hash(graph_name).hexdigest(), 16)
        return self.__stores[hashval % self.__num_workers]

    def stop(self):
        for store in self.__stores:
            store.close()

if __name__ == '__main__':
    from tempfile import mkdtemp
    from stellaris.graph import FileGraph
    from shutil import rmtree    
        
    db_path = mkdtemp()
    
    config = {'store':{'db_uri': 'sqlite:///%s' % (db_path + '/tmp.db')}}        
    config['store']['num_workers'] = '2'

    sm = StoreManager(config)
    g = FileGraph('hello', './tests/data/add.rdf')
    store = sm.responsible_store('hello')
    store.create(g)
    sm.stop()
    
    rmtree(db_path)


