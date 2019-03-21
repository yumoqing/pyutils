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
	if f['type'].lower() in ['varchar','nvarchar'] :
		return 'str'
	if f['type'].lower() == 'text':
		return 'text'
	if f['type'].lower() == 'date':
		return 'date'
	if f['type'].lower()[:9] == 'datetime':
		return 'datetime'
	if f['type'] == 'bigint':
		return 'long'
	if f['type'].lower() == 'numeric' and (f['dec'] is None or f['dec'] == '' or f['dec'] == 0):
		return 'long'
	if f['type'].lower() == 'numeric':
		return 'float'

	return f['type']
	
def xlwtWriteRecord(ws,x,y,rec):
	for r in rec:
		ws.write(x,y,r)
		y += 1
def toUnicode(d):
	t = type(d)
	if t == type(u''):
		return d
	if t == type(''):
		try:
			return d.decode('utf8')
		except:
			try:
				return d.decode('gb2312')
			except:
				print( "fail to convert to unicode",d)
				return u''
	return d
	
def writeTableDefinitionXlsx(path,summary,fields):
	wb = xlwt.Workbook()
	ws = wb.add_sheet('summary',cell_overwrite_ok=True)
	xlwtWriteRecord(ws,0,0,["name","title","primary","catelog"])
	if summary['title'] is None:
		summary['title'] = ''
	ws.write(1,0,toUnicode(summary['name'].lower()))
	ws.write(1,1,toUnicode(summary['title'].decode('utf-8')))
	ws.write(1,2,toUnicode(summary['primary']))
	
	ws = wb.add_sheet('fields',cell_overwrite_ok=True)
	xlwtWriteRecord(ws,0,0,["name","title","type","length:int","dec:int","nullable","default","comments"])
	i = 1
	for f in fields:
		if f['title'] is None:
			f['title'] = ''
		ws.write(i,0,toUnicode(f['name'].lower()))
		ws.write(i,1,toUnicode(f['title']))
		ws.write(i,2,getType(f))	
		ws.write(i,3,f['length'])	
		ws.write(i,4,f['dec'])	
		ws.write(i,5,f['nullable'])	
		i += 1
	ws = wb.add_sheet('data',cell_overwrite_ok=True)
	fs = [ toUnicode(f['name'].lower()) for f in fields ]
	xlwtWriteRecord(ws,0,0,fs)
	ws = wb.add_sheet('validation',cell_overwrite_ok=True)
	xlwtWriteRecord(ws,0,0,['name',	'oper',	'value'])

	fn = os.path.join(path,'%s.xls' % summary['name'])
	wb.save(fn)
if __name__ == '__main__':
	if len(sys.argv) < 3:
		print( """a SQL Server schema acheive tool
	Usage:
	%s dbdesc_json output_path
	examples of dbdesc_json:
	{
		"driver":"mysql",
		"kwargs":{
			"user":"ymq",
			"password":"ymq123",
			"host":"localhost",
			"database":"ambi"
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
	summarysSQL = """
	select 
	d.name,
	Isnull(f.VALUE,d.name) title,
	a.column_name pk
	from sysobjects d left join
	(
		SELECT table_name,column_name,ordinal_position FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
	) a on (a.table_name = d.name)
				  AND (d.xtype = 'U')
				  AND (d.name <> 'dtproperties') 
	left join sys.extended_properties f on d.id = f.major_id and f.minor_id = 0
	where d.xtype = 'U'
	"""

	fieldsSQL="""SELECT name = a.name
		   ,type = b.name
		   ,length = Columnproperty(a.id,a.name,'PRECISION')
		   ,dec = Isnull(Columnproperty(a.id,a.name,'Scale'),null)
		   ,nullable = CASE 
					WHEN a.isnullable = 1 THEN 'yes'
					ELSE 'no'
				  END
		   ,defaultv = Isnull(e.TEXT,'')
		   ,title = Isnull(g.[value],a.name) 
	FROM     syscolumns a
			 LEFT JOIN systypes b
			   ON a.xusertype = b.xusertype
			 INNER JOIN sysobjects d
			   ON (a.id = d.id)
				  AND (d.xtype = 'U')
				  AND (d.name <> 'dtproperties') 
			  INNER JOIN  sys.all_objects c
				ON d.id=c.object_id 
					AND  schema_name(schema_id)='dbo'
			 LEFT JOIN syscomments e
			   ON a.cdefault = e.id
			 LEFT JOIN sys.extended_properties g
			   ON (a.id = g.major_id)
				  AND (a.colid = g.minor_id)
			 LEFT JOIN sys.extended_properties f
			   ON (d.id = f.major_id)
				  AND (f.minor_id = 0)
	where d.name=${table_name}$
	ORDER BY a.id
			 ,a.colorder
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

	cur_t = None
	primary = []
	for t in tables:
		if cur_t is not None and t['name'] != cur_t['name']:
			print( cur_t['name'])
			sqldesc['sql_string'] = fieldsSQL
			fields = db.sqlExecute(sqldesc,{'table_name':cur_t['name']})
			primary = [ i for i in primary if i is not None ]
			cur_t['primary'] = ','.join(primary)
			writeTableDefinitionXlsx(sys.argv[2],cur_t,fields)
			primary = []
		cur_t = t
		primary.append(t['pk'])

	conn.close()
