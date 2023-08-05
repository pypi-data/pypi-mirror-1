from rdflib import ConjunctiveGraph, plugin
from rdflib.store import Store
from StringIO import StringIO
import unittest, httplib2, urllib
from testCherryPy import TestCherryPy

test_data = """<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:cactus="http://cactuscode.org/cactus-unit-tests-schema#">
<cactus:Test rdf:about="#myURI" cactus:testID="some test ID with a + char" /> 
</rdf:RDF>
"""

test_query = """PREFIX cactus: <http://cactuscode.org/cactus-unit-tests-schema#>
SELECT ?item
WHERE {
  ?item cactus:testID 'some test ID with a + char' .
}"""

correct = """"name" : {"type": "literal", "xml:lang" : "None", "value" : "Bob"},\n                   "x" : {"type": "uri", "value" : "http://example.org/bob"}\n                }"""

class Query(TestCherryPy):

    def testQueryPlus(self):
        data = self.readdata(StringIO(test_data))
        resp_put, content_put = self.insert(data, self.context)
        h = httplib2.Http()
        headers = {}
        headers['content-type'] = 'application/x-www-form-urlencoded'
        q = urllib.quote(test_query)
        print q
        resp_q, content_q = h.request(self.remotehost + '/query/query?query=' +
                                      q, 'GET', headers=headers)

        print content_q
        self.failUnless(content_q.find("#myURI") > -1)
        # success codes: http://rest.blueoxen.net/cgi-bin/wiki.pl?HttpMethods
        # clean up the mess
        (resp_del, content_del) = self.delete(self.context)
        self.failUnless(resp_del['status'] in ['200','202','204'], msg=resp_del['status'])


if __name__ == "__main__":
    unittest.main()
