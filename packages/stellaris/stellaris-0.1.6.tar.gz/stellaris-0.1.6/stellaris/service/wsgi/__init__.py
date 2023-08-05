# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

# these imports make it easier to import wsgi-applications from other files
from stellaris.service.wsgi.staticwsgi import StaticWSGI
from stellaris.service.wsgi.querywsgi import QueryWSGI
from stellaris.service.wsgi.stellariswsgi import StellarisWSGI
from stellaris.service.wsgi.introspectionwsgi import IntrospectionWSGI
from stellaris.service.wsgi.rootwsgi import RootWSGI
from stellaris.service.wsgi.logwsgi import LogWSGI
from stellaris.service.wsgi.securitywsgi import SecurityWSGI
from stellaris.service.wsgi.memproxywsgi import MemProxyWSGI
