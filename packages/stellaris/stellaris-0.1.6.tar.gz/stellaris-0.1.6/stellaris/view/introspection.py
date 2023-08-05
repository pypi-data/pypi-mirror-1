# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

import stellaris, os, sys
#from stellaris.view.view import View
from stellaris import RDF, STELLARIS

from urlparse import urljoin
from rdflib import URIRef, Literal, BNode
from rdflib.Graph import Graph

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
                            
# a view must implement:
# get - retrieving information
# insert - adding metadata
# update - changeing/updateing metadata
# delete - removeing metadata

class Introspection:
    """The introspection-view creates a logical hierarchy of the existing 
       contexts managed by the storage. The hierarchy contains either
       contexts or collection of contexts. A collection is recognized from
       an ending '/'-character. Example:
       
       /context/collection/ <- a collection of contexts
       /context/collection/frobozz <- context in a collection 
       /context/collection/foo/ <- a collection under collection/
       /context/collection/foo/bar <- context in a collection

       An insert registers a new context and all collections part of the path
       in an introspection-context corresponding to the given context.
       
    """
    def __init__(self, view, baseuri, contextprefix='/context/'):
        self.prefix = '/introspection/'
        self.contextprefix = contextprefix        
        #View.__init__(self, store, baseuri, prefix=self.prefix)

        self.hierarchy = Hierarchy()
        self.view = view
        self.baseuri = baseuri

        # initialize the root
        g = Graph()
        subj = urljoin(baseuri, self.prefix)
        g.add((URIRef(subj), RDF['type'], URIRef(STELLARIS['Collection'])))
        
        colnode = URIRef(subj + 'collection')
        g.add((URIRef(subj), STELLARIS['collections'], colnode))
        g.add((colnode, RDF['type'], URIRef(RDF['Bag'])))

        contextnode = URIRef(subj + 'context')
        g.add((URIRef(subj), STELLARIS['contexts'], contextnode))
        g.add((contextnode, RDF['type'], URIRef(RDF['Bag'])))
        
        self.view.insert({'context':'/', 'input':g, 'format':'', 'view': 'introspection'})
        
    def _collection(self, context):
        """An HTML-format request returns a (collections, contexts)-tuple.         
        """
        collection = self.hierarchy.get(context)
        
        cols = [c.name for c in collection if isinstance(c, Collection)]
        contexts = [(c.name, c.path) for c in collection if isinstance(c, Context)]
        
        return (cols, contexts)
        
    def get(self, request):
        context = '/'

        if 'context' in request and len(request['context']) > 0:
            context = request['context']
            
#        if not context in self.hierarchy:
#            return None

        if request['format'] == 'html':
            return self._collection(context)

        #print "Introspection get: ", request
        return self.view.get(request)

    def _join(self, prefix, end):
        if len(end) > 0 and end[0] == '/':
            end = end[1:]

        return os.path.join(prefix, end)
                            
    def insert(self, request):
        context = request['context']

        log.debug('received insert request for %s', context)
        g = Graph()

        (contextroot, _) = os.path.split(context)

        if len(contextroot) > 0 and contextroot[-1] != '/':
            contextroot += '/'

        if contextroot == '':
            contextroot = '/'
            
        storecontext = urljoin(self.baseuri, self._join(self.contextprefix, context))

        colnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, contextroot) + 'collection'))
        contextnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, contextroot) + 'context'))

