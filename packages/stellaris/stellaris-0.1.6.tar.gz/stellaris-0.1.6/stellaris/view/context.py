# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, os
from stellaris.view.view import View

log = stellaris._logger

# a view must implement:
# get - retrieving information
# insert - adding metadata
# update - changeing/updateing metadata
# delete - removeing metadata

class Context(object):
    """The context-view is supporting Creation, Retrival, Update and Delete
       on simple contexts.
    """
    def __init__(self, view):
        #self.prefix = '/context/'
        self.view = view
        #View.__init__(self, store, baseuri, prefix=self.prefix)

#    def _context(self, request):
#        context = request['context']
        
#        if context[0] == '/':
#            context = context[1:]
            
#        return os.path.join(self.prefix, context)
        
    def get(self, request):
        log.debug('GET %s', str(request))
        #tmpreq = request.copy()
        #tmpreq['context'] = self._context(request)
        return self.view.get(request)

    def insert(self, request):
#        tmpreq = request.copy()
#        tmpreq['context'] = self._context(request)
        return self.view.insert(request)
    
    def replace(self, request):
#        tmpreq = request.copy()
#        tmpreq['context'] = self._context(request)
        return self.view.replace(request)
                    
    def update(self, request):
#        tmpreq = request.copy()
#        tmpreq['context'] = self._context(request)
        return self.view.update(request)
        
    def delete(self, request):
#        tmpreq = request.copy()
#        tmpreq['context'] = self._context(request)
        return self.view.delete(request)
