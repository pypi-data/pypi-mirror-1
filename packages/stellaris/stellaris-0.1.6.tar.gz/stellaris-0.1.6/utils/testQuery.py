from rdflib import ConjunctiveGraph, plugin
from rdflib.store import Store
from StringIO import StringIO

test_data = """ 
@prefix foaf:       <http://xmlns.com/foaf/0.1/> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

_:a  foaf:name       "Alice" .
_:b  foaf:name       "Bob" .
_:c  foaf:name       "Charlie" .
_:d  foaf:name       "David" .
_:e  foaf:name       "Eve" .
"""

test_query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX ex: <http://ns.example.org/#>

SELECT ?name ?x

WHERE { ?x foaf:name ?name . }
ORDER BY ?name
"""

graph = ConjunctiveGraph(plugin.get('IOMemory',Store)())
graph.parse(StringIO(test_data), format="n3")
results = graph.query(test_query)

print results.serialize(format='json')
