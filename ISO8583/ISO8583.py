# -*- gb2312 -*-
# ISO8583 data definition
# refer to PBC spec.

import string
from ISO8583Bitmap import ISO8583Bitmap
from appPublic.mylog import mylog

def logit(s) :
	mylog('%s:%s' % (__file__,s))

_ISO8583Field_dict = {
'f002':{'name':'Primary account','type':'n..19','mac':True},
'f003':{'name':'Processing code','type':'n6','mac':True},
'f004':{'name':'Transaction account','type':'n12','mac':True},		# 000000010000 stand for 100.00
'f007':{'name':'Transmission date/time','type':'n10','mac':True},		# MMDDhhmmss
'f011':{'name':'System trace audit number','type':'n6','mac':True},	
'f012':{'name':'Local time','type':'n6'},			# hhmmss
'f013':{'name':'Local date','type':'n4'},			# MMDD
'f014':{'name':'Card expiration date','type':'n4'},		# YYMM
'f015':{'name':'Settlement date','type':'n4'},			# MMDD
'f018':{'name':'Merchart type','type':'n4','mac':True},			
'f022':{'name':'Point of service entry mode code','type':'n3'},
'f025':{'name':'Point of service condition code','type':'n2','mac':True},
'f026':{'name':'Point of service pin capture code','type':'n2'},
'f028':{'name':'Amount transaction fee','type':'xn8','mac':True},
'f032':{'name':'Acquiring institution identification code','type':'n..11','mac':True},
'f033':{'name':'Forwarding institution identification code','type':'n..11','mac':True},
'f035':{'name':'Track 2 data','type':'z..37'},
'f036':{'name':'Track 3 data','type':'z..104'},
'f037':{'name':'Retrieval Reference Number','type':'an12'},
'f038':{'name':'Authorization identification response','type':'an6','mac':True},
'f039':{'name':'Response code','type':'an2','mac':True},
'f041':{'name':'Card acceptor terminal identification','type':'ans8','mac':True},
'f042':{'name':'Card acceptor identification code','type':'ans15','mac':True},
'f043':{'name':'Card acceptor name/location','type':'ans40'},
'f048':{'name':'Additional data','type':'ans..512'},
'f049':{'name':'Currency code','type':'an3'},
'f052':{'name':'Pin Data','type':'b64'},
'f053':{'name':'Security related control information','type':'n16'},
'f054':{'name':'Additional amount','type':'an..040'},
'f059':{'name':'Details inquiry data','type':'ans..600'},
'f060':{'name':'Reserved','type':'ans..030'},
'f066':{'name':'Settlement code','type':'n1','mac':True},
'f070':{'name':'Network manaagement information code','type':'n3'},
'f082':{'name':'Processing-fee-amount-of-credits','type':'n12','mac':True},
'f084':{'name':'Processing-fee-amount-of-debits','type':'n12','mac':True},
'f086':{'name':'Amount-of-credits','type':'n16','mac':True},
'f087':{'name':'Reversal-amount-of-credits','type':'n16','mac':True},
'f088':{'name':'Amount-of-debits','type':'n16','mac':True},
'f089':{'name':'Reversal-amount-of-debits','type':'n16','mac':True},
'f090':{'name':'Original data element','type':'n42','mac':True},
'f097':{'name':'Amount-of-net-settlement','type':'xn16','mac':True},
'f100':{'name':'Receiving institution identification code','type':'n..11'},
'f102':{'name':'Account identification 1','type':'ans..28','mac':True},
'f103':{'name':'Account identification 2','type':'ans..28','mac':True},
'f128':{'name':'Message authentication code','type':'b64'},
}

def MAC_char(c) :
	if c >= 'A' and c<='Z' :
		return True
	if c>='0' and c<='9' :
		return True
	if c in [' ',',','.' ] :
		return True

def MAC_STR(s) :
	r = [ i for i in s if MAC_char(i) ]
	return ''.join(r)

def hex_string(s) :
	fs = []
	if type(s) != type('') :
		logit('hex_string() error, s is not a string,type(s)=%s,s=%s' % (type(s),str(s)))
		raise
	for i in s :
		v = ord(i)
		fs.append('%02x' % v)
	return ' '.join(fs)

def dataPrintable(v,t) :
	ret = []
	for i in v :
		if i in string.printable :
			ret.append(i)
		else :
			ret.append('[%02x]' % ord(i))
	return ''.join(ret)
	
	if 's' in t or \
			'B' in t or \
			'b' in t :
		return hex_string(v)
	else :
		return v

def checkCharType(typs,c) :
	for i in typs :
		if i=='a' :
			if c>='a' and c <= 'z' :
				return True
			if c>='A' and c <= 'Z' :
				return True
		if i=='b' :
			return True
		if i=='n' :
			if c>='0' and c <= '9' :
				return True
		if i=='s' :
			if c < ' ' :
				return True
		if i=='B' :
			return True
		if i=='z' :
			return True
		if i=='x' :
			return True
	return False

