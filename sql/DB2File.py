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
	sql = """select conf from sidconfig"""
	cur.execute(sql)
	rez = cur.fetchall()
	img = rez[0][0].read()
	cur.close()
	db.conn.close()
	f = open(sys.argv[2],'wb')
	f.write(img)
	f.close()
