from twisted.internet import reactor,defer
from twisted.web.client import getPage
from twisted.internet import threads
import time

class Synchronize:
	def __init__(self,func,*args,**kwargs):
		self.called = False

	def call_func(self,*args,**kwargs):
		print('call_func called')
		self.retvalue =  self.func(*args,**kwargs)
		self.called = True
		return self.retvalue

	def wait(self):
		while not self.called:
			print('waiting....')
			time.sleep(0.1)
		return self.retvalue


if __name__ == '__main__':
	
	def printPage(d):
		print('page body=',d)
		return d
	
	def getweb():
		d = threads.deferToThread(getPage,b'https://www.baidu.com')
		#d.addCallback(printPage)
		#return d
		s = Synchronize(printPage)
		d.addCallback(s.call_func)
		x = s.wait()
		print(x)
		reactor.stop()

	reactor.callLater(1,getweb)
	reactor.run()
	
