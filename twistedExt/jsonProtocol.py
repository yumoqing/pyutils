from lengthDataProtocol import LengthDataProtocol
#from appPublic.json import jsonDecode,jsonEncode
from ujson import dumps,loads

class JsonProtocol(LengthDataProtocol):
  def lengthDataReceived(self,data):
    d = loads(data)
    self.jsonReceived(d)

  def jsonReceived(self,d):
    print( d)

  def sendData(self,data):
    json = dumps(data)
    LengthDataProtocol.sendData(self,json)

if __name__ == '__main__':
  from twisted.internet.protocol import Factory
  from twisted.internet import reactor

  class MyJsonProtocol(JsonProtocol):
    def jsonReceived(self,data):
      self.sendData(data)

  class MyFactory(Factory):
    def buildProtocol(self,addr):
      p = MyJsonProtocol()
      p.factory = self
      return p

  f = MyFactory()
  r = reactor.listenTCP(80,f)
  reactor.run()
