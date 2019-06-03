#import cx_Oracle
import os,sys
import ujson
import codecs
from sqlor import sqlorFactory,opendb
import sqlor
import mssqlor
import oracleor

def sqlexec(conn,cmd):
	cur = conn.cursor()
	cur.execute(cmd)
	ret = []
	for i in cur:
		ret.append(i[0])
	cur.close()
	return ret
	
def maxValue(columnFields,valueFields,cfvalues):
	sql = ''
	for f in valueFields:
		i = 0			
		for field in columnFields:
			for v in cfvalues[field]:
				sql += """
,max(%s_%d) %s_%d""" % (f,i,f,i)
				i+=1
	return sql

def casewhen(columnFields,valueFields,cfvalues):
	sql = ''
	for f in valueFields:
		i = 0			
		for field in columnFields:
			for v in cfvalues[field]:
				if v is None:
					sql += """,case when %s is null then %s
	else 0 end as %s_%d  -- %s
""" % (field,f,f,i,v)
				else:
					sql += """,case when trim(%s) = trim('%s') then %s
	else 0 end as %s_%d  -- %s
""" % (field,v,f,f,i,v)
				
				i += 1
	return sql
	
def createPivotView(conn,viewname,tablename,rowFields,columnFields,valueFields):
	cfvalues={}
	for field in columnFields:
		v = sqlexec(conn,'select distinct %s from %s' % (field,tablename));
		cfvalues[field] = v
	
	sql = "create or replace view %s as" %(viewname)
	sql +="""
select """ + ','.join(rowFields)
	sql += maxValue(columnFields,valueFields,cfvalues)
	sql += """ from 
(select """  + ','.join(rowFields)
	sql += casewhen(columnFields,valueFields,cfvalues)
	sql += """
from %s)
group by %s""" % (tablename,','.join(rowFields))
	
	return sql
	
if __name__ == '__main__':
	f = codecs.open(sys.argv[1],'r','utf-8')
	dbdesc = ujson.load(f)
	f.close()
	conn = opendb(dbdesc)
	tablename = 'RPT_Tran_History'
	viewname = 'view_tran_history1'
	rowFields = ['PortfolioID','SECURITYID']
	valueFields = ['TradeAmount','TradePrice']
	columnFields = ['TradeBusinessType','TradeType']
	sql = createPivotView(conn,viewname,tablename,rowFields,columnFields,valueFields)
	print( sql)
	conn.close()
