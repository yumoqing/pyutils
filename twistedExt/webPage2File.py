import os,sys
from twisted.web import client
from twisted.internet import reactor
def mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        #print( "_mkdir %s" % repr(newdir))
        if tail:
            os.mkdir(newdir)

class WebPage2File:
    def __init__(self,url,filename):
        self.url = url
        self.filename = filename
        pa = os.path.dirname(self.filename)
        mkdir(pa)
    
    def end(self):
        reactor.stop()    
    def __call__(self):
        client.getPage(self.url).addCallback(self.callback).addErrback(self.errback)
        
    def callback(self,data):
        self.data = data
        try:
            # print( self.url, "downloaded")
            f = open(self.filename,"w")
            f.write(data)
            f.close()
            print( self.url,"=>",self.filename)
        except:
            print( self.filename,":open error")
        self.end()
        
    def errback(self,err):
        print( self.url,"download error",err)
        self.end()
        
if __name__ == '__main__':
    if len(sys.argv)<2:
        print( sys.argv[0]," url filename")
        sys.exit(1)
    p2f = WebPage2File(sys.argv[1],sys.argv[2])
    p2f()
    reactor.run()
    print( "Finish!!")
