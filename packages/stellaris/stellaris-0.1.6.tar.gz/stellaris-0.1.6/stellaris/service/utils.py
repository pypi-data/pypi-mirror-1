# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import urllib

# no error checking yet....
def parseQueryString(qs):
    """Parses a query string received in a POST/GET request. Handles data
       of type application/x-www-form-urlencoded. Returns a dictionary with
       (key,value)-pairs. The value is a list."""
    ret = {}
    for q in qs.split("&"):
        key = q[:q.find("=")]
        value = q[q.find("=")+1:]

        if key in ret:
            tmpval = ret[key]
            if not isinstance(tmpval, list):
                ret[key] = [tmpval]
                            
            ret[key] = ret[key].append(urllib.unquote_plus(value))
        ret[key] = urllib.unquote_plus(value)
    return ret

# returns the preferred content-type based on the accept-variable from the 
# request environment. Defaults to application/xml.
def contentType(env):
    if 'HTTP_ACCEPT' in env:
        # prefer json over xml
        if 'application/rdf+json' in env['HTTP_ACCEPT']:
            return 'application/rdf+json'
        elif 'application/rdf+xml' in env['HTTP_ACCEPT']:
            return 'application/rdf+xml'
    return 'application/xml'

# returns the preferred content-type based on the accept-variable from the 
# request environment. Defaults to application/xml. If the client supports
# both XML and JSON, prefer JSON.

def queryContentType(env):
    if 'HTTP_ACCEPT' in env:
        # prefer json over xml
        if 'application/sparql-results+json' in env['HTTP_ACCEPT']:
            return 'application/sparql-results+json'
        elif 'application/sparql-results+xml' in env['HTTP_ACCEPT']:
            return 'application/sparql-results+xml'
    return 'application/xml'
    
# returns the correct path from 'SCRIPT_NAME', 'PATH_INFO' when
# given an environment

def objectPath(env):
    return env['SCRIPT_NAME'] + env['PATH_INFO']

