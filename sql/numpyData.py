import numpy as np

def NumpyData(recs):
	"""
	using array fo dict to construct a numpy data
	"""
	rcnt = len(recs)
	ccnt = len(recs[0].keys())
	npd = np.arange(rcnt*ccnt).reshape(rcnt,ccnt)
	index = 0
	for r in recs:
		row = [ r[k] for k in r ]
		dts = [type(i) for i in row ]
		self.npd[index,:] = np.fromiter(row, dtype=dts, count=1)
		index += 1
	return npd

