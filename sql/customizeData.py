
class CustomizeData(object):
	def _setCustomize(self,data,key,attributes):
		cust = self.getCustomize(key)
		if cust is None:
			return
		for a in attributes:
			if a in cust.keys():
				data[a] = meta[a]
		return data
	
	def setCustomize(self,data,key,attributes):
		if type(data) == type([]):
			return [self._setCustomize(d,key,attributes) for d in data]
		if type(data) == type({}):
			return self._setCustomize(data,key,attributes)
		return data
		
	def getCustomize(self,key):
		pass