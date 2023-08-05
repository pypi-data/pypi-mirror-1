# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urllib, os, kid

from stellaris.service.template import Template
from stellaris.service.utils import objectPath

log = stellaris._logger

class StaticWSGI:
    
    def __init__(self, files=[], path='.'):
        self.files = files
        self.path = path

    def selectorMappings(self):
        return map(lambda x: (x, dict(GET=self.static)), self.files)

    def static(self, env, response):
        contenttype = {'.xhtml': 'application/xhtml+xml',
                       '.css': 'text/css',
                       '.xsl': 'application/xml',
                       '.js': 'text/javascript'}

        path = objectPath(env)
        if path in self.files:
            response('200 OK', [('Content-Type', contenttype[os.path.splitext(path)[1]])])
            tmp_path = path.replace('/static/', '')
            contents = "".join([l for l in file(os.path.join(self.path, tmp_path))])
            return [contents]
        
        response('404 NOT FOUND', [])
        return ["404 Not Found"]
