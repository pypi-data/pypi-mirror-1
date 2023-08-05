#!/usr/bin/python

from rdflib import plugin
from rdflib.Graph import ConjunctiveGraph
from rdflib.store import Store

import sys
from StringIO import StringIO

def readrdf(path):
    f = open(path)

    s = []

    for l in f:
        s.append(l)

    return "".join(s)

in_data = sys.argv[1]
    
store = plugin.get('IOMemory',Store)()
graph = ConjunctiveGraph(store)
graph.parse(StringIO(readrdf(in_data)), format='n3')
out = graph.serialize()


f = open(in_data.replace('.n3', '.rdf'), "w")

for l in out:
    f.write(l)

