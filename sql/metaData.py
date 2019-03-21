class MetaData(object):
	def _setDefault(self,data,key):
		meta = self.getMeta(key)
		if meta is not None:
			data.update(meta)
		return data
	
	def setDefault(self,data,key):
		if type(data) == type({}):
			return self._setDefault(data,key)
		return data
		
	def getMeta(self,key):
		pass