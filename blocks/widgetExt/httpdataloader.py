import sys
sys.path.append('..')
import time
import requests
import twistedplugin
import time

import threading

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent
import urllib

from kivy.network.urlrequest import UrlRequest
from .dataloader import DataLoader

class HttpDataLoader(DataLoader):
	def __init__(self):
		super(HttpDataLoader,self).__init__()
		
	def loadData(self,url,method='GET',params={},headers={}):
		try:
			resp = None
			if method=='GET':
				resp = requests.get(url,params=params,headers=headers)
			else:
				resp = requests.post(url,data=params,headers=headers)
			if resp.status_code == 200:
				#print('return 200 fffffffffffff,type of response.text=',type(resp.text))
				text = resp.text.encode(resp.encoding).decode('utf8')
				self.dataLoaded(text)
				return text
			else:
				return ''
		except Exception as e:
			print('loadData(%s) Error ' % url,e)
			raise e
			self.loadError(e)

	def aysncLoad(self,url,method='GET',params={},headers={}):
		d = defer.maybeDeferred(self.loadData,url,method=method,params=params,headers=headers)
		d.addCallback(self.dataLoaded)
		d.addErrback(self.loadError)
		

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
