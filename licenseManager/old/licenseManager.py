import os,sys
from io import StringIO
import ujson as json

from appPublic.folderUtils import ProgramPath
import pickle
import rsa
from appPublic.macAddress import getAllMacAddress
from appPublic.timeUtils import getCurrentTimeStamp


class UserIdentify(object):
	def __init__(self,appname,mac,pinfo):
		self.appname = appname
		self.mac = mac
		self.pinfo = pinfo
		self.ts = getCurrentTimeStamp()
		self.rc = None
	
	def __str__(self):
		return self.appname + '|' + self.mac + '|' + self.pinfo + '|' + self.ts
	
	def toJson(self):
		dic = {
			'appname':self.appname,
			'mac':self.mac,
			'pinfo':self.pinfo,
			'registertime':self.ts,
			'rc':self.rc,
		}
		return json.dumps(dic)
	
	def fromJson(self,jsonstr):
		dic = json.loads(jsonstr)
		self.appname = dic.get('appname',None)
		self.mac = dic.get('mac',None)
		self.pinfo = dic.get('pinfo',None)
		self.rc = dic.get('rc',None)
		self.ts = dic.get('registertime',None)
		
class LicenseGen(UserIdentify):
	def __init__(self,appname,mac,pinfo,pk_file):
		super(LicenseGen,self).__init__(appname,mac,pinfo)
		self.pk_file = pk_file
		f = open(pk_file,'rb')
		self.pk = pickle.load(f)
		f.close()
		print(self.pk)
	
	def gen(self):
		s = str(self)
		self.rc = rsa.sign(s,self.pk)
		ofile = os.path.join(os.path.dirname(self.pk_file),'license.json')
		s = self.toJson()
		f = open(ofile,'w')
		f.write(s)
		f.close()

class LicenseChecker(UserIdentify):
	def fromLicenseFile(self):
		p = os.path.join(ProgramPath(),'license.json')
		print("license file name=",p)
		f = open(p,'r')
		s = f.read()
		f.close()
		self.fromJson(s)
		print(self)
		
	def checkLicense(self):
		try:
			self.fromLicenseFile()
		except Exception as e:
			print("license file 1",e,ProgramPath(),sys.argv)
			self.registor = False
			return
		
		macs = [ i for i in getAllMacAddress()]
		if self.mac not in [ i[0] for i in macs ]:
			self.registor= False
			self.ip = '0.0.0.0'
			return
		self.ip = [i[1] for i in macs if i[0] == self.mac ][0]
		try:
			f = StringIO.StringIO(self.pubkey)
			key = pickle.load(f)
			f.close()
			s = str(self)
			verstr = rsa.verify(self.rc,key)
			if verstr == s:
				self.registor = True
			else:
				print("check failed 2")
				self.registor = False
		except Exception as e:
			print('4',e)
			print('exception 3',e)
			self.registor = False
			return

	def isLicensed(self):
		self.checkLicense()
		return self.registor

if __name__ == '__main__':
	import sys
	if len(sys.argv)<2:
		lg = LicenseGen('ktv','24-77-03-2B-E1-F0','free','./ktv/pri.key.dmp')
		lg.gen()
	lg = LicenseChecker('ktv','24-77-03-2B-E1-F0','free')
	print(lg.isLicensed())