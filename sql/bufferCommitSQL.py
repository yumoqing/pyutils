"""
env = BufferCommitSQL(dbname,100000)

@env.runSQL
def sql(ns)
	desc = {
		"sql_string":"insert ......"
	}
	return desc

env.End()
"""
from functools import wraps 
from sql.sqlorAPI import DBPools
import re

class BufferCommitSQL:
	def __init__(self,dbname,buffersize=10000):
		self.dbname = dbname
		self.totalcnt = 0
		self.dbp = DBPools()
		self.sor = self.dbp.getSqlor(dbname)
		if self.sor is None:
			raise Exception('sqlor is None,' + dbname)
		self.cur = self.sor.cursor()
		self.buffersize = buffersize
		self.sqlcnt = 0
	
	def runSQL(self,func):
		@wraps(func)
		def func_wrapper(ns,*args,**kwargs):
			desc = func(ns,*args,**kwargs)
			sql = desc.get('sql_string',None)
			if sql is None:
				return
			if desc.get('tmplsql',False):
				# tmplRender
				pass
			sqlcmd = sql.split(';')
			for s in sqlcmd:
				x = re.sub('[\t\r\n ]','',s)
				if x == '':
					continue
				self.sor.runVarSQL(self.cur,s,ns)
			self.sqlcnt += 1
			self.totalcnt += 1
			if self.sqlcnt >= self.buffersize:
				self.sor.conn.commit()
				self.sqlcnt = 0
			
		return func_wrapper
	
	def finish(self):
		if self.sqlcnt > 0:
			self.sor.conn.commit()
			
	def __del__(self):
		try:
			self.cur.close()
			self.cur = None
		except:
			pass
		try:
			self.dbp.freeSqlor(self.dbname,self.sor)
			self.sor = None
		except:
			pass
