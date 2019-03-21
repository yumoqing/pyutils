import sys
import os
import codecs
from appPublic.myImport import myImport
from appPublic.dictObject import DictObject,dictObjectFactory
from appPublic.unicoding import uDict
from patterncoding.myTemplateEngine import MyTemplateEngine

try:
	import psycopg2
except:
	pass
try:
	import sqlite3
except:
	pass
try:
	import pymssql
except:
	pass
try:
	import ibm_db
except:
	pass
try:
	import cx_Oracle
except:
	pass
import os  
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

import ujson as json

import re

from appPublic.argsConvert import ArgsConvert,ConditionConvert

class SQLorException(Exception,object):
	def __int__(self,**kvs):
		supper(SQLException,self).__init__(self,**kvs)
		self.dic = {
			'response':'error',
			'errtype':'SQLor',
			'errmsg':supper(SQLException,self).message,
		}
		
	def __str__(self):
		return 'errtype:%s,errmsg=%s' % (self.dic['errtype'],self.dic['errmsg'])
	
def setValues(params,ns):
	r = ns.get(params,os.getenv(params))
	return r
		
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

def readsql(fn):
	f = codecs.open(fn,'r','utf-8')
	b = f.read()
	f.close()
	return b

def opendb(dbdef):
	driver = __import__(dbdef['driver'])
	conn = driver.connect(**dbdef['kwargs'])
	return conn

class SQLResult(object):
	def __init__(self,cur,klass=DictObject):
		self.cur = cur
		self.autoID = 0
		self.klass =klass
		self.fields = [ 'field_%04d' % self.newAutoID() if f == '' else f[0].lower() for f in  cur.description ]
	
	def __del__(self):
		self.cur.close()
		
	def newAutoID(self):
		ret = self.autoID
		self.autoID = self.autoID + 1
		return ret
	
	def __iter__(self):
		return self
	
	def __next__(self):
		rec = self.cur.fetchone()
		if rec is None:
			self.cur.close()
			raise StopIteration
		d = {}
		for i in range(len(rec)):
			d.update({self.fields[i]:rec[i]})
		#print('d=',d,'klass=',self.klass,type(self.klass))
		d = uDict(d,coding='utf8')
		obj = dictObjectFactory(self.klass,**d)
		#print('here')
		return obj

class NullIterator(object):
	def __init__(self):
		pass
	def __iter__(self):
		return self
	def __next__(self):
		raise StopIteration
	
