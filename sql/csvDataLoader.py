import sys
import os
import ujson as json
import codecs
from appPublic.csv_Data import CSVData
from sqlor import opendb,sqlorFactory
import sqlor
import mssqlor
import oracleor
from appPublic.timeUtils import str2Date
from dbinserterWriter import DBInserter
def getTablename(fn):
	return fn[:-len('_data.csv')]

if __name__ == '__main__':
	if len(sys.argv)<3:
		print( "Usage:\n%s dbdef csvfile" % sys.argv[0])
		sys.exit(1)
	
	f = codecs.open(sys.argv[1],'r','utf8')
	dbdef = json.load(f)
	f.close()
	tabname = getTablename(os.path.basename(sys.argv[2]))

	conn = opendb(dbdef)
	sqlor = sqlorFactory(dbdef['driver'],conn)
	sqlor.setConvertFunction('date',str2Date)
	fields = sqlor.fields(tabname)
	if len(fields) == 0:
		print( "table not existed", tabname)
		sys.exit(1)
	# print( fields)
	nf = {}
	[ nf.update({f['name']:f}) for f in fields ]

	csv = CSVData(sys.argv[2])
	writer = DBInserter(sqlor=sqlor,table=tabname)

	first = 1
	for rec in csv:
		if first == 1:
			desc = [[k] for k in rec.keys() ]
			writer.setDescription(desc)
			first = 0
		d = [ sqlor.convert(nf[k]['type'],v) for  k,v in rec.items() ]
		writer.write(d)

		
