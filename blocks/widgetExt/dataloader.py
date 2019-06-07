from kivy.event import EventDispatcher

class DataLoader(EventDispatcher):
	def __init__(self,**kw):
		self.register_event_type('on_loaded')
		super(DataLoader,self).__init__(**kw)
	
	def loadData(self):
		pass
	def asyncLoad(self):
		pass
		
	def dataLoaded(self,d):
		self.dispatch('on_loaded',d)
		
	def on_loaded(self,d):
		pass #print('on_loaded,data=',d)

	def loadError(self,e):
		self.dispatch('on_loaderror',e)
		raise e

	def on_loaderror(self,a,e):
		pass #print('error:',e)
