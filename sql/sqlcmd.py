import sys
import os
import ujson
from optparse import OptionParser
import pyodbc
import psycopg2
import sqlite3
import pymssql
#import ibm_db
import cx_Oracle
import ujson
import xlsxWriter
import re
from writer import writerFactory

def findNamedParameters(sql):
	"""
	return  a list of named parameters
	"""
	re1 = '\$\{[_a-zA-Z_][a-zA-Z_0-9]*\}'
	params1 = re.findall(re1,sql)
	return params1



def uniParams(params1):
	ret = []
	for i in params1:
		if i not in ret:
			ret.append(i)
	return ret

def setValues(params,ns):
	r = ns.get(params,os.getenv(params))
	if r == None:
		raise Exception('variable %s undefine' % params)
	return r
		
def maskingSQL(org_sql,NS,placeholder='?'):
	"""
	replace all ${X} format variable exception named by '__mainsql__' in sql with '%s', and return the marked sql sentent and variable list
	sql is a sql statment with variable formated in '${X}
	the '__mainsql__' variable use to identify the main sql will outout data.
	NS is the name space the variable looking for, it is a variable dictionary 
	return (isMainSQL,MarkedSQL,list_of_variable)
	"""
	params = findNamedParameters(org_sql)
	isMainSQL = True if '${__mainsql__}' in params else False
	p = []
	for i in params:
		if i != '${__mainsql__}':
			p.append(i)
	params = p
	unips = uniParams(params)
	cnt = len(params)
	sql = ''.join(org_sql.split('${__mainsql__}')) if isMainSQL else org_sql
	m_sql = ''
	newdata = []
	for i in range(cnt):
		k = params[i]
		k1 = k[2:-1]
		v = setValues(k1,NS)
		txt1,txt2 = sql.split(k,1)
		if type(v) == type([]) or type(v) == type(()):
			newdata += list(v)
			m_sql += txt1 + '(' + ','.join([placeholder] * len(v) ) + ')'
			sql = txt2
		else:
			newdata.append(v)
			m_sql += txt1 + placeholder
			sql = txt2
	m_sql += sql
	return (isMainSQL,m_sql,newdata)

def readsql(fn):
	f = open(fn,'r')
	b = f.read()
	f.close()
	return b

def runVarSQL(cursor,sql,NS,placeholder='?'):
	"""
	using a opened cursor to run a SQL statment with variable, the variable is setup in NS namespace
	return a cursor with data
	"""					
	isMainSQL,markedSQL,datas = maskingSQL(sql,NS,placeholder)
	print( "here ",markedSQL,datas)
	cursor.execute(markedSQL,datas)
	return isMainSQL

def opendb(dbdef):
	driver = __import__(dbdef['driver'])
	conn = driver.connect(**dbdef['kwargs'])
	return conn

def sqlExecute(conn,cur,desc,NS,placeholder='?'):
	ret = []
	if 'sql_file' in desc.keys():
		sql = readsql(desc['sql_file'])
	else:
		sql = desc['sql_string']
	if 'writer' in desc.keys():
		wd = desc['writer']
		writer = writerFactory(wd['filetype'],**wd['kwargs'])
	else:
		writer = None
		ret = []
	ss = sql.split(';')
	for s in ss:
		isMainSQL = False
		try:
			isMainSQL = runVarSQL(cur,s,NS,placeholder)
			if len(ss) == 1:
				isMainSQL = True
		except Exception as e:
			print( "sql execute error",e,s)
			if 'ignore_error' not in desc.keys():		
				raise e
		if isMainSQL:
			if writer is not None:
				writer(cur,NS)
		try:
			conn.commit()
		except:
			pass
	if writer is not None:
		ret = writer.getResult()
		del writer
		writer = None
	return ret
			
def sqlcommand(args,NS):
	ret = []
	for arg in args:
		try:
			f = open(arg,'r')
			desc = ujson.load(f)
		except Exception as  e:
			print( arg,e)
			continue
		finally:
			f.close()
		conn = opendb(desc['db'])
		cur = conn.cursor()
		sqlExecute(conn,cur,desc,NS)
		cur.close()
		conn.close()
	return ret

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print( "Usage:\n%s [var1=value1 var2=value2 ...] sqldesc.json")
		sys.exit(1)
	jsons = []
	NS = {}
	for arg in sys.argv[1:]:
		a = arg.split('=',1)
		if len(a) < 2:
			jsons.append(arg)
		else:
			NS[a[0]] = a[1]
			
	sqlcommand(jsons,NS)
	
