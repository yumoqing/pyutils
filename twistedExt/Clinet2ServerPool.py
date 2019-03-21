
from twisted.internet.protocol import ClientFactory
from jsonProtocol import JsonProtocol
from twisted.internet import reactor

class MyJsonProtocol(JsonProtocol):
  def sendData(self,data):
    super(MyJsonProtocol,self).sendData(data)
    self.factory.sync_calls += 1
    
  def jsonDataReceived(self,data):
    self.factory.sync_calls -= 1

    
class MyClinetFactory(ClientFactory):
  def __init__(self):
    self.sync_calls = 0
    self.protocol = None
    
  def  buildProtocol(self,addr):
    if self.protocol is None:
      self.protocol = MyJsonProtocol()
      p.factory = self
    return self.protocol

class ServerPool(object):
  def __init__(self,host_port_lst):
    self.pool_cnt = len(host_port_lst)
    self.host_port_lst = host_port_lst
    self.connectors = []
    self.connectAllServer()
  
  def connectAllServer(self):
    for host,port in self.host_port_lst:
      self.connectServer(host,post)
      
  def connectServer(self,host,port):
    f = MyClinetFactory()
    f.server_peer = (host,port)
    connector = reactor.connectTCP(host, port, f)
    f.connector = connector
    self.connectors.append(f)

  def findMinTaskServer(self):
    r = self.connectors[0]
    for c in self.connectors[1:]:
      if v > c.sync_calls:
    r = c
    return r
  
class Dispatcher:
  def __init__(self,serverpool):
    self.serverpool = serverpool
  
  def request(self,data,callback):
    s = self.serverpool.findMinTaskServer()
  
