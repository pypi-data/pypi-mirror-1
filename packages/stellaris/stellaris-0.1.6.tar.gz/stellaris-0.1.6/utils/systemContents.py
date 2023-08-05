import httplib2, sys

class SystemContents:

    def __init__(self, host):
        self.host = host + '/context/'
        
    def readdata(self, path):
        f = open(path)

        s = []
    
        for l in f:
            s.append(l)
    
        return "".join(s)

    def head(self, uri):
        h = httplib2.Http()
        
        headers = {}
        resp, content = h.request(uri, 'HEAD', 
                                  headers=headers)
        
        return (resp, content)
        
def main():
#    uRDF = UploadRDF("http://astrogrid.aei.mpg.de:52542")
    uRDF = SystemContents("http://localhost:24000")    
    print (uRDF.head(sys.argv[1]))
    
if __name__ == '__main__':
    main()
