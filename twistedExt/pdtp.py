# pdtp.py
# python data transition protocol
# base on line protocol
# it use pickle package to serialize and unserialize python data
# and use a line only contains the serialized data length string. follows by the serialized data

import string
from twisted.protocols.basic import LineReceiver
import pickle

class PyDataP(LineReceiver):
	delimiter='\r\n'
	
	def constructPyData(self):
		if self.step == 'readline':
			lines = self.databuf.split(self.delimiter,1)
			if len(lines) < 2:
				return
			line = lines[0]
			#print "line=",line,":end",len(self.databuf)
			self.datalen = string.atoi(line)
			self.step = 'readraw'
			self.databuf = lines[1]
		if self.step == 'readraw':
			if self.datalen <= len(self.databuf):
				pd = self.doUnpickle(self.databuf[:self.datalen])
				#print "pydata=",pd
				self.pyDataReceived(pd)
				self.databuf = self.databuf[self.datalen:]
				self.step = 'readline'
				self.constructPyData()
		#print "end"
			
	def rawDataReceived(self,data):
		self.databuf = self.databuf + data
		self.constructPyData()
			
	def doUnpickle(self,pickled):
		return pickle.loads(pickled)
	
	def doPickle(self,data):
		return pickle.dumps(data)
		
	def pyDataReceived(self,pd):
		pass
	
	def sendPyData(self,pd):
		d = self.doPickle(pd)
		buf = "%d%s%s" % (len(d),self.delimiter,d)
		self.transport.write(buf)
		
	def connectionLost(self, reason):
		pass
	
	def connectionMade(self):
		a = self.transport.getPeer()
		#print a,type(a),dir(a)
		self.databuf = ''
		self.step = 'readline'
		self.setRawMode()
