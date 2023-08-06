"""
Miscellaneous utilities for lists, sets, dictionaries, strings and 
NumPy ndarrays and recarrays.

"""

import numpy
from numpy import nan, isnan


def PermInverse(s):
	"""
	Fast invert a numpy permutation.
	
	"""
	X = numpy.array(range(len(s)))
	X[s] = range(len(s))
	return X
	

def Max(x):
	if any(isnan(x)):
		return nan
	else:
		return max(x)


def enumeratefrom(i,A):
	assert i >= 0, 'index must be larger than 0 for enumeratefrom to work'
	return list(enumerate(['',]*i + list(A)))[i:]


def uniqify(seq, idfun=None): 
	"""
	Relatively fast pure python uniqification function that preservs ordering

	**Parameters**

		seq = sequence object to uniqify
		
		idfun = optional collapse function to identify items as the same

	**Returns**

		python list with first occurence of each item in seq, in order
		
	"""
	# order preserving
	if idfun is None:
		def idfun(x): return x
	seen = {}
	result = []
	for item in seq:
		marker = idfun(item)
		# in old Python versions:
		# if seen.has_key(marker)
		# but in new ones:
		if marker in seen: continue
		seen[marker] = 1
		result.append(item)
	return result
	

def FastArrayUniqify(X):
	"""
	Very fast uniqify routine for numpy array 

	**Parameters**

		X = a numpy array

	**Returns**

		[D,s] where s is a permutation that will sort X, and D is the list of "first 
		differences" in the sorted verion of X
		
		This can be used to produce a uniqified version of X by simply taking: 
		X[s][D] or X[s[D.nonzero()[0]]]
		
		But sometimes the information of D and s is useful. 

	"""
	s = X.argsort()
	X = X[s]
	return [numpy.append([True],X[1:] != X[:-1]),s]

	
def FastRecarrayUniqify(X):
	"""
	Record array version of FastArrayUniqify.

	**Parameters**

		X = numpy record array

	**Returns**

		[D,s] where s is a permutation that will sort all the columsn of X in some order,
		and D is a list of "first differences" in the sorted version of X

		This can be used to produce a uniqified version of X by simply taking:
		X[s][D] or X[s[D.nonzero()[0]]]

		But sometimes the information of D and s is useful. 			

	"""
	N = X.dtype.names
	s = X.argsort(order=N)
	X = X[s]
	return [numpy.append([True],X[1:] != X[:-1]),s]


def ListArrayTranspose(L):
	"""
	Tranposes the simple array presentation of a list of lists (of equal length). 

	**Parameters**

		L = [row1, row2, ...., rowN]
		where the rowi are python lists of equal length. 

	**Returns**	

		LT, a list of python lists such that LT[j][i] = L[i][j]. 

	"""
	return [[row[i] for row in L] for i in range(len(L[0]))]
	
	
def Union(ListOfSets):
	"""
	Takes python list of python sets [S1,S2, ..., SN] and returns their union
	
	"""
	u = set([])
	for s in ListOfSets:
		u.update(s)
	return u


def ListUnion(ListOfLists):
	"""
	Takes python list of python lists
	
	[[l11,l12, ...], [l21,l22, ...], ... , [ln1, ln2, ...]] 
	
	and returns the aggregated list 
	
	[l11,l12, ..., l21, l22 , ...]
	
	"""
	u = []
	for s in ListOfLists:
		if s != None:
			u.extend(s)
	return u


def MakeT(r):
	"""
	If input 'r' is a comma-delimited string, return tuple split on 
	commas, else return tuple(r)
	
	"""
	return tuple(r.split(',')) if isinstance(r,str) else tuple(r)	


def fastequalspairs(Y,Z):
	"""
	**Parameters**
	
		LL1 = numpy array of paths
	
		LL2 = sorted numpy array of paths
	
	**Returns**
	
		[A,B] where A and B are numpy arrays of indices in LL1 
		such that LL2[A[i]:B[i]] = LL1[i].   
		
		A[i] = B[i] = 0 if LL1[i] not in LL2

	"""		
	T = Z.copy()
	R = (T[1:] != T[:-1]).nonzero()[0] 
	R = numpy.append(R,numpy.array([len(T)-1]))
	M = R[R.searchsorted(range(len(T)))]
	D = T.searchsorted(Y)
	T = numpy.append(T,numpy.array([0]))
	M = numpy.append(M,numpy.array([0]))
	W = (T[D] == Y) * D
	U = (T[D] == Y) * (M[D] + 1)
	return [W,U]


def fastisin(Y,Z):	
	"""
	fast routine for determining indices of elements in numpy array 
	Y that appear in numpy array Z
	
	returns boolean array of those indices
	
	"""
	if len(Z) > 0:
		T = Z.copy()
		T.sort()
		D = T.searchsorted(Y)
		T = numpy.append(T,numpy.array([0]))
		W = (T[D] == Y)
		if isinstance(W,bool):
			return numpy.zeros((len(Y),),bool)
		else:
			return (T[D] == Y) 
	else:
		return numpy.zeros((len(Y),),bool)


