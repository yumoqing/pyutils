# 
import threading
from functools import wraps 
from appPublic.dictObject import DictObject
import codecs
from appPublic.Singleton import SingletonDecorator
from appPublic.jsonConfig import getConfig
from queue import Queue
# from writerAPI import writerFactory

from sql import sqlor
from sql import mssqlor
from sql import oracleor
from sql import sqlite3or
from sql import mysqlor

from appPublic.myjson import loadf

def opendb(dbdef):
	driver = __import__(dbdef['driver'])
	if dbdef['driver'] == 'cx_Oracle' and dbdef['kwargs'].get('user') == 'sys':
		conn = driver.connect(dbdef['kwargs'].get('user'),dbdef['kwargs'].get('password'),dbdef['kwargs'].get('dsn'),cx_Oracle.SYSDBA)
	else:
		conn = driver.connect(**dbdef['kwargs'])
	return conn
	
def sqlorFactory(dbdesc,conn=None):
	driver = dbdesc.get('driver',dbdesc)
	def findSubclass(name,klass):
		for k in klass.__subclasses__():
			if k.isMe(name):
				return k
			k1 = findSubclass(name,k)
			if k1 is not None:
				return k1
		return None
	k = findSubclass(driver,sqlor.SQLor)
	if k is None:
		return sqlor.SQLor(dbdesc=dbdesc)
	return k(dbdesc=dbdesc)

def sqlorFromFile(dbdef_file,coding='utf8'):
	dbdef = loadf(dbdef_file)
	return sqlorFactory(dbdef)
	
class ConnectionPool(object):
	def __init__(self,dbdesc):
		self.dbdesc = dbdesc
		self.maxconn = dbdesc.get('maxconn',5)
		self._pool = Queue(self.maxconn)
		self._fillPool()
		self.using = []
	
	def _fillPool(self):
		while not self.isFull():
			sor = sqlorFactory(self.dbdesc)
			sor._opendb()
			try:
				self._pool.put(sor)
			except Exception as e:
				sor.getConn.close()
				raise e
	
	def isEmpty(self):
		return self._pool.empty()
	
	def isFull(self):
		return self._pool.full()
		
	def get(self):
		try:
			sor = self._pool.get()
			self.using.append(sor)
			return sor
		except Exception as e:
			raise e
	def free(self,sor):
		try:
			self.using = [s for s in self.using if s != sor]
			self._pool.put(sor)
		except Exception as e:
			raise e
			
	def __del__(self):
		while 1:
			try:
				sor = self._pool.get(False)
				sor.conn.close()
			except:
				return

@SingletonDecorator
class DBPools:
	def __init__(self,databases={}):
		self._cpools = {}
		self.threadsors = {}
		self.databases = databases
		"""
		for name,dbdesc in self.databases.items():
			dbdesc.update({name:name})
			self._cpools.update({name:ConnectionPool(dbdesc)})
		"""
	
	def poolkey(self,name):
		return name + str(threading.get_ident())
		
	def initPool(self,name,dbdesc):
		dbdesc.update({name:name})
		self._cpools[self.poolkey(name)] = ConnectionPool(dbdesc)
		#print('initPool() keys=',self._cpools.keys())
		
	def status(self):
		s = {}
		[s.update({name:{'isEmpty':cp.isEmpty(),'isFull':cp.isFull()}}) for name,cp in self._cpools.items() ]
		return s
	
	def using(self):
		return self.threadsors
	
	def getSqlor(self,name):
		dbdesc = self.databases.get(name,None)
		if dbdesc is None:
			print('return None,if dbdesc is None',name)
			return None
		if type(dbdesc) == type(''):
			return self.getSqlor(dbdesc)
			
		key = self.poolkey(name)
		pool = self._cpools.get(key,False)
		if not pool:
			self.initPool(name,dbdesc)
		pool = self._cpools.get(key,None)
		if pool is None:
			print('return None,if pool is None',key,self._cpools.keys())
			return None
		sor = self._cpools[key].get()
		sor.name = name
		if not sor.isOK():
			sor._opendb()
		return sor
	
	def freeSqlor(self,name,sor):
		if name is None:
			name = sor.name
		dbdesc = self.databases.get(name,None)
		if dbdesc is None:
			print('return None,if dbdesc is None',name)
			return None
		if type(dbdesc) == type(''):
			return self.freeSqlor(dbdesc,sor)
			
		pool = self._cpools.get(self.poolkey(name),None)
		if pool is None:
			raise Exception('%s:connection pool is null' % name)
		return pool.free(sor)
	
	def freeAll(self):
		pks = self._cpools.keys()
		tid = str(threading.get_ident())
		for k in pks:
			if tid == k[-len(tid):]:
				pool = self._cpools.get(k,None)
				if pool is None:
					raise Exception('%s:connection pool is null' % k)
				for sor in pool.using:
					pool.free(sor)
				return
		

