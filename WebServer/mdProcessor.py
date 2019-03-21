from appPublic.jsonConfig import getConfig
from WebServer.configuredResource import BaseProcessor
from WebServer.globalEnv import request2ns,absUrl

class MarkDownProcessor(BaseProcessor):
	@classmethod
	def isMe(self,name):
		return name=='md'
		
	content_type='webwidget/json'

	def fileHandle(self,f,request):
		b = f.read()
		ret = {
				"__widget__":"markdown",
				"data":{
					"md_text":b
				}
		}
		self.file_data = ret
		return self.file_data
	
