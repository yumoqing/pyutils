class DictBuffer(object):
	def __init__(self,func,cnt=1000):
		self.cnt = cnt
		self.dictbuf = {}
		self.ref_ = {}
		self.func = func
		
	def __del__(self):
		del self.dictbuf
		del self.ref_
		
	def get(self,key):
		if key not in self.dictbuf.keys():
			v = self.func(key)
			if len(self.dictbuf.keys()) >= self.cnt:
				d = [[k,v] for k in self.ref_]
				sd = sorted(d,key=lambda x:x[1])
				del self.dictbuf[sd[0]]
				del self.ref_[sd[0]]
			self.dictbuf[key] = v
			self.ref_[key] = 0
		data = self.dictbuf.get(key)	
		cnt = self.ref_.get(key,0)
		self.ref_[key] = cnt + 1
		return data
