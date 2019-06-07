import codecs
from .dataloader import DataLoader
from twisted.internet import defer

class FileDataLoader(DataLoader):
	def loadData(self,filename):
		with codecs.open(filename,'r','utf8') as f:
			return f.read()

	def asyncLoad(self,filename):
		d = defer.maybeDeferred(self.loadData,filename)
		d.addCallback(self.dataLoad)
		d.addErrback(self.loadError)


