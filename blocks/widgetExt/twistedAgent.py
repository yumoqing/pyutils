import sys
sys.path.append('..')
import twistedplugin
import time

import threading

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
import urllib

from kivy.network.urlrequest import UrlRequest
from dataloader import DataLoader

class BodyHandler(Protocol):
	def __init__(self,instance,finished):
		self.finished = finished
		self.recved_buf = b''

	def dataReceived(self,data):
		self.recved_buf = self.recved_buf + data

	def connectionLost(self,reason):
		self.finished.callback(self.recved_buf)

class HttpDataLoader(DataLoader,threading.Thread):
	def __init__(self):
		super(HttpDataLoader,self).__init__()
		

	def run(self):
		req_data=urllib.parse.urlencode(self.params)
		url = self.url.encode('utf8') if not isinstance(self.url,bytes) else self.url
		agent = Agent(reactor)
		d = agent.request(self.method,url)
		d.addCallback(self.requestOK)
		d.addErrback(self.requestError)
		
	def loadData(self,url,method=b'GET',params={},headers={}):
		self.url = url
		self.method = method
		self.params = params
		self.headers = headers
		self.start()
		self.join()
		print('joined')
		while not hasattr(self,'result'):
			time.sleep(0.1)
		return self.result

	def requestOK(self,response):
		finished=Deferred()
		finished.addCallback(self.dataLoaded)
		response.deliverBody(BodyHandler(self,finished))
		return finished

	def dataLoaded(self,d):
		super(HttpDataLoader,self).dataLoaded(d)
		self.result = d

	def requestError(self,e):
		self.loadError(e)

if __name__ == '__main__':
	import sys
	from kivy.app import App
	from kivy.uix.boxlayout import BoxLayout
	from kivy.uix.button import Button
	from kivy.uix.textinput import TextInput
	class MyApp(App):
		def build(self):
			root = BoxLayout(orientation='vertical')
			btn = Button(text='get Remote data',size_hint_y=None,height=44)
			btn.bind(on_release=self.getData)
			root.add_widget(btn)
			self.txt = TextInput(multiline=True,readonly=True)
			root.add_widget(self.txt)
			return root
		def getData(self,btn):
			url = sys.argv[1] if len(sys.argv)>1 else 'https://www.baidu.com'
			hdl = HttpDataLoader()
			hdl.bind(on_loaded=self.showData)
			hdl.loadData(url)

		def showData(self,instance,x):
			self.txt.text = x
	MyApp().run()
