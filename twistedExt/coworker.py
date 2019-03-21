
import threading.Semaphore as BoundedSemaphore
import time

class CocurrencyCallClient:
  def __init__(self,max_call,servers):
    self.sem = BoundedSemaphore(max_call)
    self.servers = servers
    self.SN = 0
    self.calling = {}
    self.serverConnected = {}
    
  def connectServer(self):
    for host,port in self.servers:
      a = dict(host=host,port=port,proto=proto)
      k = host + '_' + str(port)
      self.serverConnected[k] = a
      
  def setMaxCall(self,cnt):
    self.sem.close()
    self.sem = Semaphore(cnt)
  
  def sendData(self,info):
  	info['server'].sendData(info['request'])
  	  
  def call(self,data):
    self.sem.acquire()
    package = dict(sn=self.SN,data=data)
    server = self.getServer()
    info = dict(begin=time.time(),request=data,server=server)
    self.calling[self.SN] = info
    self.SN += 1
    self.sendData(package,info)
    
  def callback(self,data):
    self.sem.release()
    