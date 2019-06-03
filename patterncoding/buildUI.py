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

def readNSJson(json_filename):
	f = codecs.open(json_filename,"r","utf-8")
	ret = json.load(f)
	f.close()
	return ret

def renderAll(namespace):
	workdir = ''
	xlsxs = []
	if namespace['sourcePath'][-len('.xlsx'):] == '.xlsx' or namespace['sourcePath'][-len('.xls'):] == '.xls':
		workdir = os.path.dirname(namespace['sourcePath'])
		xlsxs = [namespace['sourcePath']]
	else:
		workdir = namespace['sourcePath']
		xlsxs = [ f for f in listFile(namespace['sourcePath'],'.xlsx')] + [ f for f in listFile(namespace['sourcePath'],'.xls')]
		
	ac = ArgsConvert('${','}$')
	engines = {}
	e = MyTemplateEngine(namespace['tmplPaths'])
	#print( "tmpl paths = ",namespace['tmplPaths'])
	#print( xlsxs)
	for xlsx in xlsxs:
		print( xlsx," handling ...")
		a = CRUDData(xlsx)
		data = a.read()
		g = namespace.get('global',False)
		if g:
			data.update(g)
		for tmpl,fn in namespace['outputMapping'].items():
			base = os.path.basename(xlsx)
			bs = base.split('.')
			basename = '.'.join(bs[:-1])
			namespace.update({'basename' : basename})
			vs = ac.findAllVariables(fn)
			filename = ac.convert(fn,namespace).decode('utf8').encode('gb2312');
			#print( vs,fn,filename)
			namespace.update({'filename' : filename })
			
			namespace.update({'tmplname':tmpl})
			s = e.render(tmpl,data)

			out_s = s.decode(namespace['coding'])
			_mkdir(os.path.dirname(namespace['filename']))
			f = codecs.open(namespace['filename'],"w","utf-8")
			f.write(out_s)
			f.close()

if len(sys.argv) < 2:
	print( "Usage:\n%s build_description_json_file" % sys.argv[0])
	sys.exit(1)

NS = readNSJson(sys.argv[1])
#print( NS)

renderAll(NS)
