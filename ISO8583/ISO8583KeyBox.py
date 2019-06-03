# -*- coding:utf8 -*-
# 银联加密解密
# 使用 DES加解密
# 

from Crypto.Cipher import DES,DES3
from appPublic.mylog import mylog
from appPublic.PublicData import public_data
import random

def null(s) : pass

def logit(s) :
	mylog(__file__ + ':' + s)

# each byte in bs will transfer to 2 bytes
def string2bcd(bs) :
	ret = ""
	for i in bs :
		v = ord(i)
		ret += "%02x" % v
	return ret.upper()

def random_key(keylen) :
	ret = '12345678123456781234567812345678'
	klen = keylen * 2
	return bcd2string(ret[:klen])

	ss = "0123456789"
	k1 = ""
	klen = keylen * 2
	while len(k1)<klen:
		k1 += ss[random.randint(0,9)]
	return bcd2string(k1)

# 2 bytes compose to one byte
def bcd2string(s) :
	dig_values = {
		'0':0,
		'1':1,
		'2':2,
		'3':3,
		'4':4,
		'5':5,
		'6':6,
		'7':7,
		'8':8,
		'9':9,
		'A':10,
		'B':11,
		'C':12,
		'D':13,
		'E':14,
		'F':15,
	}
	ret = []
	max = len(s)
	i = 0
	while i < max :
		c = s[i].upper()
		v = dig_values[c] * 16
		c = s[i+1].upper()
		v += dig_values[c]
		ret.append(chr(v))
		i += 2
	return ''.join(ret)

def pin2hex(pin) :
	l = len(pin)
	if len(pin) % 2 == 1 :
		pin = pin + 'F'
	i = 0
	s = '%02d' % l + pin
	hex = bcd2string(s)
	while len(hex)<8 :
		hex += chr(255)
	return hex

def XorString(s1,s2) :
	s=[]
	l = len(s1)
	i=0
	while i<l :
		v = ord(s1[i]) ^ ord(s2[i])
		s.append(chr(v))
		i += 1
	return ''.join(s)

def calculateMAC(des_obj,s) :
	""" calculate MAC
	des_obj is a DES object initial by mac key
	s is a string to calculate mac
	return mac
	"""
	l = len(s)
	cnt,m = divmod(l,8)
	if m!= 0 :
		s += '\0' * (8-m)
		cnt += 1
	lastD = None
	i = 0
	while i < cnt :
		f = i*8
		s8 = s[f:f+8]
		if lastD!=None :
			s8 = XorString(lastD,s8)
		lastD = des_obj.encrypt(s8)
		i += 1

	return lastD
def pan2hex(pan) :
	""" pan右边前一位开始的12位数字 """
	l= len(pan)
	f = l-13
	s = pan[f:l-1]
	return '\0' * 2 + bcd2string(s)

