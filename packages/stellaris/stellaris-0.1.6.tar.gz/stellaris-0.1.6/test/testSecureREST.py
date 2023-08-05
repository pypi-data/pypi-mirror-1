import httplib2, os, unittest

from testCherryPy import TestCherryPy

# an access using a non-ssl connection is forwarded
# to the port of the secure service

# an unauthorized access to the secure service is dropped at the
# ssl-layer and should never be handled by any service resource

# retrieval of a non-public context is forwarded to the secure service
# retrieval is currently public

# A query which is detected to include protected contexts returns
# only public data. To access protected data within contexts, the
# user must use the secure service

class TestSecureREST(TestCherryPy):

    cfg = "./test/https_server.cfg"
    clientcert = os.path.abspath('./test/cert/valid_cert.pem')
    clientkey = os.path.abspath('./test/cert/valid_key.pem')
    invalidcert = os.path.abspath('./test/cert/invalid_cert.pem')
    invalidkey = os.path.abspath('./test/cert/invalid_key.pem')
    noauthcert = os.path.abspath('./test/cert/unauth_cert.pem')
    noauthkey = os.path.abspath('./test/cert/unauth_key.pem')
    cert = clientcert
    key = clientkey
    securehost = 'https://localhost:9020'
    
    def getsecure(self, context):
        h = httplib2.Http()
        
        h.add_certificate(self.key, self.cert, '')
        return h.request(self.securehost + context, 'GET')
    
    def putsecure(self, data, context):
        h = httplib2.Http()
        h.add_certificate(self.key, self.cert, '')        
        headers = {'content-type':'application/rdf+xml'}
        return h.request(self.securehost + context, 'PUT', 
                                  body=data,headers=headers)
        
    def postsecure(self, data, context):
        h = httplib2.Http()
        h.add_certificate(self.key, self.cert, '')        
        headers = {'content-type':'application/rdf+xml'}
        return h.request(self.securehost + context, 'POST', 
                                  body=data,headers=headers)

    def deletesecure(self, context):
        h = httplib2.Http()
        h.add_certificate(self.key, self.cert, '')
        return h.request(self.securehost + context, 'DELETE')
        
    def testConnectValid(self):
        self.cert = self.clientcert
        self.key = self.clientkey
        
        resp, cont = self.getsecure("/")

        self.failUnless(resp['status'] == '200')

    # this creates some ugly exceptions on the server code,
    # have not found a way to catch them yet.
#    def testConnectInvalid(self):
#        h = httplib2.Http(cert_file=self.invalidcert, key_file=self.invalidkey)
#        msg = ""
#        try:
#            resp, content = h.request(self.securehost, 'GET')
#        except Exception, (code, msg):
#            print msg
#            pass

#        self.failUnless(msg == 'EOF occurred in violation of protocol')

    def testPut(self):
        # put with valid user
        self.cert = self.clientcert
        self.key = self.clientkey
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.putsecure(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])

        resp, cont = self.getsecure(self.context)
        print resp, cont
        self.failUnless(resp['status'] == '200')

    def testPutNoAuth(self):
        self.cert = self.noauthcert
        self.key = self.noauthkey
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.putsecure(data, self.context)

        # a user that is not authorized to use the resource
        # should not know about its existence
        self.failUnless(resp_put['status'] == '401', resp_put['status'] + ': ' + content_put)
        
    def testPutRedirect(self):
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.insert(data, self.context)

        # this means that the resource was found at a different URL 
        self.failUnless(resp_put['status'] == '401', resp_put['status'] + content_put)

        self.cert = self.clientcert
        self.key = self.clientkey

        print "Using cert,key, context ", self.cert, self.key, self.context, resp_put
        resp_put, content_put = self.putsecure(data, self.context)
        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])
        
    def testPostNoAuth(self):
        self.cert = self.noauthcert
        self.key = self.noauthkey
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.postsecure(data, self.context)

        # a user that is not authorized to use the resource
        # should not know about its existence
        self.failUnless(resp_put['status'] == '401')

    def testPost(self):
        self.cert = self.clientcert
        self.key = self.clientkey
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.putsecure(data, self.context)

        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])
        
        resp_post, content_post = self.postsecure(data, self.context)

        self.failUnless(self.validStatus(resp_post['status']), msg=resp_post['status'])

    def testPostRedirect(self):
        # first create new data at the context
        self.cert = self.clientcert
        self.key = self.clientkey
        
        data = self.readdata(file('./test/data/add.rdf'))
        resp_put, content_put = self.putsecure(data, self.context)

        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])
            
        # try to post an update
        data = self.readdata(file('./test/data/update.rdf'))
        resp_post, content_post = self.update(data, self.context)

        # this means that the resource was found at a different URL 
        self.failUnless(resp_post['status'] == '401')

        self.cert = self.clientcert
        self.key = self.clientkey
        
        resp_post, content_post = self.postsecure(data, self.context)
        self.failUnless(self.validStatus(resp_post['status']), msg=resp_post['status'])

    def testDeleteNoAuth(self):
        # start by inserting the data using a certified user
        self.cert = self.clientcert
        self.key = self.clientkey
        
        data = self.readdata(open('./test/data/add.rdf'))
        resp_del, content_del = self.putsecure(data, self.context)

        self.failUnless(self.validStatus(resp_del['status']), msg=resp_del['status'])
    
        # init the cert/key and try to remove with an unauthorized user
        self.cert = self.noauthcert
        self.key = self.noauthkey
        
        resp_del, content_del = self.deletesecure(self.context)

        # a user that is not authorized to use the resource
        # should not know about its existence
        self.failUnless(resp_del['status'] == '401', resp_del['status'] + ': ' + content_del)

    def testDelete(self):
        self.cert = self.clientcert
        self.key = self.clientkey

        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.putsecure(data, self.context)

        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])
        
        resp_del, content_del = self.deletesecure(self.context)

        self.failUnless(self.validStatus(resp_del['status']), msg=resp_del['status'])

    def testDeleteRedirect(self):
        self.cert = self.clientcert
        self.key = self.clientkey

        # insert data
        data = self.readdata(open('./test/data/add.rdf'))
        resp_put, content_put = self.putsecure(data, self.context)

        self.failUnless(self.validStatus(resp_put['status']), msg=resp_put['status'])

        resp_del, content_del = self.delete(self.context)

        # this means that the resource was found at a different URL 
        self.failUnless(resp_del['status'] == '401')

        self.cert = self.clientcert
        self.key = self.clientkey
        
        resp_del, content_del = self.deletesecure(self.context)
        self.failUnless(self.validStatus(resp_del['status']), msg=resp_del['status'])
        
if __name__ == '__main__':
#    suite = unittest.TestSuite()
#    suite.addTest(TestSecureREST('testDeleteNoAuth'))
#    suite.addTest(TestSecureREST('testPutNoAuth'))        
#    unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
