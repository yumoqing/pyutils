import os
import sys
import json
import codecs
import math
from decimal import Decimal
# import xlwt
class BaseWriter(object):
	def __init__(self,bufferSize=10000,maxWrite=0):
		self.buffer = []
		self.bSize = bufferSize
		self.fields = None
		self.notDataReturn = False
		self.field_desc = None
		self.coding = 'utf8'
		self.maxWrite = maxWrite
	
	def getResult(self):
		return None
		
	def __call__(self,cur,namespace={}):
		if cur.description is None:
			return
		#try:
		wrtCnt = 0
		self.setDescription(cur.description)
		r = cur.fetchone()
		while r is not None:
			self.write(r)
			r = cur.fetchone()
			wrtCnt += 1
			if self.maxWrite > 0 and wrtCnt >= self.maxWrite:
				break
		#except Exception as e:
		#	print( "BaseWriter",e)
			
	def setDescription(self,desc):
		if desc is None:
			return 
		self.field_desc = desc
		self.fields = [ i[0].encode(self.coding) if type(i[0])==type(u'') else str(i[0]) for i in desc ]
		self.fields = [ f.lower() for f in self.fields ]

	
	def _isBufferOverflow(self):
		if len(self.buffer) >= self.bSize:
			return True
		return False
	
	def _write(self):
		pass
	
	def _convert2Str(self,rec):
		ret = [i.encode(self.coding) if type(i) == u'' else str(i) for i in rec ]
		return ret
	def finish(self):
		self._write(self)
		
class DataBaseEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj,Decimal):
			return float(obj)
		return json.JSONEncoder.default(self, obj)
		
class JsonWriter(BaseWriter):
	def __init__(self,outfile=None,coding='utf8',maxWrite=0):
		BaseWriter.__init__(self,maxWrite=maxWrite)
		self.outfile = outfile
		self.coding = coding
	
	@classmethod
	def isMe(self,filetype):
		return filetype=='json'
		
	def write(self,rec):
		r = {}
		cnt = len(self.fields)
		[r.update({self.fields[i]:rec[i]}) for i in range(cnt) ]
		self.buffer.append(r)

	def finish(self):
		if self.outfile is None:
			f = sys.stdout
		else:
			f = open(self.outfile,'w')
		json.dump(self.buffer,f,encoding=self.coding,cls=DataBaseEncoder,indent=4)
		f.close()
	
	def __del__(self):
		self.finish()
		
class CSVWriter(BaseWriter):
	def __init__(self,outfile=None,delimiter=',',write_mode='w',coding='utf8',outheader=False,nl='|nl|',bufferSize=10000,maxWrite=0):
		BaseWriter.__init__(self,bufferSize=bufferSize,maxWrite=maxWrite)
		self.outfile = outfile
		self.delimiter = str(delimiter)
		self.outheader=outheader
		self.nl = nl.decode(coding)
		self.write_mode = write_mode
		self.outf = None
		self._openFile()
		self.coding = coding
		self.head = False
	
	@classmethod
	def isMe(self,filetype):
		return filetype=='csv'
	
	def nlReplace(self,s):
		try:
			s = u''.join(s.split(u'\r'))
		except Exception as e:
			print( "nlReplace1",e,type(s))
			raise e
		try:
			s = self.nl.join(s.split(u'\n'))
		except Exception as e:
			print( "nlReplace2",e)
			raise e
		return s
	
	def _openFile(self):
		if self.outf is None:
			if self.outfile is None:
				self.outf = sys.stdout
			else:
				self.outf = codecs.open(self.outfile,self.write_mode,self.coding)
	
	def _closeFile(self):
		if self.outf is not None:
			self.outf.close()

	def _writeHeader(self):
		self.outf.write(u"%s\n" % self.delimiter.join(self.fields))
	
	def unicodeit(self,obj):
		if type(obj) == type(u''):
			return obj
		try:
			obj = str(obj)
		except:
			pass

		try:
			return obj.decode(self.coding)
		except:
			try:
				return obj.decode('gb2312')
			except:
				try:
					return obj.decode('utf8')
				except Exception as e:
					print( "unicodeit",e)
					raise e

	def write(self,rec):
		ret = [self.nlReplace(self.unicodeit(i)) for i in rec ]
		self.buffer.append(self.delimiter.join(ret))
		if self._isBufferOverflow():
			self._write()
			self.buffer = []

	def _write(self):
		if not self.head:
			self._writeHeader()
			self.head = True
		self.outf.write(u"%s\n" % u'\n'.join(self.buffer))

	def finish(self):
		self._write()
		self._closeFile()
	
	def __del__(self):
		self.finish()
		
class SQLWriter(BaseWriter):
	def __init__(self,outfile=None,database="testdb",table="testtbl",coding="utf8",bufferSize=10000,maxWrite=0):
		BaseWriter.__init__(self,bufferSize=bufferSize,maxWrite=maxWrite)
		self.outfile = outfile
		self.database = database
		self.table = table
		self.outf = None
		self._openFile()
		self.coding = coding

	def _openFile(self):
		if self.outfile is None:
			self.outf = sys.stdout
		else:
			self.outf = open(self.outfile,'w')
	
	def _closeFile(self):
		self._write()
		if self.outfile is not None:
			self.outf.close()
		
	def write(self,rec):
		ret = [i.encode(self.coding) if type(i) == type(u'') else '' if i is None else str(i) for i in rec ]
		t = tuple(ret)
		self.buffer.append(self.sqlcmd % t)
		if self._isBufferOverflow():
			self._write()
			self.buffer = []

	def _write(self):
		self.outf.write('%s\n' % '\n'.join(self.buffer))
	
	def finish(self):
		self._write()
		self._closeFile()
	
	def __del__(self):
		self.finish(self)
								
	def setDescription(self,desc):
		BaseWriter.setDescription(self,desc)
		self.outf.write("use %s;\ngo;\n" % self.database)
		flist = ','.join(self.fields)
		flist = flist.encode(self.coding)
		valist = ','.join(["'%s'"] * len(self.fields))
		sqlcmd = "insert into %s (%s) values (%s)" % (self.table,flist,valist)
		self.sqlcmd = sqlcmd.encode(self.coding)
	

	@classmethod
	def isMe(self,filetype):
		return filetype=='sql'
	
class DictRecordsWriter(BaseWriter):
	@classmethod
	def isMe(self,filetype):
		return filetype=='records'
	
	def __init__(self,maxWrite=0):
		BaseWriter.__init__(self,maxWrite=maxWrite)
		self.records = []
	
	def write(self,r):
		rec = {}
		[ rec.update({self.fields[i]:r[i]}) for i in range(len(self.fields)) ]
		self.records.append(rec)

	def getResult(self):
		return self.records
	
	def finish(self):
		pass
	
	def __del__(self):
		pass
				
def writerFactory(filetype,**kwargs):
	def findSubclass(ft,klass):
		for k in klass.__subclasses__():
			if k.isMe(ft):
				return k
			k1 = findSubclass(ft,k)
			if k1 is not None:
				return k1
		return None
	k = findSubclass(filetype,BaseWriter)
	return k(**kwargs)
