import netifaces

def getMacs():
	hdrs = netifaces.interfaces()
	macs =[]
	for hdr in hdrs:
		a = netifaces.ifaddresses(hdr)[netifaces.AF_LINK]
		if len(a[0]['addr']) == 17:
			macs.append(a[0]['addr'])
	return macs
	
if __name__ == '__main__':
	macs = getMacs()
	print macs
