#
import sys
sys.path.append('..')
from licenseManager import LicenseGen,LicenseChecker

class MYLC(LicenseChecker):
	def __init__(self,pkfile):
		with open(pkfile,'r') as f:
			self.pubkey = pickle.load(f)

if __name__ == '__main__':
	if len(sys.argv)<2:
		lg = LicenseGen('ktv','24-77-03-2B-E1-F0','free','./pri.key.dmp')
		lg.gen()
	else:
		lc = MYLC('./pub.key.dmp')
		r = lc.isLicensed()
		print('checker status',r)
	


