# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from __future__ import with_statement

import stellaris
from stellaris.event.pubsub import Publisher

log = stellaris._logger

CREATE = 0
UPDATE = 1
REPLACE = 2
DELETE = 3

class Event(Publisher):
    """Listens to the given view and produces events on CREATE, UPDATE, 
       REPLACE and DELETE."""
    def __init__(self, view):
        self.__view = view
        Publisher.__init__(self)

    def _caller(self, request, event, func):
        try:
            # call the method in the view below
            res = func(request)
        except:
            # when the call fails, do not notify, just pass on the exception
            raise

        # notify all the subscribers
        [s.notify(event, request) for s in self.subscribers()]
        # pass on the results
        return res
            
    def __getattr__(self, name):
        eventmap = {'insert': CREATE,
                    'update': UPDATE,
                    'replace': REPLACE,
                    'delete': DELETE}
             
        log.debug('event dispatcher: %s', name)       
        try:
            func = getattr(self.__view, name)
            #except AttributeError:
            #    pass
        except:
            raise
        
        if name in eventmap:
            return lambda request: self._caller(request, name, func)

        return func
