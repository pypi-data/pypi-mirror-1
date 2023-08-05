# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging, os, time
from base64 import urlsafe_b64decode as decode, urlsafe_b64encode as encode
from urlparse import urljoin
from rdflib.Graph import Graph as RDFLibGraph
from cStringIO import StringIO

from stellaris.utils import Property

log = logging.getLogger('stellaris')
   
class Graph(object):
    """
    A Graph is a temporary representation of a graph before it is inserted
    into a store.
    
    Attributes:
    
    ``name`` - the internal name of the graph
    ``graph`` - an RDFLib Graph, parsed on-demand (may raise an exception when
                it is accessed for the first time)
    ``serialized`` - serialized form of the ``graph`` attribute    
    ``uri`` - the URI for the named graph
    ``version`` - The version of the graph indicates how many times it has been
                  committed since it was created. Initial version is 1.
    ``ttl`` - The time in seconds after 1970 when the graph should be removed.
    
    The ``graph``-attribute parses the content of the ``serialized``-attribute 
    to get the actual triples. If the ``graph`` is modified, the data is updated
    accordingly. An externally modified graph must use the commit()-method to
    update the ``serialized``-attribute.
    
    Graphs are _not_ thread-safe.
    """
    
    def __init__(self, name, serialized, uri=None, ttl=None, version=1, baseuri='http://stellaris.zib.de/'):
        """
        Creates a new graph.

        ``name`` - the internal name of the graph        
        ``serialized`` - serialized form of the ``graph`` attribute
        ``uri`` - the URI for the named graph. If ``None``, the baseuri is used
                  to construct the URI together with the graph's name. This
                  should preferably be network-accessible.
        ``ttl`` - relative time in seconds when the graph can be removed. Can
                  be given as float, but the graph removal may not be that 
                  exact since it depends on when the garbage collection method
                  of a store is called.
        ``version`` - set the version of the graph
        ``baseuri`` - (optional) Defines the baseuri from which to construct
                      the graph's URI, i.e the full name of the graph.
                      
        """
        # Name of a graph
        self._name = name

        # cached serialized version of the graph
        self._data = serialized
        self._is_modified = False
                
        # the graph is None until first access
        self._graph = None
        
        self._baseuri = baseuri

        self._uri = uri
        # when no uri is given, create it by using the baseuri
        # this should reflect the network accessible name of the graph
        if not self._uri:
            pathname = self._name
            if pathname.startswith('/'):
                pathname = self._name[1:]
            
            self._uri = urljoin(baseuri, pathname)

        self._ttl = ttl

        if ttl:
            self._ttl = time.time() + ttl
                    
        # initial graph version
        self._version = version
        
    @Property
    def uri():
        """
        The URI for the named graph. Read-only.
        """
        def fget(self):
            return self._uri
            
    @Property
    def name():
        """
        The internal name of the graph. Read-only.
        """
        def fget(self):
            return self._name

    @Property
    def version():
        """
        The version indicates how many times a graph has been commited.
        """
        def fget(self):
            return self._version

    @Property
    def ttl():
        """
        Defines the time in seconds after epoch when the graph should be 
        removed. Setting the ttl is done by giving a relative value.
        """
        def fget(self):
            return self._ttl

        def fset(self, ttl):
            if ttl == None:
                self._ttl = None
            else:
                self._ttl = time.time() + ttl

        def fdel(self):
            self._ttl = None
            
    @Property
    def serialized():
        """
        Serialized version of the graph. This is updated when the ``graph``-
        attribute is changed. Read-only.
        """
        def fget(self):
            if self._is_modified:
                self._data = self._graph.serialize()
                self._is_modified = False

            return self._data

    @Property
    def graph():
        """
        The graph attribute reads in a graph defined by the path on demand.
        Note if this is changed externally, the ``data``-attribute will be
        inconsistent until commit() is called.
        """
        def fget(self):
            if self._graph != None:
                return self._graph
            # no data, just return an empty graph
            elif self._data == None:
                return RDFLibGraph()

            # serialize the graph
            self._graph = RDFLibGraph()
        
            format = 'n3'

            if self._data.startswith('<'):
                format = 'xml'
        
            try:
                self._graph.parse(StringIO(self._data), publicID=self.uri, format=format)
            except Exception, e:
                raise e

            return self._graph

        def fset(self, graph):
            if self._graph != None:
                self._graph = graph
            
            raise AttributeError('The graph cannot be updated after it has once been set. Use the methods of this class instead or commit.')
            
    def replace(self, graph, commit=True):
        """
        Replaces the local graph with the given graph.
        
        ``graph`` - replace the graph with the new triples in this graph
        """
        self._graph = graph.graph
        self._is_modified = True
        
        if commit:
            self.commit()
        
    def update(self, graph, commit=True):
        """
        Updates the instance with the given graph. An update means replacing 
        existing (s,p)-tuples which matches (s,p)-tuples from the new graph.
        
        ``graph`` - update the instance graph with this graph
        """
        lists = {}
        for (s,p,o) in graph.graph:
            if (s,p) not in lists:
                lists[(s,p)] = []
            
            lists[(s,p)].append((s,p,o))
                                    
        # if there is a list of triples
        # replace the current list by setting
        # graph.set() replaces triples with (s,p)
        # then add the rest of the list to the graph
        g = self.graph
        
        for sppair in lists:
            toptriple = lists[sppair].pop()
            
            g.set(toptriple)
            
            for t in lists[sppair]:
                g.add(t)

        self._is_modified = True
        
        if commit:
            self.commit()
        
    def append(self, graph, commit=True):
        """
        Appends all triples from graph.
        
        ``graph`` - append triples from this graph
        """
        g = self.graph
        g += graph.graph
        self._is_modified = True
        
        if commit:
            self.commit()
        
    def remove(self, graph, commit=True):
        """
        Remove any matching local triples from the given graph. This only works
        for normal URIs and not with BNodes.
        
        ``graph`` - remove triples matching this graph
        """        
        g = self.graph
        g -= graph.graph
        
        self._is_modified = True
        
        if commit:
            self.commit()

    def atomic_operations(self, ops):
        """
        Executes multiple operations on the graph within one version.
        
        ``ops`` - a list of (operation type, graph)-tuples, where operation
                  type is either remove, update or append and graph is 
                  the corresponding graph to use for the operation.
        """
        for (op_type, input_graph) in ops:
            try:
                f = getattr(self, op_type)
                f(input_graph, commit=False)
            except Exception, e:
                self.rollback()
                raise

        self._is_modified = True
        self.commit()                

    def update_ttl(self, ttl):
        """
        Method wrapping the ``ttl``-attribute
        """
        self.ttl = ttl
        
    def rollback(self):
        """
        Rolls back any changes of the internal graph to the state of the last
        commit. 
        """
        # a rollback is basically done by parsing the serialized graph
        # i.e. the _data, this can be done until a commit has been performed
        # self._graph = self.graph
        
        # is this enough? Next time data is read, it will returned the old
        # graph
        # next time the graph-attribute is accessed it will be re-parsed
        # from data since _graph is None
        self._is_modified = False
        self._graph = None
        
    def commit(self):   
        self._version += 1
        self._is_modified = True

    def __repr__(self):
        no_repr = ['serialized', 'graph']
        
        return "<%s(%s, %s, %s)>" % (self.__class__.__name__, self.name, self.ttl, self.version)
        
        #return "<%s(%s)>" % (self.__class__.__name__, ', '.join(["%s: %s" % (attr, getattr(self, attr)) for attr in dir(self) if not attr.startswith('_')]))
        
