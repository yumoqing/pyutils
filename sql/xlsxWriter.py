from sql.writer import BaseWriter
from xlutils.copy import copy
from xlrd import open_workbook
import xlwt

def getSheetByName(self,sheetname):
	for ws in self._Workbook__worksheets:
		if ws.get_name() == sheetname:
			return ws
	return None

xlwt.Workbook.getSheetByName = getSheetByName

class XLSXWriter(BaseWriter):
	@classmethod
	def isMe(self,ft):
		return ft == 'xls'
	
	def __init__(self,outfile=None,patternfile=None,sheet='Sheet1',start='A1',head=False,headlist=[],maxWrite=0):
		BaseWriter.__init__(self,maxWrite=maxWrite)
		self.outfile = outfile
		self.patternfile = patternfile
		self.sheet = sheet
		self.start = start
		self.head = head
		self.headlist = headlist
		self.createWorkbook()
		self.getXY(self.start)
		self.current_row = 0
	
	def setDescription(self,desc):
		BaseWriter.setDescription(self,desc)
		self.writeHead()
		
		
	def createWorkbook(self):
		self.ws = None
		if self.patternfile is not None:
			wb = open_workbook(self.patternfile)
			self.wb = copy(wb)
			#print dir(self.wb)
			self.ws = self.wb.getSheetByName(self.sheet)
		else:
			self.wb = xlwt.Workbook()
		if self.ws == None:
			self.ws = self.wb.add_sheet(self.sheet)
	
	def writeHead(self):
		if self.head:
			names = self.headlist
			#print names,self.fields
			if len(self.headlist) < 1:
				names = self.fields
			for j in range(len(names)):
				self.ws.write(self.start_row,self.start_col + j,names[j])
			self.start_row += 1

	def getXY(self,start):
		rs = []
		cs = []
		for c in start.upper():
			if c<='9' and c >= '0':
				rs.append(c)
			else:
				cs.append(c)
		self.start_row = int(''.join(rs)) - 1
		self.start_col = 0
		for c in cs:
			self.start_col += self.start_col * 26 + ord(c) - ord('A')
		
	def write(self,r):
		cnt = len(r)
		for j in range(cnt):
			self.ws.write(self.start_row + self.current_row,self.start_col + j,r[j])
		self.current_row += 1
 
	def finish(self):
 		self.wb.save(self.outfile)
	
	def __del__(self):
		self.finish()
		
 