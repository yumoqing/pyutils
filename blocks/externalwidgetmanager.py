# -*- utf-8 -*-
"""
模板文件以wrdesc结尾
界面描述文件以uidesc结尾
"""
import os
import sys
import codecs

from twisted.internet import defer

from appPublic.folderUtils import ProgramPath,listFile
from appPublic.jsonConfig import getConfig

import json
from widgetExt import HttpDataLoader
from widgetExt import FileDataLoader

def endsWith(s,sub):
	ret = s[len(s)-len(sub):] == sub
	#print(s[len(s)-len(sub):],sub,ret)
	return ret
	
def startsWith(s,sub):
	return s[:len(sub)] == sub
	
class ExternalWidgetManager:
	def __init__(self):
		#self.register_root = os.path.join(ProgramPath(),'widgets')
		#self.ui_root = os.path.join(ProgramPath(),'ui')
		self.ui_root = './ui'
		self.register_root = './widgets'
		
	def loadJson(self,filepath):
		with codecs.open(filepath,'r','utf-8') as f:
			return json.load(f)
	
	def travalRegisterDesc(self,func):
		return
		for f in listFile(self.register_root,suffixs=['wrdesc'],rescursive=True):
			desc = self.loadJson(f)
			return func(desc)
			
	def loadWidgetDesc(self,desc):
		def text2Json(d):
			j = json.loads(d)
			return j

		# print(desc)
		if desc.get('filename'):
			path = desc.get('filename')
			if endsWith(path,'.uidesc'):
				f = FileDataLoader()
				f.bind(on_dataloaded=text2Json)
				if startsWith(path,'/'):
					path = path[1:]
				fn = os.path.join(self.ui_root,path)
				return text2Json(f.loadData(fn))
			raise Exception('file error',path)

		if desc.get('url'):
			url = desc.get('url')
			headers = desc.get('headers',{})
			params = desc.get('params',{})
			http = HttpDataLoader()
			return text2Json(http.loadData(url,params=params,headers=headers))

		raise Exception('ui desc loaded failed' , desc)
	
