import httplib2, sys

class UploadRDF:

    def __init__(self, host):
        self.host = host + '/context/'
        
    def readdata(self, path):
        f = open(path)

        s = []
    
        for l in f:
            s.append(l)
    
        return "".join(s)

    def upload(self, path, uri):
        h = httplib2.Http()
        data = self.readdata(path)
        
        headers = {'content-type':'application/rdf+xml'}
        resp_put, content_put = h.request(uri, 'PUT', 
                                  body=data,headers=headers)
        
        return (resp_put, content_put)
        
def main():
#    uRDF = UploadRDF("http://astrogrid.aei.mpg.de:52542")
    uRDF = UploadRDF("http://localhost:24000")    
    uRDF.upload(sys.argv[1], sys.argv[2])
    
if __name__ == '__main__':
    main()