class ISO8583KeyPeer :
	def __init__(self,peer,mk1,mk2,tripledes=False) :
		self.peer = peer
		self.triple = tripledes
		self.klen = self.triple and 16 or 8
		self.workklen = 8
		if len(mk1)<self.klen :
			raise Exeption('master key first part length to short',mk1)
		if len(mk2) < self.klen :
			raise Exception('master key second part length to short',mk2)

		self.__mkey = bcd2string(mk1[:self.klen]) + bcd2string(mk2[:self.klen])
		if self.triple :
			self.__mobj = DES3.new(self.__mkey,DES3.MODE_ECB)
		else :
			self.__mobj = DES.new(self.__mkey,DES.MODE_ECB)
		self.__pin_obj = None
		self.__mac_obj = None
	
	def getKeys(self) :
		return string2bcd(self.__mkey), \
			string2bcd(self.__pin_key), \
			string2bcd(self.__mac_key)

	def getpeer(self) :
		return peer

	def encrypt(self,k_type,s) :
		if k_type=='M' :
			return self.__mobj.encrypt(s)
		if k_type=='m' :
			return self.__mac_obj.encrypt(s)
		if k_type=='p' :
			return self.__pin_obj.encrypt(s)
		return s

	def decrypt(self,k_type,s) :
		if k_type=='M' :
			return self.__mobj.decrypt(s)
		if k_type=='m' :
			return self.__mac_obj.decrypt(s)
		if k_type=='p' :
			return self.__pin_obj.decrypt(s)
		return s

	def setWorkingKey(self,pin_key,mac_key) :
		# print len(pin_key),pin_key,len(mac_key),mac_key
		assert len(pin_key)>=self.workklen
		assert len(mac_key)>=self.workklen
		self.__pin_key = self.__mobj.decrypt(pin_key[:self.workklen])
		self.__mac_key = self.__mobj.decrypt(mac_key[:self.workklen])
		self.getWorkingKeyObjectEnc()
		
	def getWorkingKey(self) :
		"""
		generate a pin key and a mac key
		"""
		self.__pin_key = random_key(self.workklen)
		self.__mac_key = random_key(self.workklen)
		mpk,mmk = self.getWorkingKeyObjectEnc()
		# print self.__pin_key,self.__mac_key
		logit('%s:MK:%s,pk:%s--%s:mk:%s--%s:' %
				(self.triple and 'DES3' or 'DES',
					string2bcd(self.__mkey),
					string2bcd(self.__pin_key),
					string2bcd(mpk),
					string2bcd(self.__mac_key),
					string2bcd(mmk))
			)
		return (mpk,mmk)

	def getWorkingKeyObjectEnc(self) :
		if self.workklen>8 :
			self.__pin_obj = DES3.new(self.__pin_key,DES3.MODE_ECB)
			self.__mac_obj = DES3.new(self.__mac_key,DES3.MODE_ECB)
		else :
			self.__pin_obj = DES.new(self.__pin_key,DES.MODE_ECB)
			self.__mac_obj = DES.new(self.__mac_key,DES.MODE_ECB)

		return (self.__mobj.encrypt(self.__pin_key), \
			self.__mobj.encrypt(self.__mac_key))
				
	def encrypt_pin(self,pin,pan=None) :
		"""
		encrypt pin
		"""
		if self.__pin_obj == None :
			self.getWorkingKey()
		s1 = pin2hex(pin)
		plain = s1
		if pan!=None :
			s2 = pan2hex(pan)
			plain = XorString(s1,s2)
		return self.__pin_obj.encrypt(plain)

	def decrypt_pin(self,bin,pan=None) :
		"""
		decrypt pin
		"""
		t = self.__pin_obj.decrypt(bin)
		if pan!=None :
			s2 = pan2hex(pan)
			t = XorString(t,s2)
		s = string2bcd(t)
		try :
			plen = int(s[:2])
			return s[2:plen+2]
		except :
			logit('decrypt_pin error:%s' % s)
			return ''

	def gen_mac(self,iso8583) :
		"""
		create iso8583 package mac
		"""
		if self.__mac_obj==None :
			self.getWorkingKey()
		s = iso8583.mac_string()
		return self.gen_mac_str(s)

	def gen_mac_str(self,s) :
		mac = calculateMAC(self.__mac_obj,s)
		mac16 = string2bcd(mac)
		mac8 = mac16[:8]
		logit('gen_mac():mac_key=%s,mac_string=%s,mac=%s' % \
				( self.__mac_key, s, mac16))
		return mac8

	def chk_mac(self,iso8583,mac=None) :
		"""
		"""
		mac1 = self.gen_mac(iso8583)
		if mac==None :
			mac=iso8583.get_mac()
		macCheck_flag = getattr(public_data,'macCheck_flag',False)
		logit('chk_mac():%s:%s'%(string2bcd(mac),string2bcd(mac1)))
		if not macCheck_flag :
			return True
		return mac==mac1


class KeyBox :
	sk = 'ymq1234_'
	def __init__(self) :
		self.peers = {}
	
	def addPeer(self,peer,mk1,mk2,triple=False) :
		self.peers[peer] = ISO8583KeyPeer(peer,mk1,mk2,triple)

	def encrypt(self,peer,k_type,s) :
		p = self.peers[peer]
		return p.encrypt(k_type,s)

	def decrypt(self,peer,k_type,s) :
		p = self.peers[peer]
		return p.decrypt(k_type,s)

	def encrypt_pin(self,peer,pin,pan=None) :
		p = self.peers[peer]
		return p.encrypt_pin(pin,pan)

	def recrypt_pin(self,from_peer,to_peer,bin,pan=None) :
		p = self.peers[from_peer]
		pin = p.decrypt_pin(bin,pan)
		return self.encrypt_pin(to_peer,pin,pan)

	def gen_mac(self,peer,pkg) :
		p = self.peers[peer]
		return p.gen_mac(pkg)

	def chk_mac(self,peer,pkg,mac=None) :
		p = self.peers[peer]
		return p.chk_mac(pkg,mac)

	def newWorkingKey(self,peer) :
		p = self.peers[peer]
		return p.getWorkingKey()

	
