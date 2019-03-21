import os
import sys
import codecs
import ujson
import xlrd
import xlwt
import xlutils
from sqlor import sqlorFactory,opendb
import sqlor
import mssqlor
import oracleor

def getType(f):
	if f['type'].lower() == 'char':
		return 'char'
	if f['type'].lower() == 'varchar2':
		return 'str'
	if f['type'].lower() == 'clob':
		return 'text'
	if f['type'].lower() == 'blob':
		return 'bin'
	if f['type'].lower() == 'date':
		return 'date'
	if f['type'].lower()[:9] == 'timestamp':
		return 'timestamp'
	if f['type'].lower() == 'number' and (f['dec'] is None or f['dec'] == 0):
		return 'long'
	return 'float'
	
def xlwtWriteRecord(ws,x,y,rec):
	for r in rec:
		ws.write(x,y,r)
		y += 1

def writeTableDefinitionXlsx(path,summary,fields):
	wb = xlwt.Workbook()
	ws = wb.add_sheet('summary',cell_overwrite_ok=True)
	xlwtWriteRecord(ws,0,0,["name","title","primary","catelog"])
	if summary['title'] is None:
		summary['title'] = ''
	ws.write(1,0,summary['name'].lower())
	ws.write(1,1,summary['title'].decode('utf-8'))
	ws.write(1,2,summary['primary'])
	
	ws = wb.add_sheet('fields',cell_overwrite_ok=True)
	xlwtWriteRecord(ws,0,0,["name","title","type","length:int","dec:int","nullable","default","comments"])
	i = 1
	for f in fields:
		if f['title'] is None:
			f['title'] = ''
		ws.write(i,0,f['name'].lower().decode('utf-8'))
		ws.write(i,1,f['title'].decode('utf-8'))	
		ws.write(i,2,getType(f))	
		ws.write(i,3,f['length'])	
		ws.write(i,4,f['dec'])	
		ws.write(i,5,f['nullable'])	
		#ws.write(i,6,f['default'])
		i += 1
	ws = wb.add_sheet('data',cell_overwrite_ok=True)
	fs = [ f['name'].lower().decode('utf-8') for f in fields ]
	xlwtWriteRecord(ws,0,0,fs)
	ws = wb.add_sheet('validation',cell_overwrite_ok=True)
	xlwtWriteRecord(ws,0,0,['name',	'oper',	'value'])

	fn = os.path.join(path,'%s.xls' % summary['name'])
	wb.save(fn)

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

	NS={}
	summarysSQL = """SELECT
	  a.TABLE_NAME name,
	  a.COMMENTS title,
	  b.column_name primary
	FROM
	  USER_TAB_COMMENTS a left join (
				select uc.table_name,col.column_name , uc.constraint_type,case uc.constraint_type when 'P' then '1' else '' end "PrimaryKey"
				from user_tab_columns col left join user_cons_columns ucc on ucc.table_name=col.table_name and ucc.column_name=col.column_name
				left join user_constraints uc on uc.constraint_name = ucc.constraint_name and uc.constraint_type='P'
				where uc.table_name is not null 
	) b on a.table_name = b.table_name
	where table_type = 'TABLE'"""

	fieldsSQL="""select utc.COLUMN_NAME name
	,utc.DATA_TYPE type
	,utc.DATA_LENGTH length
	,utc.data_scale dec
	,case when utc.nullable = 'Y' then 'yes' else 'no' end nullable
	,ucc.comments title
	from  user_tab_cols utc left join USER_COL_COMMENTS ucc on utc.table_name = ucc.table_name and utc.COLUMN_NAME = ucc.COLUMN_NAME
	where utc.table_name = ${table_name}$"""

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

	cur_t = None
	primary = []
	for t in tables:
		if cur_t is not None and t['name'] != cur_t['name']:
			sqldesc['sql_string'] = fieldsSQL
			fields = db.sqlExecute(sqldesc,{'table_name':cur_t['name']})
			primary = [ i for i in primary if i is not None ]
			cur_t['primary'] = ','.join(primary)
			writeTableDefinitionXlsx(sys.argv[2],cur_t,fields)
			primary = []
		cur_t = t
		primary.append(t['primary'])

	conn.close()
