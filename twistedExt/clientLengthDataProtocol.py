from lengthDataProtocol import LengthDataProtocol
from twisted.internet.protocol import ClientFactory,ClientCreator
from twisted.internet import reactor,defer

class MyFactory(ClientFactory):
  def buildProtocol(self,addr):
  	p = LengthDataProtocol()
  	p.factory = self
  	return p

def sendData(p):
  p.sendData('123456789')
  p.sendData('yyyyyyyyyyy12345')
  #p.lostConnect()

a = reactor.connectTCP('localhost',80,MyFactory())
a.factory.newconnect = sendData
reactor.run()
