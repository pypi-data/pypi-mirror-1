# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from __future__ import with_statement
from mutex import mutex
from contextlib import contextmanager
from threading import Lock

import time, sys, stellaris, threading
log = stellaris._logger

class LockHandler:
    """Lock management for single writer/multiple reader. A concurrent read during
       a write returns the latest completed write. Queries are not seen as reads and
       may execute during concurrent writes. Read and writes to single statements
       are still atomic.
    """
    def __init__(self): #, db):
        self.readers = 0
        self.wmutex = {}
        self.writes = 0
        self.querylock = Lock()
        self.cachelock = {}
#        self.db = db

    @contextmanager
    def cachewrite(self, context):
        if not context in self.cachelock:
            self.cachelock[context] = Lock()
            
        with self.cachelock[context]:
            yield None

    @contextmanager
    def cacheread(self, context):
        with self.cachelock[context]:
            yield None
                    
    @contextmanager
    def read(self, context):
        try:
            self.readers += 1
            
                # the writer is active, return the old value
            if context in self.wmutex and self.wmutex[context].test():
                    #print 'returning tmpdb: ', threading.currentThread(), self.tmpdb
                    yield True
            else:    
#                yield self.db
                yield False
        except Exception, e:
            #print "Reader exception: ", e, sys.exc_info(), threading.currentThread()
            #yield None
            raise e
        finally:
            self.readers -= 1
            

    @contextmanager
    def write(self, context): #, value):
        if not context in self.wmutex:
            self.wmutex[context] = mutex()
            
        log.debug('writer %s trying to get lock for %s, %s', str(threading.currentThread()), context, self.writes)
        
        while not self.wmutex[context].testandset():
            time.sleep(0.1)

        # this blocks any new writes while there are ongoing queries
        # bad! since this also blocks concurrent writes to different contexts!
#        with self.querylock:
        log.debug('writer %s allowed to write to %s, %s', threading.currentThread(), context, 
self.writes)

        try:
            self.writes += 1
            yield None 
        except Exception, e:
            log.debug('writer %s exception %s', threading.currentThread(), sys.exc_info())
            raise
        finally:
            log.debug('writer %s finished, unlock %s, %s', threading.currentThread(), context, self.writes)
            self.writes -= 1
            self.wmutex[context].unlock()

    @contextmanager
    def queryall(self):
        try:
            # there might be active writes, but there will not
            # be any new writes until this lock is released
            self.querylock.acquire(False)
            #self.queries += 1

            # left to ensure is that the query waits for all
            # active writes to finish. This is sufficient
            # since the counter will not increase until the
            # querylock is released
            while self.writes != 0:
                time.sleep(0.1)

            log.debug('Query %s executing %s', threading.currentThread(), self.writes)
            yield None
        except Exception, e:
            log.debug('Query %s exception: %s', threading.currentThread(), sys.exc_info())
            raise
        finally:
            try:
                self.querylock.release()
            except:
                # expect this to go of all the time
                pass
