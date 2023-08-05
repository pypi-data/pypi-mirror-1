# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

from __future__ import with_statement
from stellaris.event.pubsub import Subscriber
from stellaris.utils import contextPath

from rdflib import Literal, URIRef
from rdflib.Graph import Graph
from datetime import datetime
from urlparse import urljoin

import stellaris, os

STELLARIS = stellaris.STELLARIS
XSD = stellaris.XSD
RDF = stellaris.RDF
log = stellaris._logger

class Context(object):
    def __init__(self, path, name):
        self.name = name
        self.path = path

    def __repr__(self):
        return '(' + self.path + ': ' + self.name + ')'
                
class Collection(object):
    """Represents a collection containing collections and contexts"""
    def __init__(self, name, parent, separator='/'):
        self.name = name
        self.collections = {}
        self.contexts = {}
        self.sep = separator
        self.parent = parent

    def __setitem__(self, path, value):
        # check if this item is a collection (i.e. ending with a separator)
        if path[-1] == self.sep:
            self.collections[path] = value
        else:
            self.contexts[path] = value
            
    def __getitem__(self, path):
        if path in self.collections:
            return self.collections[path]
        elif path in self.contexts:
            return self.contexts[path]
        raise KeyError            

    def __delitem__(self, path):
        if path in self.collections:
            del self.collections[path]
        elif path in self.contexts:
            del self.contexts[path]
        
        if len(self) == 0 and self.parent != None:
            del self.parent[self.name]
    
    def __iter__(self):
        """Returns an iterator which first iterates over the collections and 
           then the contexts.
        """
        for c in self.collections:
            yield self.collections[c]

        for c in self.contexts:
            yield self.contexts[c]
                        
    def __contains__(self, item):
        if item not in self.collections and item not in self.contexts:
            return False
        return True
        
    def __len__(self):
        return len(self.collections) + len(self.contexts)
        
    def __repr__(self):
        return ', '.join([str(self.contexts[ctx]) for ctx in self.contexts])
        
class Hierarchy(object):
    """Represents a hierarchy of collections and contexts."""
    
    def __init__(self, separator='/'):
        # a lookup table used to make retrieval of specified parts
        # of the tree faster. Contains collections only.
        self.sep = separator
        self.tree = {self.sep: Collection(self.sep, None)}

    def get(self,  path):
        """Returns the collection for the given path."""
        # make sure that the path starts with a separator
        if path[0] != self.sep:
            path = self.sep + path

        return self.tree[path]
        
    def append(self, path, context):
        """Appends/assigns the context to the given path. Creates sub-paths
           if necessary. Returns a (context, collections)-tuple."""

        # make sure that the path starts with a separator
        if path[0] != self.sep:
            path = self.sep + path
            
        curpath = self.sep
        
        newcols = []
        if path not in self.tree:
            # create all necessary sub-paths
            subpaths = path[:path.rfind(self.sep)].split(self.sep)
            subpaths = [p for p in subpaths if p != '']
            
            for subpath in subpaths:
                # using os.path.join breaks separator abstraction
                prevpath = curpath
                curpath = os.path.join(curpath, subpath + self.sep)
                if curpath not in self.tree:
                    self.tree[curpath] = Collection(curpath, self.tree[prevpath])
                    newcols.append(self.tree[curpath])
                self.tree[prevpath][curpath] = self.tree[curpath]

        ctx = None
        if not path[-1] == self.sep:
            ctx = Context(path, context)
            #print curpath, path, ctx
            self.tree[curpath][path] = ctx

        return (ctx, newcols)
        
    def remove(self, path):
        # make sure that the path starts with a separator
        if path[0] != self.sep:
            path = self.sep + path

        colpath = path[:path.rfind(self.sep)] + self.sep

        ctx = None
        if path not in self.tree:
            # remove this context from the collection it belongs to
            ctx = self.tree[colpath][path]
            del self.tree[colpath][path]

        subpaths = colpath.split(self.sep)
        subpaths = [p for p in subpaths if p != '']
        
        delcols = []
        keepcols = []
        # remove all empty subcollections
        for k in range(len(subpaths),0,-1):
            p = os.path.join(self.sep, '/'.join(subpaths[:k]) + self.sep)
            if len(self.tree[p]) == 0 and p != self.sep: 
                delcols.append(self.tree[p])
                del self.tree[p]

        return (ctx, delcols)
        
    def __contains__(self, path):
        # make sure that the path starts with a separator

        if len(path) > 0 and path[0] != self.sep:
            path = self.sep + path
        # strip away the context name, only check for collections
        return path in self.tree
                            
    def __iter__(self):
        for key in self.tree:
            yield (key, self.tree[key])

    def __repr__(self):
        return '\n'.join([str(k) + ' -> ' + str(val) for (k, val) in self])

class Introspection(Subscriber):

    def __init__(self, store, lockmanager, contextprefix):
        self.store = store
        self.viewname = 'introspection'
        self.prefix = '/introspection/'
        # use this to ensure that no-one is reading while
        # we are writing
