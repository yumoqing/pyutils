# -*- coding:utf8 -*-
from sql.sqlorAPI import DBPools,runSQL,runSQLIterator,getTableFields,getTablePrimaryKey,getTableForignKeys
from sql.filter import DBFilter
from appPublic.objectAction import ObjectAction
from appPublic.dictObject import DictObject
from appPublic.timeUtils import  date2str,time2str,str2Date
toStringFuncs={
	'char':None,
	'str':None,
	'short':str,
	'long':str,
	'float':str,
	'date':date2str,
	'time':time2str,
}
fromStringFuncs={
	'short':int,
	'long':int,
	'float':float,
	'date':str2Date,
	'time':str2Date
}

class CRUD(object):
	def __init__(self,dbname,rows=10):
		self.dbname = dbname
		self.rows = rows
		self.oa = ObjectAction()
		
	def primaryKey(self,tablename):
		data = getTablePrimaryKey(self.dbname,tablename)
		return data
	
	def forignKeys(self,tablename):
		data = getTableForignKeys(self.dbname,tablename)
		return data
		
	def I(self,tblname):
		"""
		fields information
		"""
		pks = [ i.field_name for i in self.primaryKey(tblname) ]
		data = getTableFields(self.dbname,tblname)
		[ d.update({'primarykey':True}) for d in data if d.name in pks ]
		data = self.oa.execute(self.dbname+'_'+tblname,'tableInfo',data)
		return data
	
	def fromStr(self,tablename,data):
		fields = getTableFields(self.dbname,tablename)
		ret = {}
		for k in data:
			v = None if data[k] == '' else data[k]
			for f in fields:
				if k == f.name:
					ret[k] = v
					f = fromStringFuncs.get(f.type,None)
					if f is not None and v is not None:
						ret[k] = f(v)
		return ret
	
	def toStr(self,tablename,data):
		fields = getTableFields(self.dbname,tablename)
		ret = {}
		for k in data:
			for f in fields:
				if k == f.name:
					ret[k] = data[k]
					f = toStringFuncs.get(f.type,None)
					if f is not None and data[k] is not None:
						ret[k] = f(data[k])
		return ret
		
	def datagrid(self,request,tablename,target):
		fields = self.I(tablename)
		fs = [ self.defaultIOField(f) for f in fields ]
		id = self.dbname+':'+tablename
		pk = self.primaryKey(tablename)
		print('primary key=',pk)
		idField = pk[0].field
		data = {
			"tmplname":"widget_js.tmpl",
			"data":{
				"__ctmpl__":"datagrid",
				"__target__":target,
				"data":{
					"name":id,
					"icon-conv":"icon-table",
					"title":tablename,
					"url":absurl('./RP.dspy?id=%s' % id),
					"deleteUrl":absurl('./D.dspy?id=%s' % id),
					"addUrl":absurl('./C.dspy?id=%s' % id),
					"updateUrl":absurl('./U.dspy?id=%s' % id),
					"idField":idField,
					"dnd":True,
					"view":"scrollview",
					"fields":fs,
					"toolbar":{
						"tools":[
							{
								"name":"add",
								"icon":"icon-add",
								"label":"add ball"
							},
							{
								"name":"delete",
								"icon":"icon-delete",
								"label":"delete ball"
							},
							{
								"name":"moveup",
								"icon":"icon-up",
								"label":"moveup ball"
							},
							{
								"name":"movedown",
								"icon":"icon-down",
								"label":"movedown ball"
							}
						]
					},
					"options":{
						"pageSize":50,
						"pagination":False
					}
				}
			}
		}
		data = self.oa.execute(id,'datagrid',data)
		return data
		
	def defaultIOField(self,f):
		
		if f.type in ['str']:
			return {
				"primarykey":f.get('primarykey',False),
				"name":f.name,
				"hidden":False,
				"sortable":True,
				"label":f.title,
				"align":"center",
				"iotype":"text"	
			}
		if f.type in ['float','short','long']:
			return {
				"primarykey":f.get('primarykey',False),
				"sortable":True,
				"name":f.name,
				"hidden":False,
				"label":f.title,
				"align":"right",
				"iotype":"text"	
			}
		return {
			"primarykey":f.get('primarykey',False),
			"name":f.name,
			"sortable":True,
			"hidden":False,
			"label":f.title,
			"align":"center",
			"iotype":"text"	
		}

	def C(self,tblname,rec):
		"""
		create new data
		"""
		fields = getTableFields(self.dbname,tblname)
		flist = [ f['name'] for f in fields ]
		fns = ','.join(flist)
		vfs = ','.join([ '${' + f + '}$' for f in flist ])
		data = {}
		[ data.update({k.lower():v}) for k,v in rec.items() ]
		@runSQL
		def addSQL(dbname,data):
			sqldesc={
				"sql_string" : """
				insert into %s (%s) values (%s)
				""" % (tblname,fns,vfs),
			}
			return sqldesc
			
		data = self.oa.execute(self.dbname+'_'+tblname,'beforeAdd',data)
		addSQL(self.dbname,data)
		data = self.oa.execute(self.dbname+'_'+tblname,'afterAdd',data)
		return data
	
	def defaultFilter(self,tblname,NS):
		fields = getTableFields(self.dbname,tblname)
		d = [ '%s = ${%s}$' % (f.name,f.name) for f in fields if f.name in NS.keys() ]
		if len(d) == 0:
			return ''
		ret = ' and ' + ' and '.join(d)
		#print('defaultFilter=',ret)
		return ret

	def R(self,tblname,filters=None,NS={}):
		"""
		retrieve data
		"""
		@runSQLIterator
		def retrieve(dbname,data,filterString):
			sqldesc = {
				"sql_string":"""select * from %s where 1=1 %s""" % (tblname,filterString),
			}
			return sqldesc
			
		fstr = ''
		if filters is not None:
			fstr = ' and '
			dbf = DBFilter(filters)
			fstr = fstr + dbf.genFilterString()
		else:
			fstr = self.defaultFilter(tblname,NS)
		
		data = self.oa.execute(self.dbname+'_'+tblname,'beforeRetieve',NS)
		data = retrieve(self.dbname,data,fstr)
		#data = self.oa.execute(self.dbname+'_'+tblname,'afterRetieve',data)
		return data
		
	def RP(self,tblname,filters=None,NS={}):
		@runSQLIterator
		def totalCount(dbname,data,filterString):
			sqldesc = {
				"sql_string":"""select * from %s where 1=1 %s""" % (tblname,filterString),
				"count":True,
				"default":{'rows':self.rows}
			}
			return sqldesc
			
		@runSQLIterator
		def pagingdata(dbname,data,filterString):
			sqldesc = {
				"sql_string":"""select * from %s where 1=1 %s""" % (tblname,filterString),
				"paging":{
					"rowsname":"rows",
					"pagename":"page"
				},
				"default":{'rows':self.rows}
			}
			return sqldesc
			
		if not NS.get('sort',False):
			fields = getTableFields(self.dbname,tblname)
			NS['sort'] = fields[0]['name']
		fstr = ""
		if filters is not None:
			fstr = ' and '
			dbf = DBFilter(filters)
			fstr = fstr + dbf.genFilterString()
		else:
			fstr = self.defaultFilter(tblname,NS)
			
		rtv_cnt = [ i for i in totalCount(self.dbname,NS,fstr) ]
		total = rtv_cnt[0].rcnt
		d = [r for r in pagingdata(self.dbname,NS,fstr)]
		ret = {'total':total,'rows':d}
		return DictObject(**ret)

	def U(self,tblname,data):
		"""
		update  data
		"""
		@runSQL
		def update(dbname,NS,condi,newData):
			c = [ '%s = ${%s}$' % (i,i) for i in condi ]
			u = [ '%s = ${%s}$' % (i,i) for i in newData ]
			cs = ' and '.join(c)
			us = ','.join(u)
			sqldesc = {
				"sql_string":"""update %s set %s where %s""" % (tblname,us,cs)
			}
			return sqldesc
		
		pk = self.primaryKey(tblname)
		pkfields = [k.field_name for k in pk ]
		newData = [ k for k in data if k not in pkfields ]
		data = self.oa.execute(self.dbname+'_'+tblname,'beforeUpdate',data)
		update(self.dbname,data,pkfields,newData)
		data = self.oa.execute(self.dbname+'_'+tblname,'afterUpdate',data)
		return data
	
	def D(self,tblname,data):
		"""
		delete data
		"""
		@runSQL
		def delete(dbname,data,fields):
			c = [ '%s = ${%s}$' % (i,i) for i in fields ]
			cs = ' and '.join(c)
			sqldesc = {
				"sql_string":"delete from %s where %s" % (tblname,cs)
			}
			return sqldesc

		pk = self.primaryKey(tblname)
		pkfields = [k.field_name for k in pk ]
		data = self.oa.execute(self.dbname+'_'+tblname,'beforeDelete',data)
		delete(self.dbname,data,pkfields)
		data = self.oa.execute(self.dbname+'_'+tblname,'afterDelete',data)
		return data

