#genKey.py
import os
from appPublic.printf import printf
import sys
import rsa
import pickle
from appPublic.folderUtils import _mkdir,ProgramPath

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Usage:\n%s software_name" % sys.argv[0]
		sys.exit(1)
	p = os.path.join(ProgramPath(),sys.argv[1])
	_mkdir(p)
	pub,pri = rsa.gen_pubpriv_keys(2048)
	printf(pub,pri)
	f = open(os.path.join(p,'pri.key.dmp'),'wb')
	pickle.dump(pri,f)
	f.close()
	f = open(os.path.join(p,'pub.key.dmp'),'wb')
	pickle.dump(pub,f)
	f.close()
