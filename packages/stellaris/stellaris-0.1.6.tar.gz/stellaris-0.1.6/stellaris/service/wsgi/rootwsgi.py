# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris

from stellaris.service.template import Template

log = stellaris._logger

class RootWSGI:

    def __init__(self, store, tmpl):
        self.store = store
        self.tmpl = tmpl

    def selectorMappings(self):
        # urls.add("/", GET=self.stats)
        return [('/', dict(GET=self.root))]

    def root(self, env, response):
        data = {'size': len(self.store)}
        return self.tmpl.render(response, 'root.html', data)
