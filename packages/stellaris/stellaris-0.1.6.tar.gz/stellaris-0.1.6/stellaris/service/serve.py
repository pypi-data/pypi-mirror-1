# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import selector, stellaris, signal, sys, logging, os, Queue, socket, time
from threading import Thread
from benri.lifetime import Lifetime

from httpserver.wsgiserver import CherryPyWSGIServer
from stellaris.storage.native import RDFLibStorage
from stellaris.storage.virtuoso import VirtuosoStorage
from stellaris.scheduler import Scheduler
from stellaris.service.wsgi import StellarisWSGI, RootWSGI, QueryWSGI, StaticWSGI, IntrospectionWSGI, LogWSGI, SecurityWSGI, MemProxyWSGI

from stellaris.service.template import Template

from stellaris.service.security import SecurityService
from stellaris.service.security import NoValidAuthorizationTypes

from stellaris.service.config import Config

log = stellaris._logger

class ServeStellaris:

    def __init__(self, configpath=None, workdir = ''):
        
        config = Config(configpath, workdir)
        
        #print "Using baseuri: ", config.get("service", "baseuri")
        datapath = None
        
        try:
            datapath = config['storage']['data_path']
        except KeyError, e:
            # using memory storage
            sys.exit('You must define a data path since it is used to store persistent information on lifetime management and user access')
        
        backend = config['storage']['backend'].lower()

        self.apps = []

                        
        if backend == 'rdflib-persistent':
            self.store = RDFLibStorage(datapath, baseuri=config['service']['baseuri'])
        elif backend == 'rdflib-memory':
            self.store = RDFLibStorage(datapath, memory=True, baseuri=config['service']['baseuri'])
        elif backend == 'virtuoso':
            try:
                service = config['storage']['virtuoso']            
                memproxy = MemProxyWSGI()
                self.store = VirtuosoStorage(datapath, memproxy, service=service, baseuri=config['service']['baseuri'])
                self.apps.append(memproxy)
            except Exception, e:
                sys.exit('Virtuoso is not correctly configured: %s' % str(e))
        else:
            sys.exit('Backend %s is not available. Try either virtuoso or rdflib' % backend)
            
        #self.scheduler = Scheduler(1)
        
        try:
            tmpl = Template(config["service"]["template_path"])
        except KeyError, e:
            tmpl = "./templates/"

        log.debug('Initializing template path: %s' % tmpl)
                  
        self.lifetime = Lifetime(os.path.join(self.store.data_path, 'lifetime'), None)
        stellariswsgi = StellarisWSGI(self.store, tmpl, self.lifetime)
        
        self.apps.append(stellariswsgi)
        #self.apps.append(IntrospectionWSGI(stellariswsgi.view))
        self.apps.append(RootWSGI(self.store, tmpl))
        #self.apps.append(QueryWSGI(self.store, self.scheduler))

        try:
            staticpath = config['service']['static_path']
        except KeyError, e:
            staticpath = "./static/"
        
        log.debug('Initializing static path: %s' % staticpath)
        
        self.apps.append(StaticWSGI(['/static/style.css', '/static/sparql-xml-to-html.xsl', '/static/query.js', '/static/introspection.js'], staticpath))
                
        wsgiapp = selector.Selector()
        
        for app in self.apps:
            wsgiapp.slurp(app.selectorMappings())
        
        self.port = int(config["service"]["port"])

#        self.server = WSGIServer(s , bindAddress = '/tmp/fastcgi.sock')
#        self.server.start = self.server.run
        
        self.secure = False
        # log and security wsgi apps are wrappers around other wsgi apps
        if config['security']['enabled'].lower() == 'true':
            try:
                self.secservice = SecurityService(config, interval=60.0)
            except NoValidAuthorizationTypes, e:
                sys.exit('Security is enabled, but no valid authorization sources found.')

            self.reverse_proxy = False
            try:
                proxy_host = config['security']['reverse_proxy'].split(':')
                self.reverse_proxy = True
            except KeyError:
                try:
                    self.secure_port = int(config['security']['secure_port'])
                    proxy_host = (None, self.secure_port)
                except:
                    sys.exit('Security is enabled, no secure port or reverse proxy is specified.')                    
            wsgiapp = SecurityWSGI(wsgiapp, self.secservice, host=proxy_host[0], port=proxy_host[1])
            self.secure = True
                    
        # setup logging
        
        try:
            logfile = config["service"]["access_log_path"]
            wsgiapp = LogWSGI(wsgiapp, logfile)
        except:
            pass
        
        self.server = CherryPyWSGIServer(('', self.port), wsgiapp)
        
        if self.secure:
            # start a secure cherrypy server
            self.https_server = CherryPyWSGIServer(('', self.secure_port), wsgiapp)

#            self.https_server.ssl_private_key = config["security"]["ssl_key_path"]
#            self.https_server.ssl_certificate = config["security"]["ssl_cert_path"]            
            self.https_server.ssl_key_cert = config["security"]["ssl_key_cert_path"]            
            self.https_server.ssl_ca_certs = config["security"]["ssl_cacert_path"]            
            
            # run the https server in a separate thread and the http server
            # in the main thread
            self.https_server_t = Thread(target=self.https_server.start)
        
        # setup common logging, if defined
        try:
            _filehandler = logging.FileHandler(config['service']['common_log_path'])
            _filehandler.setFormatter(logging.Formatter('%(asctime)s (%(levelname)s) %(name)s:%(module)s:%(message)s'))
            log.addHandler(_filehandler)
        except:
            pass
        
        # install a signal handler for a clean shutdown when a kill is
        # received 
        signal.signal(signal.SIGTERM, self._sigterm)

    def _sigterm(self, signum, frame):
        log.debug("Received SIGTERM, stopping server.")
        raise SystemExit("Received signal SIGKILL")
            
    def start(self):
        log.info("Starting server at " + str(self.port))
        self.lifetime.start()
        # let the lifetime sub-system start all threads
        time.sleep(0.1)
        
        if self.secure:
            try:
                self.secservice.start()
            except socket.error, e:
                log.error("Secure port %s is busy, change the configuration file to use another port for HTTPS." % (str(self.secure_port)))
                self.stop()
            
            if not self.reverse_proxy:
                #self.https_server_t.setDaemon(0)
                self.https_server_t.start()
                #self.https_server.start()
            log.info("Secure server started at " + str(self.secure_port))
        
        try:    
            self.server.start()
        except socket.error, e:
            log.error('Port %s is busy, change the port-attribute in the configuration file.' % (str(self.port)))
            self.stop()
            
#        self.server.run()

    def stop(self):
        self.lifetime.stop()
        
        if self.secure:
            self.secservice.stop()
            
            log.info('Stopping secure server')
            # stop the https server and wait for its thread.
            if not self.reverse_proxy:
                self.https_server.stop()
                self.https_server_t.join()

        self.server.stop()    
        self.store.close()
                   
        log.info("Server shutdown complete")

if __name__ == '__main__':
    server = ServeStellaris(sys.argv[1])
#    server = ServeStellaris('./etc/stellaris.cfg')

    try:
        server.start()
    except KeyboardInterrupt, e:
        log.debug("Received a keyboard interrupt, stopping server.")
        server.stop()
    except SystemExit, e:
        log.debug("Received system exit, stopping server.")
        server.stop()
    
#if __name__ == '__main__':
#    import hotshot
#    prof = hotshot.Profile("hotshot_stellaris_stats")
#    prof.runcall(main)
#    prof.close()
