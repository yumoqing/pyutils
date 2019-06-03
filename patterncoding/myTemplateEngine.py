import os
import sys
import appPublic.myjson as json
from jinja2 import Environment,FileSystemLoader
import codecs
from appPublic.argsConvert import ArgsConvert
from appPublic.Singleton import SingletonDecorator,GlobalEnv
from appPublic.dictObject import DictObject
def isNone(obj):
	return obj is None

def recordFind(lst,dic):
	ret = []
	for r in lst:
		f = True
		for k in dic.keys():
			if r.get(k,False) != dic.get(k):
				f = False
		if f:
			ret.append(r)
	return ret


class MyTemplateEngine:
	def __init__(self,pathList,file_coding='utf-8',out_coding='utf-8',getGlobal=GlobalEnv):
		self.file_coding = file_coding
		self.getGlobal = getGlobal
		self.out_coding = out_coding
		loader = FileSystemLoader(pathList, encoding=self.file_coding)
		self.env = Environment(loader=loader)	
		self._setDefault_()

	def set(self,n,v):
		# self.env.globals.update({n:v})
		tenv = self.getGlobal()
		tenv[n] = v
		#print('MyTemplateEngine.py,set(),tenv=',tenv)
	
	def _setDefault_(self):
		self.set('json',json)
		self.set('hasattr',hasattr)
		self.set('int',int)
		self.set('float',float)
		self.set('str',str)
		self.set('type',type)
		self.set('isNone',isNone)
		self.set('len',len)
		self.set('recordFind',recordFind)
		self.set('render',self.render)
		self.set('renders',self.renders)
		self.set('ArgsConvert',ArgsConvert)
		self.set('renderJsonFile',self.renderJsonFile)
		self.set('ospath',lambda x:os.path.sep.join(x.split(os.altsep)))
		self.set('basename',lambda x:os.path.basename(x))
		self.set('basenameWithoutExt',lambda x:os.path.splitext(os.path.basename(x))[0])
		self.set('extname',lambda x:os.path.splitext(x)[-1])
	def _setEnv(self):
		tenv = self.getGlobal()
		self.env.globals.update(tenv)
		
	def _render(self,template,data):
		self._setEnv()
		uRet = template.render(**data)
		return uRet.encode(self.out_coding)
		
	def renders(self,tmplstring,data):
		def getGlobal():
			return data
		self.set('global',getGlobal)
		template = self.env.from_string(tmplstring)
		return self._render(template,data)

	def render(self,tmplfile,data):
		def getGlobal():
			return data
		self.set('global',getGlobal)
		template = self.env.get_template(tmplfile)
		return self._render(template,data)

	def renderJsonFile(self,tmplfile,jsonfile):
		f = codecs.open(jsonfile,"r",self.file_coding)
		data = json.load(f)
		f.close()
		return self.render(tmplfile,data)

		