class SQLor(object):
	def __init__(self,dbdesc=None,sqltp = '$[',sqlts = ']$',sqlvp = '${',sqlvs = '}$'):
		self.conn = None
		self.sqltp = sqltp
		self.sqlts = sqlts
		self.sqlvp = sqlvp
		self.sqlvs = sqlvs
		self.dbdesc = dbdesc
		self.writer = None
		self.convfuncs = {}
		self.cc = ConditionConvert()
	
	def grammar(self):
		return {
			'select':None,
		}
		
	def getConn(self):
		return self.conn
	
	def _opendb(self):
		driver = myImport(self.dbdesc['driver'])
		try:
			if self.dbdesc['driver'] == 'cx_Oracle' and self.dbdesc['kwargs'].get('user') == 'sys':
				conn = driver.connect(
					self.dbdesc['kwargs'].get('user'),
					self.dbdesc['kwargs'].get('password'),
					self.dbdesc['kwargs'].get('dsn'),
					cx_Oracle.SYSDBA)
			else:
				conn = driver.connect(**self.dbdesc['kwargs'])
			self.conn = conn
		except Exception as e:
			print('dbdesc=',self.dbdesc)
			raise e
	
	def setConvertFunction(self,typ,func):
		self.convfuncs.update({typ:func})
	
	def convert(self,typ,value):
		if self.convfuncs.get(typ,None) is not None:
			return self.convfuncs[typ](value)
		return value
	@classmethod
	def isMe(self,name):
		if name=='sqlor':
			return True
	def setWriter(self,writer):
		self.writer = writer
		
	def pagingSQLmodel(self):
		return u""
		
	def placeHolder(self,varname):
		if varname=='__mainsql__' :
			return ''
		return '?'
	
	def dataConvert(self,dataList):
		return [ i.get('value',None) for i in dataList]
	
	def dataList(self,k,v):
		a = []
		a.append({'name':k,'value':v})
		return a
		
	def cursor(self):
		return self.conn.cursor()
	
	def recordCnt(self,sql):
		ret = u"""select count(*) rcnt from (%s) rowcount_table""" % sql
		return ret
	
	def pagingSQL(self,sql,paging,NS):
		"""
		default it not support paging
		"""
		page = int(NS.get(paging['pagename'],1))
		rows = int(NS.get(paging['rowsname'],10))
		sort = NS.get(paging.get('sortname','sort'),None)
		order = NS.get(paging.get('ordername','asc'),'asc')
		if not sort:
			return sql
		if page < 1:
			page = 1
		from_line = (page - 1) * rows + 1
		end_line = page * rows + 1
		psql = self.pagingSQLmodel()
		ns={
			'from_line':from_line,
			'end_line':end_line,
			'rows':rows,
			'sort':sort,
			'order':order,
		}
		ac = ArgsConvert('$[',']$')
		psql = ac.convert(psql,ns)
		retSQL=psql % sql
		return retSQL
	
	def filterSQL(self,sql,filters,NS):
		ac = ArgsConvert('$[',']$')
		fbs = []
		for f in filters:
			vars = ac.findAllVariables(f)
			if len(vars) > 0:
				ignoreIt = False
				for v in vars:
					if not NS.get(v,False):
						ignoreIt = True
				if not ignoreIt:
					f = ac.convert(f,NS)
				else:
					f = '1=1'
			fbs.append(f)
		fb = ' '.join(fbs)
		retsql = u"""select * from (%s) filter_table where %s""" % (sql,fb)
		return retsql
		
	def runVarSQL(self,cursor,sql,NS):
		"""
		using a opened cursor to run a SQL statment with variable, the variable is setup in NS namespace
		return a cursor with data
		"""					
		isMainSQL,markedSQL,datas = self.maskingSQL(sql,NS)
		datas = self.dataConvert(datas)
		try:
			markedSQL = markedSQL.encode('utf8')
			cursor.execute(markedSQL,datas)
		except Exception as e:
			print( "markedSQL=",markedSQL,datas,e)
			raise e
		return isMainSQL
			
	def maskingSQL(self,org_sql,NS):
		"""
		replace all ${X}$ format variable exception named by '__mainsql__' in sql with '%s', 
		and return the marked sql sentent and variable list
		sql is a sql statment with variable formated in '${X}$
		the '__mainsql__' variable use to identify the main sql will outout data.
		NS is the name space the variable looking for, it is a variable dictionary 
		return (isMainSQL,MarkedSQL,list_of_variable)
		"""
		sqltextAC = ArgsConvert(self.sqltp,self.sqlts)
		sqlargsAC = ArgsConvert(self.sqlvp,self.sqlvs)
		sql1 = sqltextAC.convert(org_sql,NS)
		cc = ConditionConvert()
		sql1 = cc.convert(sql1,NS)
		vars = sqlargsAC.findAllVariables(sql1)
		phnamespace = {}
		[phnamespace.update({v:self.placeHolder(v)}) for v in vars]
		m_sql = sqlargsAC.convert(sql1,phnamespace)
		isMainSQL = True if '__mainsql__' in vars else False
		newdata = []
		for v in vars:
			if v != '__mainsql__':
				value = sqlargsAC.getVarValue(v,NS,None)
				newdata += self.dataList(v,value)
		
		return (isMainSQL,m_sql,newdata)
		
	def execute(self,sql,value,callback,*args,**kwargs):
		cur = self.cursor()
		self.runVarSQL(cur,sql,value)
		if callback is not None:
			fields = [ i[0].lower() for i in cur.description ]
			rec = cur.fetchone()
			while rec is not None:
				dic = {}
				for i in range(len(fields)):
					dic.update({fields[i]:rec[i]})
				dic = uDict(dic,coding='utf8')
				obj = DictObject(**dic)
				callback(obj,*args,**kwargs)
				rec = cur.fetchone()
		
			r = cur.fetchone()
			while r:
				callback(r)
				r = cur.fetchone()
		cur.close()

	def isOK(self):
		try:
			self.execute('select 1 as cnt',{});
			return True
		except:
			return False
	
	def executemany(self,sql,values):
		cur = self.cursor()
		try:
			isMainSQL,markedSQL,datas = self.maskingSQL(sql,{})
			datas = [ self.dataConvert(d) for d in values ]
			cur.executemany(markedSQL,datas)
			self.conn.commit()
		except Exception as e:
			print( "executemany():error",e,markedSQL)
			self.conn.rollback()
		cur.close()
	
	def pivotSQL(self,tablename,rowFields,columnFields,valueFields):
		def maxValue(columnFields,valueFields,cfvalues):
			sql = ''
			for f in valueFields:
				i = 0			
				for field in columnFields:
					for v in cfvalues[field]:
						sql += """
		,sum(%s_%d) %s_%d""" % (f,i,f,i)
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
	
		cfvalues={}
		for field in columnFields:
			sqlstring = 'select distinct %s from %s' % (field,tablename)
			v = []
			self.execute(sqlstring,{},lambda x: v.append(x))
			cfvalues[field] = [ i[field] for i in v ]
		
		sql ="""
	select """ + ','.join(rowFields)
		sql += maxValue(columnFields,valueFields,cfvalues)
		sql += """ from 
	(select """  + ','.join(rowFields)
		sql += casewhen(columnFields,valueFields,cfvalues)
		sql += """
	from %s)
	group by %s""" % (tablename,','.join(rowFields))
		return sql
		
	def pivot(self,desc,tablename,rowFields,columnFields,valueFields):
		sql = self.pivotSQL(tablename,rowFields,columnFields,valueFields)
		desc['sql_string'] = sql
		ret = []
		return self.execute(sql,{},lambda x:ret.append(x))

	def sqlIterator(self,desc,NS):
		klass = desc.get('classname','DictObject')
		cur = self.cursor()
		rowcount = desc.get('count',False)
		ret = []
		if 'sql_file' in desc.keys():
			sql = readsql(desc['sql_file'])
		else:
			sql = desc['sql_string']
		ss = sql.split(';')
		singleSQL = True
		if len(ss)>1:
			singleSQL = False
		try:
			for s in ss:
				isMainSQL = False
				try:
					if singleSQL and desc.get('filters',False):
						s = self.filterSQL(s,desc.get('filters'),NS)
					if rowcount:
						if singleSQL:
							s = self.recordCnt(s)
					else:
						if singleSQL and desc.get('paging',False):
							if desc.get('sortfield',False):
								NS['sort'] = desc.get('sortfield')
							s = self.pagingSQL(s,desc.get('paging'),NS)
					isMainSQL = self.runVarSQL(cur,s,NS)
					if singleSQL:
						isMainSQL = True
					if isMainSQL:
						result = SQLResult(cur,klass)
						return result
				except Exception as e:
					print( "exception=!",e)
					cur.close()
					raise e
			self.conn.commit()
		except Exception as e:
			print( "exception=!--",e)
			self.conn.rollback()
		cur.close()
		return NullIterator()
	
	def sqlExecute(self,desc,NS,rowcount=False):
		cur = self.cursor()
		ret = []
		if 'sql_file' in desc.keys():
			sql = readsql(desc['sql_file'])
		else:
			sql = desc['sql_string']
		ss = sql.split(';')
		singleSQL = True
		can_paging = True
		if len(ss)>1:
			singleSQL = False
		try:
			for s in ss:
				isMainSQL = False
				try:
					if singleSQL and desc.get('filters',False):
						s = self.filterSQL(s,desc.get('filters'),NS)
					if rowcount:
						if singleSQL:
							s = self.recordCnt(s)
					else:
						if singleSQL and desc.get('paging',False):
							if desc.get('sortfield',False):
								NS['sort'] = desc.get('sortfield')
							s = self.pagingSQL(s,desc.get('paging'),NS)
					isMainSQL = self.runVarSQL(cur,s,NS)
					if singleSQL:
						isMainSQL = True
				except Exception as e:
					print( "exception=",e)
					if 'ignore_error' not in desc.keys():		
						raise e
				if isMainSQL:
					if self.writer is not None:
						self.writer(cur,NS)
			self.conn.commit()
			if self.writer is not None:
				ret = self.writer.getResult()
		except Exception as e:
			print( e)
			self.conn.rollback()
		cur.close()
		return ret
	
	def tables(self):
		sqlstring = self.tablesSQL()
		ret = []
		self.execute(sqlstring,{},lambda x:ret.append(x))
		return ret
	
	def indexesSQL(self,tablename):
		"""
		record of {
			index_name,
			index_type,
			table_name,
			column_name
		}
		"""
		return None
		
	def indexes(self,tablename=None):
		sqlstring = self.indexesSQL(tablename.lower())
		if sqlstring is None:
			return []
		recs = []
		self.execute(sqlstring,{},lambda x:recs.append(x))
		return recs
		
	def fields(self,tablename=None):
		sqlstring = self.fieldsSQL(tablename)
		recs = []
		self.execute(sqlstring,{},lambda x:recs.append(x))
		ret = []
		for r in recs:
			r.update({'type':self.db2modelTypeMapping.get(r['type'].lower(),'unknown')})
			r.update({'name':r['name'].lower()})
			ret.append(r)
		return ret
	
	def primary(self,tablename):
		sqlstring = self.pkSQL(tablename)
		recs = []
		self.execute(sqlstring,{},lambda x:recs.append(x))
		return recs
		
	def fkeys(self,tablename):
		sqlstring = self.fkSQL(tablename)
		recs = []
		self.execute(sqlstring,{},lambda x:recs.append(x))
		return recs
	
	def createTable(self,tabledesc):
		te = MyTemplateEngine([],'utf8','utf8')
		desc = {
			"sql_string":te.renders(self.ddl_template,tabledesc)
		}
		return self.sqlExecute(desc,{})
		
	def getTableDesc(self,tablename):
		desc = {}
		summary = [ i for i in self.tables() if tablename.lower() == i.name ]
		primary = [i.field_name for i in self.primary(tablename) ]
		summary['primary'] = primary
		desc['summary'] = summary
		desc['fields'] = self.fields(tablename=tablename)
		desc['validation'] = []
		idx = {}
		for idxrec in self.indexes(tablename=tablename):
			if idxrec.index_name != idx.get('name',None):
				if idx != {}:
					desc['validation'].append(idx)
					idx = {
						'fields':[]
					}
				else:
					idx['fields'] = []
				idx['name'] = idxrec.index_name
				idx['oper'] = 'idx'
			idx['fields'].append(idxrec.field_name)
		if idx != {}:
			desc['validation'].append(idx)		
		return desc
	
		
				
