import os
import sys
import codecs
import ujson
import xlrd
import xlwt
import xlutils
from appPublic.argsConvert import ArgsConvert
from sqlor import sqlorFactory,opendb
import sqlor
import mssqlor
import oracleor

def allTableName(my_sqlor):
	summarysSQL = """select a.TABLE_NAME name
	 from user_tables a 
	 order by TABLE_NAME 
	"""
	sqldesc = {
			"writer":{
				"filetype":"records",
				"kwargs":{
				}
			},
			"sql_string":summarysSQL,
			"default":{}
		}
	tables = db.sqlExecute(sqldesc,{})
	return [t['name'] for t in tables ]
	
def dumpTable(my_sqlor,tblname,outPath):
	fieldsSQL="""select * from %s""" % tblname
	#fieldsSQL="""select * from ashareisqa where object_id='{113D4D6F-EBEF-41E9-8FF4-A7F9812B1347}'"""
	grapdesc = {
			"writer":{
				"filetype":"csv",
				"kwargs":{
					"outheader":True,
					"maxWrite":100000,
				}
			},
			"sql_string":fieldsSQL,
		}
	print( fieldsSQL)
	fn = os.path.join(outPath,tblname.lower() + '_data.csv')
	grapdesc['writer']['kwargs']['outfile'] = fn
	grapdesc['sql_string'] = fieldsSQL
	my_sqlor.sqlExecute(grapdesc,{})
	
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print( """a Oracle schema acheive tool
	Usage:
	%s dbdef output_path
	examples of dbdesc_json:
	{
		"driver":"cx_Oracle",
		"kwargs":{
			"user":"rel",
			"password":"edm",
			"dsn":"10.0.193.176:1521/kedm"
		}
	} 
	""" % sys.argv[0])
		sys.exit(1)

	f = codecs.open(sys.argv[1],'r','utf-8')
	dbdesc = ujson.load(f)
	f.close()
	conn = opendb(dbdesc)
	db = sqlorFactory(dbdesc['driver'],conn)
	
	tables = allTableName(db)
	if len(sys.argv) > 3:
		tables = sys.argv[3:]
	
	for t in tables:
		dumpTable(db,t,sys.argv[2])
	conn.close()
