import os
import sys
import codecs
import ujson

#from sqlor import sqlorFactory,opendb
from sqlorAPI import sqlorFromFile,DBPools
from writerAPI import writerFactory


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print( """a universal SQL runner, support many database
Usage:\n%s dbdesc [a=v,...] [sqlfile ... ]""" % sys.argv[0])
		sys.exit(1)
	f = open(sys.argv[1],'r')
	dbdesc = ujson.load(f)
	f.close()
	print('dbdesc=',dbdesc)
	pools = DBPools({'db':dbdesc})
	db = pools.getSqlor('db',dbdesc)
	files = []
	NS = {}
	ignore_error = False
	for arg in sys.argv[2:]:
		if arg == '-i': 
			ignore_error = True
		else:
			a = arg.split('=',1)
			if len(a) < 2:
				files.append(arg)
			else:
				NS[a[0]] = a[1]
	print( "ns=",NS)
	if len(files) < 1:
		sqlstring = sys.stdin.read().decode('utf8')
		sqlds = {
			"sql_string":sqlstring,
			"ignore_error":ignore_error,
		}
		NS={}
		d = db.sqlExecute(sqlds,NS)
	else:	
		for f in files:
			sqlds = {
				"sql_file":f,
				"ignore_error":ignore_error,
			}
			NS={}
			d = db.sqlExecute(sqlds,NS)
	del pools
