# acResource.py
from twisted.internet import reactor
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource
class AuthorityControler:
	def check(self,request):
		return True

class  AuthorityControlResource(Resource):
	"""
	this resource is the same as Resource, only add a authority Check if the user as the access rights on the resource
	"""
	def _responseFailed(self, failure, call,request):
		call.cancel()
		raise failure
		
	def render(self,request):
		ac = AuthorityControler()
		if ac.check(request):
			call = reactor.callLater(1, self._render, request)	# referInThread()?
			request.notifyFinish().addErrback(self._responseFailed, call,request)
			return NOT_DONE_YET
		else:
			return AuthorityCheckFailed(request)
	
	def _render(self,request):
		pass