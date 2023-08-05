from twisted.internet import reactor
from twisted.web2 import server
from twisted.web2.channel import http
from twisted.web2 import channel
from twisted.application import service, strports
from twisted.protocols import policies

#from stellaris.storage import Storage
from stellaris.twistedstorage import TwistedStorage as Storage
from stellaris.service import ServeREST
from stellaris.service import security

from ConfigParser import SafeConfigParser
from M2Crypto.SSL.TwistedProtocolWrapper import TLSProtocolWrapper
from M2Crypto.SSL.Checker import Checker
from M2Crypto import SSL

import sys, os

# make sure that Proxy certificates are possible to use
os.putenv("OPENSSL_ALLOW_PROXY_CERTS", "1")

config_file = sys.argv[2]
config = SafeConfigParser()
        
if config.read([config_file]) == []:
    raise SystemExit("Configuration file: " + config_file + " not found")

port = sys.argv[1]
store = Storage(ttl=30.0)


secsite = server.Site(ServeREST.IceCore(store, config))
secsite = security.secureSite(secsite, security.ContextFactory(os.path.abspath('test/cert/cacert.pem'), os.path.abspath('test/cert/server_key_cert.pem')), auth=security.AuthorizeVOMRS(allowed=["/C=DE/ST=TestCert/O=GACG/CN=Unauthorized", "/C=DE/ST=TestCert/O=GACG/CN=Valid"]))

#secsite.startTLS = True

#secsite = policies.WrappingFactory(channel.HTTPFactory(secsite))
#secsite.protocol.TLS = True
#secsite.protocol = lambda factory, wrappedProtocol: \
#                TLSProtocolWrapper(factory,
#                       wrappedProtocol,
#                       startPassThrough=0,
#                       client=0,
#                       contextFactory=GSIContextFactory(),
#                       postConnectionCheck=Authorize())
                       
seclisten = reactor.listenTCP(int(port)+1, secsite, interface="127.0.0.1")                       
p = reactor.listenTCP(int(port), http.HTTPFactory(server.Site(ServeREST.IceCore(store, config))), interface="127.0.0.1")

port = p.getHost().port
remotehost = "http://127.0.0.1:" + str(port)      
print remotehost

reactor.run()

# clear the storage after the server is done
store.close()
store.clear()