#        self.lockmanager = lockmanager

        self.contextprefix = contextprefix        
        #View.__init__(self, store, baseuri, prefix=self.prefix)

        self.hierarchy = Hierarchy()
#        self.view = view
        self.baseuri = self.store.baseURI()

        # initialize the root
        try:
            self.store[contextPath(self.prefix, '')]
        except KeyError:
            g = self.store.makeGraph(contextPath(self.prefix, ''))
            subj = urljoin(self.baseuri, self.prefix)
            g.add((URIRef(subj), RDF['type'], URIRef(STELLARIS['Collection'])))
        
            colnode = URIRef(subj + 'collection')
            g.add((URIRef(subj), STELLARIS['collections'], colnode))
            g.add((colnode, RDF['type'], URIRef(RDF['Bag'])))

            contextnode = URIRef(subj + 'context')
            g.add((URIRef(subj), STELLARIS['contexts'], contextnode))
            g.add((contextnode, RDF['type'], URIRef(RDF['Bag'])))
        
            self.store[contextPath(self.prefix, '')] = g
        
    def _event_default(self, request):
        """Unhandled events."""
        log.debug('event not handled: %s', request)

    def _event_insert(self, request):
        """Unhandled events."""
        context = request['context']

        (contextroot, _) = os.path.split(context)

        if len(contextroot) > 0 and contextroot[-1] != '/':
            contextroot += '/'

        if contextroot == '':
            contextroot = '/'
            
        storecontext = self.store.contextURI(contextPath(self.contextprefix, context))

        colnode = URIRef(self.store.contextURI(contextPath(self.prefix, contextroot) + 'collection'))
        contextnode = URIRef(self.store.contextURI(contextPath(self.prefix, contextroot) + 'context'))

#        if contextroot not in self.hierarchy:
#            subj = self.store.contextURI(contextPath(self.contextprefix, contextroot))
#            g.add((URIRef(subj), RDF['type'], URIRef(STELLARIS['Collection'])))
#
#            g.add((URIRef(subj), STELLARIS['collections'], colnode))
#            g.add((colnode, RDF['type'], URIRef(RDF['Bag'])))

#            g.add((URIRef(subj), STELLARIS['contexts'], contextnode))
#            g.add((contextnode, RDF['type'], URIRef(RDF['Bag'])))

        (ctx, collection) = self.hierarchy.append(context, storecontext)
        #collection = self.hierarchy.get(context)
        
        # the collection and context node is based on the context, but without
        # the context name after the last slash
        
        colcounter = 1
        contextcounter = 1
        for col in collection:
            colcontext = self.store.contextURI(contextPath(self.prefix, col.name))
            if colcontext not in self.store:
                # bootstrap this collection
                tmpcolnode = URIRef(self.store.contextURI(contextPath(self.prefix, col.name) + 'collection'))
                tmpcontextnode = URIRef(self.store.contextURI(contextPath(self.prefix, col.name) + 'context'))
                gtmp = self.store.makeGraph(contextPath(self.prefix, col.name))
                gtmp.add((URIRef(colcontext), RDF['type'], URIRef(STELLARIS['Collection'])))

                gtmp.add((URIRef(colcontext), STELLARIS['collections'], tmpcolnode))
                gtmp.add((tmpcolnode, RDF['type'], URIRef(RDF['Bag'])))
    
                gtmp.add((URIRef(colcontext), STELLARIS['contexts'], tmpcontextnode))
                gtmp.add((tmpcontextnode, RDF['type'], URIRef(RDF['Bag'])))

                #tmpreq = {}
                #tmpreq['context'] = contextPath(self.prefix, col.name)
                #tmpreq['view'] = request['view']
                #tmpreq['input'] = gtmp
                #tmpreq['format'] = request['format']
                
                #self.view.insert(tmpreq) 
                self.store[contextPath(self.prefix, col.name)] = gtmp

            colobj = URIRef(self.store.contextURI(contextPath(self.prefix, col.name))) #URIRef(urljoin(urljoin(self.baseuri, self.contextprefix), col.name))

            # assume that the col.name always look like /foo/bar/
            parent = "/" + "/".join(col.name.split('/')[1:-2])
            
            if parent != '/':
                parent += '/'
                
            parentcolnode = URIRef(self.store.contextURI(contextPath(self.prefix, parent) + 'collection'))
            # this triple should be in the parents collection
            gtmp = self.store.makeGraph(contextPath(self.prefix, parent))
            gtmp.add((parentcolnode, RDF['li'], colobj))

#            tmpreq = {}
#            tmpreq['context'] = contextPath(self.prefix, parent)
#            tmpreq['view'] = request['view']
#            tmpreq['input'] = gtmp
#            tmpreq['format'] = request['format']
                
            #self.view.insert(tmpreq)
            # retrieving and adding the temporary graph
            self.store[contextPath(self.prefix, parent)] += gtmp

        parentcol = "/" + "/".join(context.split('/')[:-1])
            
        if parentcol != '/':
            parentcol += '/'

        ctx = contextPath(self.prefix, parentcol)        
        g = self.store.makeGraph(contextPath(self.prefix, parentcol))
        contextobj = URIRef(self.store.contextURI(contextPath(self.contextprefix, context)))
        g.add((contextnode, RDF['li'], contextobj))

