
# coding: utf-8

# In[1]:


import sys

from twisted.web import static
from twisted.web import server
from appPublic.unicoding import unicoding
from appPublic.jsonConfig import getConfig
from twisted.internet import reactor
from WebServer.myResource import MyResource
from sql.sqlorAPI import DBPools
from acBase import ACBase,NotImplementYet,UserNeedLogin,ACSite
from dbAC import DatabaseAC

class RefuseResponse:
    def __str__(self):
        return """{
            "errmsg":"you deny to access"
            "status":"error"
            "errno":"404"
        }"""
    
		
if __name__ == '__main__':
	import sys
	p = 'f:/runenv'
	if len(sys.argv)>1:
		p = sys.argv[1]
	conf = getConfig(p,NS={'workdir':p,'ProgramPath':p})
	DBPools(conf.databases)
	resource = static.File(conf.website['root'])
	print('doc root=',conf.website['root'])
	resource.indexNames = resource.indexNames + ['index.tmpl','index.dspy','index.wpd']
	ac = DatabaseAC('metadb','ymq123')
	site = ACSite(resource,ac)
	p1 = reactor.listenTCP(9988, site,interface='0.0.0.0')
	reactor.run()