class FileGraph(Graph):
    """
    A ``FileGraph`` extends the ``Graph`` with a ``path``-attribute indicating
    a file which contains the graph. The path is complementary to the
    ``serialized``-attribute. That means, that when the graph is committed, the
    file is updated to reflect the new graph.
    """

    def __init__(self, name, path, read_only=True, uri=None, ttl=None, baseuri='http://example.org/'):
        """
        Reads the graph from the given path. When ``read_only`` is False, any
        changes to the graph are written back to the file on graph commit.
        Default is True to avoid unpleasant surprises.
        
        ``path`` - a file-system path where the graph is stored.
        ``read_only`` - indicates if changes to the graph should be written back
                        to the file on commit.
        """
        
        # absolute path where the data of the graph is accessible
        if not os.path.exists(path):
            raise IOError(2, "No such file or directory: '%s'" % path)

        self._path = path
        self.__read_only = read_only
        
        # The serialized data is None since we use the file to read in the 
        # graph
        Graph.__init__(self, name, None, uri=uri, ttl=ttl, baseuri=baseuri)
        
    @Property
    def path():
        """
        Path to where the graph is stored.
        """
        def fget(self):
            return self._path
    
    @Property
    def serialized():
        def fget(self):
            if self._data == None:
                g = self.graph
                self._data = g.serialize()

            return Graph.serialized.fget(self)
                                  
    @Property
    def graph():
        """
        The graph attribute reads in a graph defined by the path.
        """
        def fget(self):
            if self._graph != None:
                return self._graph

            # serialize the graph
            self._graph = RDFLibGraph()
        
            format = 'n3'        
            f = open(self.path)
        
            s = f.readline()
            if s.startswith('<'):
                format = 'xml'
        
            f.seek(0)
        
            try:
                self._graph.parse(f, publicID=self.uri, format=format)
                self._is_modified = True
            except Exception, e:
                raise e

            return self._graph

    def commit(self):
        self._is_modified = True
        if not self.__read_only:
            f = file(self._path, 'w+')
            f.write(self.serialized)
            f.close()
            
        # commit the normal graph, this will set self._is_modified which
        # results in that self.serialized lets rdflib serialize the graph
        # again, FIXME: ignore this for now...    
        Graph.commit(self)
        