#                '_' + str(contextcounter)
#                contextcounter += 1

        # dont change the original request (its a reference and used by other views)
#        tmpreq = {}
#        tmpreq['context'] = contextPath(self.prefix, contextroot)
#        tmpreq['view'] = request['view']
#        tmpreq['input'] = g
#        tmpreq['format'] = request['format']
        
        #introcontext = self.store.contextURI(self.prefix + context)
       
        # this context should be the parent as well, and it must exist by now...

        #with self.lockmanager.write(ctx):
        log.debug('introspection insert into %s, %s, %s', ctx, parentcol, context.split('/'))
        self.store[ctx] += g
        #return self.view.insert(tmpreq)
        
#        log.debug('event replace: %s', request)

        #log.debug('event insert: %s', request)

    def _event_replace(self, request):
        """Unhandled events."""
        self._event_insert(request)

    def _event_update(self, request):
        pass        

    def _event_delete(self, request):
        context = request['context']
        (ctx, delcols) = self.hierarchy.remove(context)

        # create a graph with the triples that should
        # be removed from the storage

        # clean out all empty collections        
        for col in delcols:
            colname = col.name

            if len(colname) > 0 and colname[0] == '/':
                colname = colname[1:]

            #tmpreq['context'] = colname
            try:
                #self.view.delete(tmpreq)
                self.store.delete(contextPath(self.prefix, colname))
            except:
                log.debug('error while deleting collection, ' + str(sys.exc_info()))
        
        # the "shortest" deleted collection needs to be removed from its parent's
        # graph
        try:
            removecol = delcols[-1].name
            g = Graph()
            
            # the parentnode is the previous path in the hierarchy
            parentcol = os.path.split(removecol[:-1])[0]
            parentnode = URIRef(self.store.contextURI(contextPath(self.prefix, parentcol) +     'collection'))
            removecolobj = URIRef(self.store.contextURI(contextPath(self.prefix, removecol)))
            g.add((parentnode, RDF['li'], removecolobj))

            # remove the collection from its parent graph
#            print g.serialize()
            self.store.remove(g, contextPath(self.prefix, parentcol))

        except:
            pass
#            removecol = context
        
        #introcontext = self.store.contextURI(contextPath(self.prefix, contextroot))

        (contextroot, _) = os.path.split(context)

        if len(contextroot) > 0 and contextroot[-1] != '/':
            contextroot += '/'
        
        # return directly if the graph storing data about the context and 
        # collection was removed already
        if self.store.contextURI(contextPath(self.prefix, contextroot)) not in self.store:
            log.debug('did not find collection: %s', self.store.contextURI(contextPath(self.prefix, contextroot)))
            return

        #print "Deleting: ", ctx, cols
        
        g = Graph()
        # add the collection that should be removed
        
#        for col in delcols:
#            colobj = URIRef(self.store.contextURI(contextPath(self.prefix, col.name)))
#            g.add((colnode, RDF['li'], colobj))
                # '_' + str(colcounter)
#                colcounter += 1

        #colnode = URIRef(self.store.contextURI(contextPath(self.prefix, contextroot) + 'collection'))
        contextnode = URIRef(self.store.contextURI(contextPath(self.prefix, contextroot) + 'context'))
        
        contextobj = URIRef(self.store.contextURI(contextPath(self.contextprefix, context)))
        g.add((contextnode, RDF['li'], contextobj))

        log.debug('removing from: %s', contextroot)
        #self.view.remove({'context': introcontext, 'input': g, 'view': 'introspection'})
        self.store.remove(g, contextPath(self.prefix, contextroot))
                        
    def notify(self, event, request):
        f = getattr(self, '_event_%s' % event, self._event_default)
        f(request)

if __name__ == '__main__':
    h = Hierarchy()
    h.append('test', 'testuri')
    h.append('/flum', 'bluburi')    
    h.append('/test/blub', 'fullpath')
    h.append('/test/blub2', 'fewwwefw')
    h.append('/test/test/flum', 'http://fwq.com')
    h.append('/test/test/foo', 'http://bar.com')

    print h

    c = h.get('/test/')
    
#    print [isinstance(c[p], Collection) for p in c]
    
    h.remove('/test/blub')
    h.remove('/test/blub2')
                        
    print h
    
    h.remove('/test/test/foo')
    h.remove('/test/test/flum')
        
    print h

    # test performance
    h_perf = Hierarchy()

    import time
    from random import randint

    num_inserts = 100000


    for j in range(100):    
        t1 = time.time()

        for i in range(0,num_inserts):
            h_perf.append('test', 'uri_' + str(i))
        
        print "inserting %s uris took %s s" %(num_inserts, str(time.time()-t1))
    
