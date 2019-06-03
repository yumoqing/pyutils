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

def getType(f):
	if f['type'].lower() == 'char':
		return 'char'
	if f['type'].lower() == 'varchar2':
		return 'str'
	if f['type'].lower() == 'nclob':
		return 'str'
	if f['type'].lower() == 'date':
		return 'date'
	if f['type'].lower()[:9] == 'timestamp':
		return 'timestamp'
	if f['type'].lower() == 'number' and (f['dec'] is None or f['dec'] == 0):
		return 'long'
	return 'float'

if __name__ == '__main__':	
	if len(sys.argv) < 3:
		print( """a Oracle schema acheive tool
	Usage:
	%s dbdesc_json output_path
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

	NS={}
	summarysSQL = """SELECT name FROM SysObjects 
	Where XType='U' 
	and lower(name) not in ('ed_foreignremarks','ed_macrodata',
		'hk_sectioninfo','lc_analysereport',
		'lc_announcementinfo','lc_bshareipo',
		'LC_EnterprisePerfStdValue','lc_interimbulletin_se',
		'lc_keywordinfo_se','lc_marketnews_se',
		'lc_marketview_se','lc_news_se',
		'lc_organizationinfo','lc_performanceforecast_se')
	and lower(name) >= 'lc_performanceforecast_se_data'
	ORDER BY Name"""

	fieldsSQL="""select * from $[table_name]$"""

	sqldesc = {
			"writer":{
				"filetype":"records",
				"kwargs":{
				}
			},
			"sql_string":summarysSQL,
			"default":{}
		}
		
	grapdesc = {
			"writer":{
				"filetype":"csv",
				"kwargs":{
					"outheader":True,
					"maxWrite":100000,
				}
			},
			"ignore_error":1,
			"sql_string":fieldsSQL,
		}
	tables = db.sqlExecute(sqldesc,{})
	ac = ArgsConvert('$[',']$')
	cur_t = None
	for t in tables:
		fn = os.path.join(sys.argv[2],t['name'].lower() + '_data.csv')
		grapdesc['writer']['kwargs']['outfile'] = fn
		grapdesc['sql_string'] = ac.convert(fieldsSQL,{'table_name':t['name']})
		try:
			tables = db.sqlExecute(grapdesc,{})
		except:
			print( t['name'],"data grap error")
	conn.close()
