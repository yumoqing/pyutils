# 

import os
import sys
import time
import ujson as json
import codecs
from appPublic.argsConvert import ArgsConvert
from appPublic.folderUtils import listFile,_mkdir
from xlsxData import CRUDData,XLSXData
from myTemplateEngine import MyTemplateEngine

def readJson():
	data = sys.stdin.read()
	ret = json.loads(data)
	return ret

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print( "Usage:\n%s tmplfile" % sys.argv[0])
		sys.exit(1)
	paths=[]
	tmpls=[]
	ap=False
	for a in sys.argv[1:]:
		if ap:
			paths.append(a)
			ap = False
		else:
			tmpls.append(a)
		
		if a == '-p':
			ap = True
	ns = readJson()	
	for t in tmpls:
		mypath = [i for i in paths ]
		mypath.append(os.path.dirname(t))
		tmplname = os.path.basename(t)
		e = MyTemplateEngine(mypath)
		s = e.render(tmplname,ns)
		print( s)
	sys.exit(0)
