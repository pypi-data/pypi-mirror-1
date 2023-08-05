# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, urllib, os, kid

from kid import XHTMLSerializer

log = stellaris._logger

class Template:

    def __init__(self, tmplpath):
        self.tmplpath = tmplpath
        
    def render(self, response, tmpl, data):
        serializer = XHTMLSerializer(encoding='utf-8')
        template = kid.Template(file=os.path.join(self.tmplpath, tmpl), **data)
        body = template.serialize(output=serializer)
        
        response("200 OK", [('Content-Type', 'text/html')])        
        return [body]
