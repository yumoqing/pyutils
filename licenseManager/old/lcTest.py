from licenseManager import LicenseChecker

class MyLicenseChecker(LicenseChecker):
	pubkey = """(dp0
S'e'
p1
L68024227949032272933540310204488396592048913431105705928961784172824900175709796980228232376580903713662387282989955337471096277415293574464080503457317342712572559960596904868857343074726882988715137964840493355817574303039872258824689458223838146282723435029209996398570692425303544091444740611876464417737L
sS'n'
p2
L512968404649223889123143524942969767447208281549944263942703258629923672803408276340787475780629599081133745662184568117033309333376475554874046090708647627115475520370134887976219542835550872570500732267410326458454219487619034106845372946931634228473137815448229294166208340458206971101904824257463491518947741060881215229868348947630928279598624535339462251206064245201818204636136111907982753431209023613889017675273991916011624221344990627243591517195790085504029052532960111968100987585496147389033911955836160945995372879069952886767338038654480326990776570733994237914267082627853848498959843947381029547266608465535376672085591384364222115078551901694813599857919852393646891355412867892596293840899805457388549063302209205407204285303711316331557960578397298436325200786825965441730885351846343885957325674496717298056547675658905508803442959352174173305645180805152878915036023748937749114149070295395910244531141878247583546582503522217778035817251619747125257356144450988245972405376170793924871752203050067937982007445503959547315080187109952174077391512336855984241812898372629701429595207877435908257355125656467453692751952488807049308738835717400545725988772623879626222446020189088191500071757998048157001228237327L
s."""

lc = MyLicenseChecker('','','')
a = lc.isLicensed()	
print a