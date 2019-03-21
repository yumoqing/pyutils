from jsonProtocol import JsonProtocol
from twisted.internet.protocol import ClientFactory,ClientCreator
from twisted.internet import reactor,defer

class MyFactory(ClientFactory):
  def buildProtocol(self,addr):
  	p = JsonProtocol()
  	p.factory = self
  	return p

def sendData(p):
  p.sendData({'a':1234,'b':1,'c':'24e45f'})
  p.sendData({'a':1234,'b':1,'c':'24e45f'})
  p.sendData({'a':1234,'b':1,'c':'24e45f'})
  p.sendData({'a':1234,'b':1,'c':'24e45f'})
  p.sendData({'a':1234,'b':1,'c':'24e45f'})

a = reactor.connectTCP('localhost',80,MyFactory())
a.factory.newconnect = sendData
reactor.run()