def FastRecarrayEquals(Y,Z):
	"""
	fast routine for determining whether numpy record array Y 
	equals record array Z
	
	"""
	if Y.dtype.names != Z.dtype.names or len(Y) != len(Z):
		return False
	else:
		NewY = numpy.array([str(l) for l in Y])
		NewZ = numpy.array([str(l) for l in Z])
		NewZ.sort(); NewY.sort()
		return all(NewY == NewZ)
		

def FastRecarrayEqualsPairs(Y,Z):
	NewY = numpy.array([str(l) for l in Y])
	NewZ = numpy.array([str(l) for l in Z])
	s = NewZ.argsort()  ; NewZ.sort()
	[A,B] = fastequalspairs(NewY,NewZ)
	return [A,B,s]


def FastRecarrayIsIn(Y,Z):
	"""
	Fast routine for determining which records in numpy record array
	Y appear in record array Z
	
	"""
	if Y.dtype.names != Z.dtype.names:
		return numpy.zeros((len(Y),),bool)
	else:
		NewY = numpy.array([str(l) for l in Y])
		NewZ = numpy.array([str(l) for l in Z])
		NewZ.sort()
		return fastisin(NewY,NewZ)
		
		
def FastRecarrayDifference(X,Y):
	"""
	fast routine for determining which records in numpy array X do
	not appear in numpy array Y
	
	"""
	if len(Y) > 0:
		Z = FastRecarrayIsIn(X,Y)
		return X[numpy.invert(Z)]
	else:
		return X


def fastarraymax(X,Y):
	"""
	fast way to achieve: 
	
	**Parameters**
	
		X,Y numpy arrays of equal length

	**Returns**

		Z where Z[i] = max(X[i],Y[i])
	
	"""
	Z = numpy.zeros((len(X),),int)
	A = X <= Y
	B = Y < X
	Z[A] = Y[A]
	Z[B] = X[B]
	return Z


def fastarraymin(X,Y):
	"""
	fast way to achieve: 
	
	**Parameters**
	
		X,Y numpy arrays of equal length
	
	**Returns**
	
		Z where Z[i] = min(X[i],Y[i])
	
	"""
	Z = numpy.zeros((len(X),),int)
	A = X <= Y
	B = Y < X
	Z[A] = X[A]
	Z[B] = Y[B]
	return Z
	

def SimpleStack(seq,UNIQIFY=False):
	"""
	Vertically stack sequences numpy record arrays. 
	Avoids some of the problems of numpy.v_stack
	
	"""
	newseq = [ss for ss in seq if len(ss) > 0]
	if len(newseq) > 1:
		seq = newseq
		names = seq[0].dtype.names
		formats = [max([a.dtype[att] for a in seq]).str for att in names]
		if UNIQIFY:
			X =  numpy.rec.fromarrays([ListUnion([a[att].tolist() for a in seq]) for att in names], names = names, formats = formats)
			[D,s] = FastRecarrayUniqify(X)
			return X[s][D]
		else:
			return numpy.rec.fromarrays([ListUnion([a[att].tolist() for a in seq]) for att in names], names = names, formats = formats)
	elif len(newseq) == 1:
		return newseq[0]
	else:
		return seq[0][0:0]

		
def SimpleStack1(seq,UNIQIFY=False):
	"""
	Vertically stack sequences numpy record arrays. 
	Avoids some of the problems of numpy.v_stack but is slower
	
	if UNIQIFY set to true, only retains unique records
	
	"""
	newseq = [ss for ss in seq if len(ss) > 0]
	if len(newseq) > 1:
		seq = newseq
		names = seq[0].dtype.names
		formats = [max([a.dtype[att] for a in seq]).str for att in names]
		if UNIQIFY:
			numpy.rec.fromrecords(uniqify(ListUnion([ar.tolist() for ar in newseq])), names = names, formats = formats)
		else:
			return numpy.rec.fromrecords(ListUnion([ar.tolist() for ar in newseq]), names = names, formats = formats)
	elif len(newseq) == 1:
		return newseq[0]
	else:
		return seq[0][0:0]		
	

def SimpleColumnStack(seq):
	"""
	Stack columns in sequences of numpy record arrays. 
	Avoids some of the problems of numpy.c_stack but is slower
	
	"""
	Columns = ListUnion([[a[l] for l in a.dtype.names] for a in seq])
	names = ListUnion([list(a.dtype.names) for a in seq])
	return numpy.rec.fromarrays(Columns,names=names)	
	

def RemoveColumns(recarray,ToRemove):
	"""
	Given numpy recarray and list of column names ToRemove,
	return recarray with columns whose names are not in ToRemove
	
	"""
	newdtype = numpy.dtype([x for x in recarray.dtype.descr if x[0] not in ToRemove])
	return numpy.rec.fromarrays([recarray[name] for name in recarray.dtype.names if name not in ToRemove],dtype = newdtype)


def DictInvert(D):
	"""
	**Parameters**

		dictionary D

	**Returns**

		dictionary whose keys are unique elements of values of D, and 
		whose values on key 'K' are lists of keys 'k' in D such that D[k] = K
	
	"""
	return dict([(v,set([j for j in D.keys() if D[j] == v])) for v in set(D.values())])