class _CRUD(CRUD):
	def __init__(self,dbname,tablename,rows=10):
		super(_CRUD,self).__init__(dbname,rows=rows)
		self.tablename = tablename
		
	def primaryKey(self):
		return super(_CRUD,self).primaryKey(self.tablename)
	
	def forignKeys(self):
		return super(_CRUD,self).forignKeys(self.dbname,self.tablename)
		
	def I(self):
		return super(_CRUD,self).I(self.tablename)
		
	def fromStr(self,data):
		return super(_CRUD,self).fromStr(self.tablename,data)
		
	def toStr(self,data):
		return super(_CRUD,self).toStr(self.tablename,data)
		
	def C(self,rec):
		return super(_CRUD,self).C(self.tablename,rec)
		
	def R(self,filters=None,NS={}):
		return super(_CRUD,self).R(self.tablename,filters=filters,NS=NS)
		
	def RP(self,filters=None,NS={}):
		return super(_CRUD,self).RP(self.tablename,filters=filters,NS=NS)
		
	def U(self,data):
		return super(_CRUD,self).U(self.tablename,data)
		
	def D(self,data):
		return super(_CRUD,self).D(self.tablename,data)
	

if __name__ == '__main__':
	DBPools({
		"ambi":{
			"driver":"pymssql",
			"coding":"utf-8",
			"dbname":"ambi",
			"kwargs":{
				"user":"ymq",
				"database":"ambi",
				"password":"ymq123",
				"host":"localhost"
			}
		},
		"metadb":{
			"driver":"pymssql",
			"coding":"utf-8",
			"dbname":"metadb",
			"kwargs":{
				"user":"ymq",
				"database":"metadb",
				"password":"ymq123",
				"host":"localhost"
			}
		}
	})
	crud = CRUD('ambi')
	#fields = crud.I('cashflow')
	#for i in fields:
	#	print(i)
	
	data = crud.RP('cashflow')
	print(data.total)
	for i in data.rows:
		print(i.balance,i.asid)
		
