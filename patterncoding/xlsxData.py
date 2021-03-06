import os
import sys
import xlrd
from appPublic.myjson import loadf,dumpf,dumps

from appPublic.dictObject import DictObject
	
class TypeConvert:
	def conv(self,typ,v):
		if typ is None:
			return v
		f = getattr(self,'to_'+typ,None)
		if f is None:
			return v
		return f(v)
	
	def to_int(self,v):
		try:
			return int(v)
		except:
			return 0
	
	def to_float(self,v):
		try:
			return float(v)
		except:
			return 0.0
	
	def to_str(self,v):
		try:
			return str(v)
		except:
			return ''
	def to_json(self,v):
		if v == '':
			return v
		try:
			return loads(v)
		except:
			return v
			
	def to_date(self,v):
		return v
	
	def to_time(self,v):
		return v
	
	def to_timestamp(self,v):
		return v

	def to_cruddata(self,v):
		vs = v.split('"',3)
		if vs < 3:
			return v
		fn = vs[1]
		d = CRUDData(fn)
		try:
			data = d.read()
		except Exception as e:
			return v
		if vs[2] is None:
			return data
		cmd = "d%s" % vs[2]
		ret=eval(cmd,{'d':data})
		return ret
    
	def to_xlsxdata(self,v):
		vs = v.split('"',3)
		if vs < 3:
			return v
		fn = vs[1]
		d = XLSXData(fn)
		try:
			data = d.read()
		except Exception as e:
			return v
		if vs[2] is None:
			return data
		cmd = "d%s" % vs[2]
		ret=eval(cmd,{'d':data})
		return ret
    
class CRUDException(Exception):
	def __init__(self,xlsfile,errmsg,*args,**argv):
		Exception.__init__(self,*args,**argv)
		self.xlsfile = xlsfile
		self.errmsg = errmsg
	
	def __str__(self):
		return 'filename:' + self.xlsfile+' error:' + self.errmsg

class XLSXData(object):
	def __init__(self,xlsxfile):
		atype = type(xlsxfile) 
		if atype == type('') or atype == type(u''):
			self.xlsxfile = xlsxfile
			self.book = xlrd.open_workbook(xlsxfile)
		else:
			self.book = xlsxfile # is from Factory
	  
	def readRecords(self,sheet):
		i = 1
		recs = []
		name = sheet.name
		fields = self.getFieldNames(sheet)
		tc = TypeConvert()
		while (i < sheet.nrows):
			j = 0
			rec = {}
			while (j < sheet.ncols):
				a = sheet.cell(i,j).value
				k = fields[j][0]
				v = tc.conv(fields[j][1],a)
				rec[k] = v
				j += 1
			o = DictObject(**rec)
			recs.append(o)
			i += 1
		return {name:recs}
	 
	def read(self):
		ret = {}
		for s in self.book.sheets():
			ret.update(self.readRecords(s))
		return DictObject(**ret)

	def getFieldNames(self,sheet):
		fs = []
		i = 0
		while (i < sheet.ncols):
			f = sheet.cell(0,i).value
			if f is None:
				f = 'F_' + str(i)
			else:
				if type(f) != type(u""):
					f = 'F_' + str(f)
			b=f.split(':')
			if len(b) < 2:
				b.append(None)
			fs.append(b)
			i+= 1
		return fs
	  
class CRUDData(XLSXData):
	@classmethod
	def isMe(self,book):
		sheets = book.sheets()
		names = [ s.name for s in sheets ]
		if 'summary' not in names:
			return False
		if 'fields' not in names:
			return False
		if 'validation' not in names:
			return False
		return True
	
	def read(self):
		d = XLSXData.read(self)
		if not 'summary' in d.keys():
			raise CRUDException(self.xlsxfile,'summary sheet missing')
		if not 'fields' in d.keys():
			raise CRUDException(self.xlsxfile,'fields sheet missing')
		if not 'validation' in d.keys():
			raise CRUDException(self.xlsxfile,'validation sheet missing')
			
		v = d['summary'][0]['primary']
		v = v.split(',')
		d['summary'][0]['primary'] = v
		#print( "priamry=",d['summary'][0]['primary'],'type=',type(d['summary'][0]['primary']))
		d = self.convForeignkey(d)
		d = self.convIndex(d)
		return d
  
	def convForeignkey(self,data):
		vs = data['validation']
		nvs = []
		for v in vs:
			if v['oper'] == 'fk':
				m = v['value']
				des= m.split(':')
				if len(des) != 3:
					raise CRUDException(self.xlsxfile,'fk value error:%s' % m)
				v['value'] = {'table':des[0],'value':des[1],'title':des[2]}
			nvs.append(v)
		data['validation'] = nvs
		return data
 
	def getFieldByNmae(self,fields,name):
		for f in fields:
			if f['name'] == name:
				return f

	def getFKs(self,validation):
		fks = []
		for v in validation:
			if v['oepr'] == 'fk':
				fks.append(v)
		return fks

	def getIDXs(self,validation):
		idxs = []
		for v in validation:
			if v['oper'] == 'idx':
				idxs.append(v)
		return idxs

	def isFieldExist(self,fields,name):
		for f in fields:
			if f['name'] == name:
				return True
		return False

	def convIndex(self,data):
		vs = data['validation']
		nvs = []
		for v in vs:
			if v['oper'] == 'idx':
				m = v['value']
				des= m.split(':')
				if len(des) != 2:
					raise CRUDException(self.xlsxfile,'idx value format:idx_type:keylist:%s' % m)
				v['value'] = {'idxtype':des[0],'keys':des[1].split(',')}
			nvs.append(v)
		data['validation'] = nvs
		return data

def xlsxFactory(xlsxfilename):
	def findSubclass(name,klass):
		for k in klass.__subclasses__():
			if k.isMe(name):
				return k
			k1 = findSubclass(name,k)
			if k1 is not None:
				return k1
			return None
	book = xlrd.open_workbook(xlsxfilename)
	k = findSubclass(book,XLSXData)
	if k is not None:
		return k(book)
	return XLSXData(book)

def ValueConvert(s):
	if s[:9] == 'xlsfile::':
		d = xlsxFactory(s[9:])
		return d.read()
	if s[:10] == 'jsonfile::':
		return loadf(s[10:])
	return s
	
def paramentHandle(ns):
	for k,v in ns.items():
		ns[k] = ValueConvert(v)
	return ns

if __name__ == '__main__':
	retData = {}
	ns = {}
	datafiles = []
	for a in sys.argv[1:]:
		m = a.split('=',1)
		if len(m)>1:
			ns[m[0]] = m[1]
		else:
			datafiles.append(a)
	
	ns = paramentHandle(ns)
	for f in datafiles:
		ext = os.path.splitext(f)[-1]
		if ext in ['.xlsx','.xls' ]:
			d = xlsxFactory(f)
			data = d.read()
			retData.update(data)
		else:
			data = loadf(f)
			retData.update(data)
	retData.update(ns)
	print( dumps(retData))
     
