"""
Functions to summarize :class:`tabular.tabarray.tabarray` 
objects:  horizontal and vertical stacking.

See :mod:`numpy.lib.shape_base`.
"""

__all__ = ['datahstack', 'datavstack']

import numpy
import tabular as tb
from tabular import utils as utils

def datahstack(ListOfArrays):
	'''
	For "horizontal stacking" tabarrays, e.g. adding columns. 
	Requires all tabarrays to have same number of records. 
	If column appears to two tabarrays in ListOfDats, first is 
	taken. 
	'''
	dtype = []
	data = []
	coloring = {}
	for a in ListOfArrays:
		if 'coloring' in dir(a):
			coloring.update(a.coloring)
		dtype += a.dtype.descr
		for att in a.dtype.names:
			data += [a[att]]
	dtype = numpy.dtype(dtype)
	rowdata = SafeColumnStack([l.rowdata for l in ListOfArrays if l.rowdata != None])
	return tb.tabarray(columns=data, dtype=dtype, coloring=coloring, rowdata=rowdata)

def SafeColumnStack(seq):
	'''
	Horizontally stack sequences numpy record arrays. 
	Avoids some of the problems of numpy.hstack
	'''
	seq = [l for l in seq if l != None]
	if len(seq) > 0:
		done = []
		Columns = []
		names = []
		for l in seq:
			Columns += [l[n] for n in l.dtype.names if n not in done]
			names += [n for n in l.dtype.names if n not in done]
			done += [n for n in l.dtype.names if n not in done]
		
		return numpy.rec.fromarrays(Columns, names=names)
	else:	
		return None

def datavstack(ListOfArrays):
	'''
	"Vertical stacking" of tabarrays, e.g. adding rows. 
	'''
	CommonAttributes = ListOfArrays[0].dtype.names
	for l in ListOfArrays:
		CommonAttributes = [c for c in CommonAttributes if c in l.dtype.names]
	CommonAttributes = list(CommonAttributes)
	CommonAttributes = [CommonAttributes[j] for j in [CommonAttributes.index(e) for e in ListOfArrays[0].dtype.names if e in CommonAttributes]]
	
	if len(CommonAttributes) == 0:
		try:
			return numpy.row_stack(ListOfArrays)
		except:
			print "The data arrays you tried to stack couldn't be stacked."
	else:		
		A = utils.SimpleStack1([l[CommonAttributes] for l in ListOfArrays])
		if all(['coloring' in dir(l) for l in ListOfArrays]):
			restrictedcoloring = dict([(a,[c for c in ListOfArrays[0].coloring[a] if c in CommonAttributes]) for a in ListOfArrays[0].coloring.keys()])
			for l in ListOfArrays[1:]:
				restrictedcoloring.update(dict([(a,[c for c in l.coloring[a] if c in CommonAttributes]) for a in l.coloring.keys()]))
		else:
			restrictedcoloring = {}
		if not all ([l.rowdata == None for l in ListOfArrays]):
			rowdata = SafeSimpleStack([l.rowdata if l.rowdata != None else numpy.array(['']*len(l)) for l in ListOfArrays ])		
		else:
			rowdata = None
		return tb.tabarray(array=A, dtype=A.dtype, coloring=restrictedcoloring, rowdata=rowdata)		

def SafeSimpleStack(seq):
	'''
	Vertically stack sequences numpy record arrays. 
	Avoids some of the problems of numpy.vstack.
	'''
	names =  utils.uniqify(utils.ListUnion([list(s.dtype.names) for s in seq if s.dtype.names != None]))
	formats =  [max([s.dtype[att] for s in seq if s.dtype.names != None and att in s.dtype.names]).str for att in names]
	D = numpy.rec.fromarrays([utils.ListUnion([s[att].tolist() if (s.dtype.names != None and att in s.dtype.names) else [nullvalueformat(format)] * len(s) for s in seq]) for (att,format) in zip(names,formats)], names = names)
	D = D.dumps()
	return numpy.loads(D)

def nullvalueformat(format):
	"""
	Returns a null value for each of various kinds of format values. 
	"""
	return 0 if format.startswith(('<i','|b')) else 0.0 if format.startswith('<f') else ''