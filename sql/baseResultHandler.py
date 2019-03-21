
class BaseResultHandler(object):
	def __init__(self,desc,cur,NS):
		self.desc = desc
		self.NS = NS
	
	def __call__(self,cur):
		pass

