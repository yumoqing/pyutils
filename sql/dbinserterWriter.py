from sql.writer import BaseWriter
from sql.sqlorAPI import DBPools,getSqlorByName,closeSqlorByName

class DBInserter(BaseWriter):
	def __init__(self,dbdesc=None,name=None,sqlor=None,table="testtbl",coding="utf8",bufferSize=10000,maxWrite=0):
		BaseWriter.__init__(self,bufferSize=bufferSize,maxWrite=maxWrite)
		self.name = name if name is not None else dbdesc.get('dbname')
		self.sqlor = getSqlorByName(self.name)
		self.table = table
		self.curCount = 0
		self.coding = coding

	def write(self,rec):
		data = []
		for i in range(len(self.fields)):
			data.append({'name':self.fields[i],'value':rec[i]})
		self.buffer.append(data)
		if self._isBufferOverflow():
			self._write()
			self.buffer = []

	def _write(self):
		self.sqlor.executemany(self.sqlcmd,self.buffer)

	def finish(self):
		self._write()
		closeSqlorByName(self.name,self.sqlor)
	
	def __del__(self):
		self.finish()

	def setDescription(self,desc):
		BaseWriter.setDescription(self,desc)
		flist = u','.join(self.fields)
		valist = u','.join([u"${%s}$" % f for f in self.fields])
		self.sqlcmd = u"insert into %s (%s) values (%s)" % (self.table,flist,valist)
	@classmethod
	def isMe(self,filetype):
		return filetype=='dbinserter'