def getSqlorByName(name):
	pools = DBPools()
	return pools.getSqlor(name)
	
def closeSqlorByName(name,sor):
	pools = DBPools()
	pools.freeSqlor(name,sor)

def runSQLIterator(func):
	@wraps(func)
	def func_wrapper(dbname,NS,*args,**kwargs):
		dbp = DBPools()
		sor = dbp.getSqlor(dbname)
		ret = None
		try:
			sqldesc =  func(dbname,NS,*args,**kwargs)
			ret = sor.sqlIterator(sqldesc,NS)
		except Exception as e:
			print('Exception:',e,dbname,NS)
			raise e
		finally:
			dbp.freeSqlor(dbname,sor)
		return ret
	return func_wrapper

def runSQLResultFields(func):
	@wraps(func)
	def func_wrapper(dbname,NS,*args,**kwargs):
		ns = {}
		ns.update(NS)
		ns['page'] = 1
		ns['rows'] = 1
		dbp = DBPools()
		sor = dbp.getSqlor(dbname)
		ret = None
		try:
			sqldesc =  func(dbname,NS,*args,**kwargs)
			mydesc = {}
			mydesc.update(sqldesc)
			mydesc.update(
				{		
					"paging":{
						"rowsname":"rows",
						"pagename":"page",
						"sortname":"sort",
						"ordername":"order"
					}
				})
			rzt = sor.sqlIterator(mydesc,ns)
			ret = [ {'name':i[0],'type':i[1]} for i in rzt.cur.description ]
			
		except Exception as e:
			print('Exception:',e,dbname,ns)
			raise e
		finally:
			dbp.freeSqlor(dbname,sor)
		return ret
	return func_wrapper


def runSQLPaging(func):
	@wraps(func)
	def func_wrapper(dbname,NS,*args,**kwargs):
		dbp = DBPools()
		sor = dbp.getSqlor(dbname)
		ret = None
		try:
			sqldesc =  func(dbname,NS,*args,**kwargs)
			cnt_desc = {}
			cnt_desc.update(sqldesc)
			cnt_desc.update({"count":True})
			data_desc = {}
			data_desc.update(sqldesc)
			data_desc.update(
			{		
				"paging":{
					"rowsname":"rows",
					"pagename":"page",
					"sortname":"sort",
					"ordername":"order"
				}
			})
			cntRet = [ i for i in sor.sqlIterator(cnt_desc,NS) ]
			dataRet = [ i for i in sor.sqlIterator(data_desc,NS) ]
			ret = {'total':cntRet[0].rcnt,'rows':dataRet}	
		except Exception as e:
			print('Exception:',e,dbname,NS)
			raise e
		finally:
			dbp.freeSqlor(dbname,sor)
		return ret
	return func_wrapper


def sqlGrammar(dbname):
	dbp = DBPools()
	sor = dbp.getSqlor(dbname)
	g = sor.grammar()
	dbp.freeSqlor(dbname,sor)
	return g
	
def runSQL(func):
	@wraps(func)
	def func_wrapper(dbname,NS,*args,**kwargs):
		dbp = DBPools()
		sor = dbp.getSqlor(dbname)
		ret = None
		try:
			sqldesc =  func(dbname,NS,*args,**kwargs)
			w = sqldesc.get('writer',None)
			ret = sor.sqlExecute(sqldesc,NS)
		except Exception as e:
			print('Exception:',e,dbname,NS)
			raise e
		finally:
			dbp.freeSqlor(dbname,sor)
		return  ret
	return func_wrapper

def getTables(dbname):
	dbp = DBPools()
	sor = dbp.getSqlor(dbname)
	ret = None
	try:
		ret = sor.tables()
	finally:
		dbp.freeSqlor(dbname,sor)
	return  ret

def getTableFields(dbname,tblname):
	dbp = DBPools()
	sor = dbp.getSqlor(dbname)
	ret = None
	try:
		ret = sor.fields(tblname)
	finally:
		dbp.freeSqlor(dbname,sor)
	return  ret

def getTablePrimaryKey(dbname,tblname):
	dbp = DBPools()
	sor = dbp.getSqlor(dbname)
	ret = None
	try:
		ret = sor.primary(tblname)
	finally:
		dbp.freeSqlor(dbname,sor)
	return  ret
	
def getTableForignKeys(dbname,tblname):
	dbp = DBPools()
	sor = dbp.getSqlor(dbname)
	ret = None
	try:
		ret = sor.fkeys(tblname)
	finally:
		dbp.freeSqlor(dbname,sor)
	return  ret
	