#        if contextroot not in self.hierarchy:
#            subj = self.store.contextURI(self._join(self.contextprefix, contextroot))
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
            colcontext = urljoin(self.baseuri, self._join(self.prefix, col.name))
            if colcontext not in self.view:
                # bootstrap this collection
                tmpcolnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, contextroot) + 'collection'))
                tmpcontextnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, contextroot) + 'context'))
            
                gtmp = Graph()
                gtmp.add((URIRef(colcontext), RDF['type'], URIRef(STELLARIS['Collection'])))

                gtmp.add((URIRef(colcontext), STELLARIS['collections'], tmpcolnode))
                gtmp.add((tmpcolnode, RDF['type'], URIRef(RDF['Bag'])))
    
                gtmp.add((URIRef(colcontext), STELLARIS['contexts'], tmpcontextnode))
                gtmp.add((tmpcontextnode, RDF['type'], URIRef(RDF['Bag'])))

                tmpreq = {}
                tmpreq['context'] = self._join(self.prefix, col.name)
                tmpreq['view'] = request['view']
                tmpreq['input'] = gtmp
                tmpreq['format'] = request['format']
                
                self.view.insert(tmpreq) 

            colobj = urljoin(self.baseuri, self._join(self.prefix, col.name)) #URIRef(urljoin(urljoin(self.baseuri, self.contextprefix), col.name))

            # assume that the col.name always look like /foo/bar/
            parent = "/" + "/".join(col.name.split('/')[1:-2])
            
            if parent != '/':
                parent += '/'
                
            parentcolnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, parent) + 'collection'))
            # this triple should be in the parents collection
            gtmp = Graph()
            gtmp.add((parentcolnode, RDF['li'], colobj))

            tmpreq = {}
            tmpreq['context'] = self._join(self.prefix, parent)
            tmpreq['view'] = request['view']
            tmpreq['input'] = gtmp
            tmpreq['format'] = request['format']
                
            self.view.insert(tmpreq)
        
        contextobj = URIRef(urljoin(urljoin(self.baseuri, self.contextprefix), context))
        g.add((contextnode, RDF['li'], contextobj))
        
#                '_' + str(contextcounter)
#                contextcounter += 1

        # dont change the original request (its a reference and used by other views)
        tmpreq = {}
        tmpreq['context'] = self._join(self.prefix, contextroot)
        tmpreq['view'] = request['view']
        tmpreq['input'] = g
        tmpreq['format'] = request['format']
        
        #introcontext = self.store.contextURI(self.prefix + context)
        
        return self.view.insert(tmpreq)
        
    def update(self, request):
        pass
    
    def replace(self, request):
        pass
            
    def delete(self, request):
        (ctx, cols) = self.hierarchy.remove(request['context'])

        # create a graph with the triples that should
        # be removed from the storage

        context = request['context']
        
        (contextroot, _) = os.path.split(context)

        if len(contextroot) > 0 and contextroot[-1] != '/':
            contextroot += '/'
        
        # clean out all empty collections
        for col in cols:
            tmpreq = {}
            colname = col.name
            
            if len(colname) > 0 and colname[0] == '/':
                colname = colname[1:]
                 
            tmpreq['context'] = colname
            try:
                self.view.delete(tmpreq)
            except:
                log.debug('error while deleting collection, ' + str(sys.exc_info()))

        introcontext = urljoin(self.baseuri, self._join(self.prefix, contextroot))
        
        # since this context was empty and removed, partial remove is not 
        # necessary
        if introcontext not in self.view:
            return
            
        g = Graph()
            
        storecontext = urljoin(self.baseuri, self._join(self.contextprefix, context))

        colnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, contextroot) + 'collection'))
        contextnode = URIRef(urljoin(self.baseuri, self._join(self.prefix, contextroot) + 'context'))

        #print "Deleting: ", ctx, cols

        for col in cols:
            colobj = URIRef(urljoin(urljoin(self.baseuri, self.contextprefix), col.name))
            g.add((colnode, RDF['li'], colobj))
                # '_' + str(colcounter)
#                colcounter += 1

        
        contextobj = URIRef(urljoin(urljoin(self.baseuri, self.contextprefix), context))
        g.add((contextnode, RDF['li'], contextobj))


        self.view.remove({'context': introcontext, 'input': g, 'view': 'introspection'})
        #print introcontext, self.store.get(introcontext)
        
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
    
    print [isinstance(c[p], Collection) for p in c]
    
    h.remove('/test/blub')
    h.remove('/test/blub2')
                        
    print h
    
    h.remove('/test/test/foo')
    h.remove('/test/test/flum')
        
    print h

