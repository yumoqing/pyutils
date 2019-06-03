import os
import sys
import codecs
import ujson
import cx_Oracle

#from sqlor import sqlorFactory,opendb
from sqlorAPI import sqlorFromFile
# from writerAPI import writerFactory

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print( """a universal SQL runner, support many database
Usage:\n%s dbdesc rarfile""" % sys.argv[0])
		sys.exit(1)
	db = sqlorFromFile(sys.argv[1])
	cur = db.conn.cursor()
	f = open(sys.argv[2],'rb')
	img =f.read()
	f.close()
	sql = """insert into sidconfig (conf) values (:blobData)"""
	cur.setinputsizes(blobData=cx_Oracle.BLOB)
	cur.execute(sql,{'blobData':img})
	cur.execute('commit')
	cur.close()
	db.conn.close()