class VersionedGraph(Graph):
    """
    Version graphs are reflecting persistent state of a Graph stored in a 
    version store.
    
    Extends the attributes from ``stellaris.graph.Graph`` with:
    
    ``version`` - The latest version of the graph.
    """

    def __init__(self, path, version_sep='+'):
        """
        Each versioned graph is stored in a separate directory. The given path
        should include the directory and the file-name of the graph.
        
        ``path`` - Full path to where the graph is or should be stored.
        """
        if not os.path.exists(path):
            # create the directory
            os.makedirs(os.path.dirname(path))
            f = file(path,'w')
            f.write('')
            f.close()
            
        self._path = path
        
        self.__version_sep = version_sep
        Graph.__init__(self, path, None)

        self.__pending_ops = False
        
        # the first in the list of versions is the latest available
        try:
            self.version = sorted([int(v[v.find(self.__version_sep)+1:]) for v in os.listdir(os.path.dirname(self._path)) if v.find(self.__version_sep) > -1], reverse=True)[0]
        except Exception, e:
            # no previous versions
            self.version = 0
        
    @Property
    def name():
        """
        The name is derived from the path.
        """
        def fget(self):
            return decode(os.path.basename(self._path))

        def fset(self, val):
            self._name = val

    @Property
    def graph():
        """
        Extends the normal Graph by tracking updates via versions.
        """
        def fget(self):
            return Graph.graph.fget(self)
        
        def fset(self, graph):
            # this replaces the current graph
            self._graph = graph.graph
            
            # the version path is the next version
            version_path = '%s%s%s' % (self._path, self.__version_sep, self.version+1)
            f = file(version_path, 'w')
            
            # the destination makes serialize to flush to disk during
            # write, saving memory
            self._graph.serialize(destination=f, format='xml')
            f.close()

            try:
                os.symlink(version_path, self._path)
            except OSError, e:
                # 17 == file exists
                if e.errno == 17:
                    # remove the previous symlink and try again
                    os.unlink(self._path)
                    os.symlink(version_path, self._path)
            
            # everything is done, update the version    
            self.version += 1

    def __eq__(self, other):
        if self.graph.isomorphic(other.graph) and self.version == other.version:
            return True
        
        return False

    def update(self, graph, commit=False):
        # perform the updates on the local instance
        Graph.update(self, graph)
        # now do an assignment to the RDFLib graph in order to write down the
        # new version to disk. If anything goes wrong here, we can still roll
        # back to the old version.
        self.__pending_ops = True        
        if commit:
            self.commit()

    def replace(self, graph, commit=False):
        Graph.replace(self, graph)
        self.__pending_ops = True        
        if commit:
            self.commit()

    def append(self, graph, commit=False):
        Graph.append(self, graph)
        self.__pending_ops = True        
        if commit:
            self.commit()
        
    def remove(self, graph, commit=False):
        Graph.remove(self, graph)
        self.__pending_ops = True        
        if commit:
            self.commit()
        
    def delete(self):
        # simply remove the symlink to the latest version
        os.unlink(self._path)

    def rollback(self, version):
        # reset the version 
        self.version = version
        self.__pending_ops = False        
        
    def commit(self):
        # commit the all changes that have been performed until the current
        # state
        if self.__pending_ops:
            self.graph = self
