# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import sys, os, logging

from benri.service import Service, Application, InitFailure
#from benri.security.authorization import AuthorizationService, AuthorizeFlatFile
#from benri.security.authfilter import AuthFilter
	
from stellaris.service.graphs import Graphs
from stellaris.service.system import SystemGraphs, SystemCollections, SystemIndices
from stellaris.service.groups import Groups
from stellaris.service.query import Query
from stellaris.service.static import Static
from stellaris.store import FrontendStore
from stellaris.exceptions import ConfigAttributeMissing
from stellaris.service.security import disable_security, enable_security
from stellaris.service.collections import CollectionsFilter

class StellarisApp(Application):
    def __init__(self, env):
        Application.__init__(self)

        try:
            graphs_prefix = env.config['service']['graphs_prefix']
        except KeyError, e:
            raise ConfigAttributeMissing('service', e)
            
        self.__store = FrontendStore(env)
        
        static = Static(env.static_dir)
        system_graphs = SystemGraphs(self.__store)
        system_collections = SystemCollections(self.__store)
        system_indices = SystemIndices(self.__store)    
        
        graphs = Graphs(self.__store, env.static_dir, prefix=graphs_prefix)
        groups = Groups(self.__store)
        query = Query(self.__store, env.static_dir, log=env.log)
        
        # always put graphs last since if the prefix is '/', i.e. the root, then the
        # dispatcher will get caught on that and forward the request to the graphs app
        for app in [static, groups, system_graphs, system_collections, system_indices, query,  graphs]:
            self.add(app)

        try:
            self.fixate()
        except InitFailure, e:
            env.log.info(str(e))

        app = self.application
        
        # security filter
        try:
            if env.config['security']['enabled'].lower() == 'true':
                app = enable_security(app, env.data_dir)
            else:
                app = disable_security(app)
            
        except KeyError, e:
            app = disable_security(app)
        
        self.replace(app)

    def stop(self):
        self.__store.close()
                
class Serve(Service):
    """
    Initializes the applications that should be served by this service.
    """
    def __init__(self, env, server_threads=50):
        Service.__init__(self, env.config, server_threads=server_threads)

        self.__app = StellarisApp(env)
        self.useApplication(self.__app.application)
        
    def start(self):
        Service.start(self)
    
    def stop(self):
        Service.stop(self)
        self.__app.stop()
