# Concurrent.py 
from twisted.internet import reactor
from twisted.python.threadpool import ThreadPool
from threading import RLock

class Concurrent:
	def __init__(self,reactor,callee,finishcall=None,minth=10,maxth=20):
		self.thpool = ThreadPool(minthreads=minth, maxthreads=maxth)
		self.callee = callee
		self.finishcall = finishcall
		self.customcall = None
		self.cnt = 0
		self.total = 0
		self.reactor = reactor
		self.mutex = RLock()
		self.reactor.addSystemEventTrigger('after', 'shutdown', self.thpool.stop)
		self.thpool.start()
		self.execlog = []
		self.lastTaskcnt = 0
		self.dummyTerm = 0
		
	def enableLog(self):
		self.reactor.callLater(2,self.log)
		
	def setCustomFunc(self,func):
		self.customcall = func
		
	def log(self):
		print('Concurrent log: total=',self.total,'concurrent cnt=',self.cnt)
		if self.customcall is not None:
			self.customcall(self)
		self.reactor.callLater(10,self.log)
		
	def _callee(self,*args,**kwarg):
		# print('self.total=',self.total,'self.cnt=',self.cnt)
		self._bc()
		try:
			self.callee(*args,**kwarg)
		except Exception as e:
			print('Concurrent exception:',e)
		self._ec()
		
	def _bc(self):
		if self.mutex.acquire():
			self.cnt += 1
			self.total += 1
			r = self.mutex.release()
	
	def _chkEnd(self):
		if self.cnt <= 0:
			if self.finishcall is not None:
				self.finishcall()
			
	def _ec(self):
		if self.mutex.acquire():
			self.cnt -= 1
			r = self.mutex.release()
			if self.cnt <= 0 and self.total>0:
				self._chkEnd()
		
	def __call__(self,*args,**kwarg):
		self.thpool.callInThread(self._callee,*args,**kwarg)
		
if __name__ == '__main__':
	import time
	def c(cc,i):
		d = i % 3
		print('haha',d,i,cc.cnt)
		if d==0:
			raise Exception('No:%d,curr %d exception' % (cc.total,cc.cnt))
		time.sleep(d)
		
	def stop():
		reactor.stop()
	
	cc = Concurrent(reactor,c,stop)
	cc.enableLog()
	for i in range(4000):
		cc(cc,i)
	reactor.run()
	print(cc.total,' run')