def DataTypeDetail(typ) :
	'''
	split a datatype string to (typ,length,variable length flag)
	'''
	varlength = False
	a = typ.split('..')
	if len(a)>1 :
		varlength=True
	typ1 = ''
	length1=''
	for i in typ :
		if i >='0' and i <= '9' :
			length1 += i
		else :
			typ1 += i
	return (typ1,length1,varlength)

def dataAttachTo8583(data,typ) :
	if data==None :
		return ''

	typ1,length1,varlength = DataTypeDetail(typ)
	if typ1 == 'z' or typ=='B' :
		return data

	if varlength :
		l = len(length1)
		L = str(len(data))
		while len(L)< l :
			L = '0' + L
		return L + data
	l = int(length1)
	if typ1=='b' :
		l,v=divmod(l,8)
		if v :
			l += 1
	while len(data)< l :
		if typ1=='n' :
			data = '0' + data
		else :
			data = data + ' '
	if data>l :
		data = data[:l]
	return data	
	
def dataRipFrom8583(text,typ) :
	""" 
	trip data out from iso8583 package
	text, where the trip beginning
	typ, data type
	return (data,length)
	length -- charectors trip out from text
	data   -- data trip out from text
	"""
	typ1,length1,varlength = DataTypeDetail(typ)
	if typ1 == 'z' :
		return (text,len(text))

	if length1=='' :
		raise Exception('type definition miss length(%s)' % typ)
	if typ1=='' :
		raise Exception('type definition miss type(%s)' % typ)
	if varlength :
		l = len(length1)
		maxlength = 0
		try :
			maxlength = int(length1)
		except :
			raise 
		s1 = text[:l]
		datalen = 0 
		try :
			datalen = int(s1)
		except :
			raise Exception('need int but not,(%s)' % s1)
		if datalen > maxlength :
			raise Exception('%d extend maxlen(%d)' % (datalen,maxlength))
		value = text[l:l+datalen]
		return (value,l + datalen)
	datalen = int(length1)
	if typ1=='b' :
		datalen,v = divmod(datalen,8)
		if v :
			datalen += 1

	value = text[:datalen]
	#for i in value :
	#	if not checkCharType(typ1,i) :
	#		s = 'typ1= %s' % typ1 + 'i=%s' % i
	#		raise s,text
	return (value,datalen)


class DecodeEncode8583 :
	def __init__(self,dict) :
		self.desc_dict = dict
		self._rawtext = None
		self.decodeError = False
		self.encodeError = False
	
	def encode(self) :
		text = ''
		fields = self.desc_dict.keys()
		fields.sort()
		for i in fields :
			v = getattr(self,i)
			typ = self.desc_dict[i]['type']
			if type(v)!=type('') :
				print(i,'=',v,':type=',type(v))
				continue
			text += dataAttachTo8583(v,typ)
		self._rawtext = text
		return text

	def set(self,name,v) :
		setattr(self,name,v)

	def get(self,name,defautl=None) :
		return getattr(self,name,default)

	def decode(self,text) :
		self.org_text = text[:]
		self._rawtext = text[:]
		fields = self.desc_dict.keys()
		fields.sort()
		for i in fields :
			typ = self.desc_dict[i]['type']
			try :
				v,length=dataRipFrom8583(text,typ)
			except :
				logit('dataRipFrom8583 error,pkg=%s:,field=%s' % ( self.org_text,i) )
				self.decodeError = True
				pass
				# raise 'dataRipFrom8583 error',i
			text = text[length:]
			setattr(self,i,v)

	def rawtext(self) :
		if self._rawtext==None :
			return ''
		return self._rawtext

	def listData(self,exclude=[]) :
		keys = self.desc_dict.keys()
		keys.sort()
		fs = []
		for i in keys :
			if i not in exclude :
				name = self.desc_dict[i]['name']
				typ = self.desc_dict[i]['type']
				v = getattr(self,i,None)
				if v :
					fs.append('%s:%s:%s' % \
						(i,name,dataPrintable(v,typ)))

		return '\n'.join(fs)

class ISO8583PkgHead(DecodeEncode8583) :
	"""
	iso 8583 package head
	"""
	def __init__(self) :
		desc_dict = {
		'ph01':{'name':'Application type','type':'n2'},
		'ph02':{'name':'Specification version number','type':'n2'},
		'ph03':{'name':'Terminal status','type':'n1'},
		'ph04':{'name':'Reserved field','type':'n3'},
		'ph05':{'name':'Package length','type':'n4'},
		}
		DecodeEncode8583.__init__(self,desc_dict)
		self.ph04 = '000'
	
	def setApplicationType(self,apt) :
		self.ph01 = apt

	def getApplicationType(self) :
		return self.ph01

	def setSVnumber(self,svn) :
		self.ph02 = svn
	
	def getSVnumber(self) :
		return sef.ph02

	def setTerminalStatus(self,s) :
		self.ph03 = s
	
	def getTerminalStatus(self) :
		return self.ph03

	def setPackageLength(self,lengStr) :
		self.ph05 = lengStr

	def getPackageLength(self) :
		return self.ph05

