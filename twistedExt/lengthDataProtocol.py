import string
from twisted.internet.protocol import Protocol
from twisted.internet import defer
class LengthDataProtocol(Protocol):
  """
  transfered data hass format:data length in string,followed by a newline and data body total length indicated above.
  like:11\n\rqqqqqqqqqqq
  so it has two state:"readLenth",and "readBody"
  """
  delimiter='\r\n'
  def connectionMade(self):
    a = self.transport.getPeer()
    #print( a,type(a),dir(a))
    self.databuf = ''
    self.state = "readLength"
    self.dataLen = -1
    self.stopParse = False
    if hasattr(self,'factory'):
      if hasattr(self.factory,'newconnect'):
        self.factory.newconnect(self)
		
  def sendData(self,data):
    self.transport.write("%d%s%s" % (len(data),self.delimiter,data))

  def lengthDataReceived(self,data):
    print( data)

  def parseData(self):
    if self.state == "readLength":
      lines = self.databuf.split(self.delimiter,1)
      if len(lines) > 1:
	self.dataLen = string.atoi(lines[0])
	self.databuf = lines[1]
	self.state = 'readBody'
      else:
	self.stopParse = True

    if self.state == 'readBody':
      if self.dataLen <= len(self.databuf):
	lengthData = self.databuf[:self.dataLen]
	self.databuf = self.databuf[self.dataLen:]
	self.state = 'readLength'
	self.lengthDataReceived(lengthData)
      else:
	self.stopParse = True

  def dataReceived(self,data):
    self.databuf = self.databuf + data
    self.stopParse = False
    while (not self.stopParse):
      self.parseData()

def readyjob(protocol):
	print( "server is ready")
	
if __name__ == '__main__':
  from twisted.internet.protocol import Factory
  from twisted.internet import reactor
  
  class MyLengthDataProtocol(LengthDataProtocol):
    def lengthDataReceived(self,data):
      self.sendData(data)

  class MyFactory(Factory):
  		
    def buildProtocol(self,addr):
      p = MyLengthDataProtocol()
      p.factory = self
      return p
			
  f = MyFactory()
  #f.newconnect = readyjob
  r = reactor.listenTCP(80,f)
  print( type(r),type(r.factory))
  print( r)
  print( dir(r))
  reactor.run()
