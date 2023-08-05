import sys, httplib2

def delete(remotehost, context):
    h = httplib2.Http()
       
    resp_del, content_del = h.request(remotehost + '/context/' + context, 'DELETE')
        
    return (resp_del, content_del)

def main():
    host = "http://astrogrid.aei.mpg.de:52540"
    
    delete(host, sys.argv[1])
    
if __name__ == '__main__':
    main()