class ISO8583Fields(DecodeEncode8583) :
	def __init__(self) :
		DecodeEncode8583.__init__(self,_ISO8583Field_dict)
	
	def encode(self) :
		"""
		encode to iso8583 package text
		"""
		bitmap = ISO8583Bitmap()
		texts=[]
		for i in range(2,129) :
			id = 'f%03d' % i
			if hasattr(self,id) :
				v = getattr(self,id)
				typ = self.desc_dict[id]['type']
				bitmap.setBitmap(i)
				# logit("%s:%s" % (id,v))
				txt = dataAttachTo8583(v,typ)
				texts.append(txt)
		return (bitmap,''.join(texts))

	def decode(self,bitmap,text) :
		self.org_text = text[:]
		self._rawtext = text[:]
		for i in range(2,129) :
			id = 'f%03d' % i
			if bitmap.chkBitmap(i) :
				typ = self.desc_dict[id]['type']
				try :
					v,length=dataRipFrom8583(text,typ)
				except Exception as e:
					raise e
				except :
					logit('dataRipFrom8583 error,pkg=%s:,field=%s'% (self.org_text,id) )
					self.decodeError = True
					pass
					# raise 'dataRipFrom8583 error',id
					
				else :
					text = text[length:]
					setattr(self,id,v)
	
	def setData(self,pos,text) :
		if pos < 2 or pos > 128 :
			return

		id = 'f%03d' % pos
		setattr(self,id,text)
	
	def getData(self,pos) :
		id = 'f%03d' % pos
		return getattr(self,id,None)

	def mac_string(self) :
		texts=[]
		for i in range(2,129) :
			id = 'f%03d' % i
			if not id in self.desc_dict.keys() :
				continue
			dic = self.desc_dict[id]
			if 'mac' in dic.keys() and getattr(self,id,False):
				v = getattr(self,id)
				typ = self.desc_dict[id]['type']
				txt = dataAttachTo8583(v,typ)
				txt = txt.strip()
				if i==90 and len(txt)>20 :
					txt = txt[:20]
				txt = txt.upper()
				txt = MAC_STR(txt)
				if txt!='' :
					texts.append(txt)
		return ' '.join(texts)

class ISO8583(DecodeEncode8583) :
	"""
	iso 8583 package for BankLink of China
	"""
	def __init__(self) :
		desc_dict = {
			'pkg01':{'name':'Package head','type':'n12'},
			'pkg02':{'name':'Message type','type':'n4'},
			'pkg03':{'name':'Bit map','type':'B16'},
			'pkg04':{'name':'Package text','type':'z'},
		}
		DecodeEncode8583.__init__(self,desc_dict)
		self.p_head = ISO8583PkgHead()
		self.bitmap = ISO8583Bitmap()
		self.p_fields = ISO8583Fields()
	
	def listData(self) :
		bitmap,self.pkg04 = self.p_fields.encode()
		bitmap.encode()
		ss = []
		ss.append('=======pkg.listData() BEGIN========')
		ss.append(self.p_head.listData())
		ss.append('Message type:' + self.pkg02)
		ss.append('Bit map:'+bitmap.bitStream())
		ss.append(self.p_fields.listData())
		ss.append('=======pkg.listData() END========')
		return '\n'.join(ss)

	def encode(self) :
		bitmap,self.pkg04 = self.p_fields.encode()
		tlen = 4 + len(bitmap.encode()) + len(self.pkg04)
		self.p_head.ph05 = '%04d' % tlen
		self.pkg03 = bitmap.encode()
		self.pkg01 = self.p_head.encode()

		text = ''
		fields = self.desc_dict.keys()
		fields.sort()
		for i in fields :
			v = getattr(self,i)
			typ = self.desc_dict[i]['type']
			txt = dataAttachTo8583(v,typ)
			# print "txt=",txt,type(txt),type(text)
			text += dataAttachTo8583(v,typ)
		return text

	def decode(self,text) :
		self.org_text = text[:]
		self._rawtext = text[:]
		fields = self.desc_dict.keys()
		fields.sort()
		for i in fields :
			typ = self.desc_dict[i]['type']
			try :
				v,length=dataRipFrom8583(text,typ)
			except :
				logit('dataRipFrom8583 error,pkg=%s,field=%s' % (self.org_text,i) )
				pass
				# raise 'dataRipFrom8583 error',i
			if i=='pkg03' :
				if ord(v[0])>=128 :
					print('16 byte')
					length = 16
				else :
					print('8byte')
					length = 8
					v = v[:8]
			# print 'i==',i		
			text = text[length:]
			setattr(self,i,v)
		
		self.p_head.decode(self.pkg01)
		self.bitmap = ISO8583Bitmap()
		self.bitmap.decode(self.pkg03)
		self.p_fields.decode(self.bitmap,self.pkg04)
		logit('===test pkg==%s' % self.listData())
		
	def mac_string(self) :
		"""
		fixme
		get string to be calculate mac
		"""
		if not getattr(self,'pkg02') :
			return None 
		if self.pkg02[:2] not in ['01','02','04','05' ] :
			return None
		return self.pkg02 + ' ' + self.p_fields.mac_string()

	def get_mac(self) :
		"""
		faxme
		get package mac data
		"""
		try :
			return self.p_fields.f128
		except :
			return None
