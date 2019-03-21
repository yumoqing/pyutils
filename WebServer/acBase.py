# coding: utf-8

import traceback
import copy

from twisted.web.server import Session,Site
from twisted.python.components import registerAdapter
from twisted.python import components, filepath, log
from twisted.web.resource import Resource
from twisted.web import resource,static
from zope.interface import Interface, Attribute, implements,implementer
from appPublic.jsonConfig import getConfig
from appPublic.rsa import RSA
from WebServer.globalEnv import UserNeedLogin,WebsiteSessiones

class NotImplementYet(Exception):
    pass

class RefusedResource(Resource):
	def render(self,request):
		return request.path + b':refused access!'

class UnknownException(Resource):
	def __init__(self,e,*args,**kwargs):
		super(UnknownException,self).__init__(*args,**kwargs)
		self.e = e
		
	def render(self,request):
		print('Exception.....!',request.path,'exception=',self.e,'type e=',type(self.e))
		return request.path + b':exception happend'
		
class ACBase:
	"""
	网站访问控制基本类
	需要继承此类，并实现checkPassword，和checkUserPrivilege两个函数
	使用例子：
	class MyAC(ACBase):
		def checkPassword(self,user,password):
			myusers= {
				'root':'pwd123'
				'user1':'pwd123'
			}
			p = myusers.get(user,None)
			if p == None:
				return False
			if p != password:
				return False
			return True
		def checkUserPrivilege(self,user,path):
			# 用户可以做任何操作
			return True
		
	在需要控制的地方
	ac = MyAC()
	if not ac.accessCheck(request):
		#拒绝操作
	# 正常操作
	"""
	def __init__(self):
		self.conf = getConfig()
		self.rsaEngine = RSA()
		fname = self.conf.website.rsakey.privatekey
		self.privatekey = self.rsaEngine.read_privatekey(fname,'ymq123')
		
	def _selectParseHeader(self,authheader):
		txt = self.rsaEngine.decode(self.privatekey,authheader)
		return txt.split(':')
		
	def checkUserPrivilege(self,user,path):
		raise NotImplementYet

	def checkPassword(self,user,password):
		raise NotImplementYet
		
	def getRequestUserPassword(self,request):
		try:
			authheader = request.getHeader(b'authorization')
			if authheader is not None:
				return self._selectParseHeader(authheader)
			return None,None
		except Exception as e:
			return 'Anonymous',None

	def isNeedLogin(self,path):
		raise NotImplementYet
		
	def acCheck(self,request):
		path = request.path
		ws = WebsiteSessiones()
		user =  ws.getUserid(request)
		if user == None:
			user,password = self.getRequestUserPassword(request)
			if user is None:
				raise UserNeedLogin(path)
			if not self.checkPassword(user,password):
				raise UserNeedLogin(path)
			ws.login(request,user)
	
		if not self.checkUserPrivilege(user,path):
			raise UnauthorityResource()
		return True
		
	def accessCheck(self,request):
		"""
		检查用户是否由权限访问此url
		"""
		if self.isNeedLogin(request.path):
			# print('need login')
			return self.acCheck(request)
		#没在配置文件设定的路径不做控制，可以随意访问
		# print('not need login')
		return True
        
class BaseResource(static.File):
	def __init__(self,path,accessController=None, defaultType="text/html", ignoredExts=(), registry=None, allowExt=0):
		super(BaseResource,self).__init__(path)
		self.newProcessors = {}
		self.access_controller = accessController

	def getChild(self,path,request):
		if isinstance(path, bytes):
			try:
				# Request calls urllib.unquote on each path segment,
				# leaving us with raw bytes.
				path = path.decode('utf-8')
			except UnicodeDecodeError:
				log.err(None,
					"Could not decode path segment as utf-8: %r" % (path,))
				return self.childNotFound

		self.restat(reraise=False)

		if not self.isdir():
			return self.childNotFound

		if path:
			try:
				fpath = self.child(path)
			except filepath.InsecurePath:
				return self.childNotFound
		else:
			fpath = self.childSearchPreauth(*self.indexNames)
			if fpath is None:
				return self.directoryListing()

		if not fpath.exists():
			fpath = fpath.siblingExtensionSearch(*self.ignoredExts)
			if fpath is None:
				return self.childNotFound
		

		if self.access_controller is not None:
			# print('here --------------')
			try:
				if not self.access_controller.accessCheck(request):
					# print('Refused REsource')
					return RefusedResource()
			except UserNeedLogin as e:
				return e
			except Exception as e:
				traceback.print_exc()
				return UnknownException(e)
		
		for k in self.newProcessors.keys():
			if fpath.path.endswith(k):
				processor = self.newProcessors.get(k)
				if processor:
					return resource.IResource(processor(fpath.path, self.registry))
		return self.createSimilarFile(fpath.path)

	def createSimilarFile(self, path):
		f = self.__class__(path, accessController=self.access_controller)
		f.newProcessors = self.newProcessors
		f.indexNames = self.indexNames[:]
		f.childNotFound = self.childNotFound
		return f
	
