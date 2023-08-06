"""
Run from tabular/

"""

import tabular as tb
import tabular.utils as utils
import numpy as np
import unittest, cPickle, os, shutil

			
def delete(ToDelete):
	'''
	unified "strong" version of delete that uses os.remove for a file 
	and shutil.rmtree for a directory tree
	'''
	if os.path.isfile(ToDelete):
		os.remove(ToDelete)
	elif os.path.isdir(ToDelete):
		shutil.rmtree(ToDelete)		

def makedir(DirName,creates = ()):
	'''
	is a "strong" directory maker -- if DirName already exists, this deletes it first 
	'''
	if os.path.exists(DirName):
			delete(DirName)
	os.mkdir(DirName)

TestDataDir = 'tests/tabularTestData/'
makedir(TestDataDir)

class TestBasic(unittest.TestCase):

	def setUp(self):
		self.D = tb.tabarray(array=[(2, 'a', 2, 'cc', 3.0), (2, 'b', 5, 'dcc', 2.0), (7, 'e', 2, 'cjc', 8.0), (2, 'e', 2, 'ccj', 3.0)], names=['a','c','b','d','e'], formats='i4,|S1,i4,|S3,f8', coloring={'moo': ['a', 'b'], 'boo': ['a', 'd', 'e']})
		self.Root = 'basic'
	
	def test_getitem_list_order(self):
		self.assert_(eq(self.D[['a','b']], self.D[['b','a']]))
	
	def test_getitem_color(self):
		self.assert_(eq(self.D['moo'], self.D[['a','b']]))
		
	def test_getitem_color_threshold(self):
		self.assertEqual(self.D[['a','b']].coloring, {})
		
	def test_getitem_list_colors(self):
		self.assert_(eq(self.D[['a','boo']], self.D['boo']))
		
	def test_toload(self):				
		toload = ['boo', 'c']
		f1 = TestDataDir + self.Root + '.tsv'
		D1 = tb.tabarray(SV = f1, toload = toload)
		f2 = TestDataDir + self.Root + '.hsv/'		
		D2 = tb.tabarray(HSV = f2, toload = toload)
		self.assert_(eq(self.D[toload], D1), eq(self.D[toload], D2))
		
	def test_toload_redundant(self):				
		toload = ['a', 'boo']
		f1 = TestDataDir + self.Root + '.tsv'
		D1 = tb.tabarray(SV = f1, toload = toload)
		f2 = TestDataDir + self.Root + '.hsv/'		
		D2 = tb.tabarray(HSV = f2, toload = toload)
		self.assert_(eq(self.D[toload], D1), eq(self.D[toload], D2))
		
	def test_replace_int(self):
		D = self.D.copy()
		D.replace(2, 100, cols=['a','b','e'])
		x = self.D[['a','b','e']].extract()
		x[x == 2] = 100
		self.assert_((D[['a','b','e']].extract() == x).all())
		
	def test_replace_float(self):
		D = self.D.copy()
		D.replace(2.0, 100.0, cols=['a','b','e'])
		x = self.D[['a','b','e']].extract()
		x[x == 2.0] = 100.0
		self.assert_((D[['a','b','e']].extract() == x).all())
	
	def test_replace_str(self):
		D = self.D.copy()
		D.replace('cc', 'bb', cols=['d'])
		x = self.D.copy()['d']
		x[x == 'cc'] = 'bb'
		self.assert_(all(D['d'] == x))
		
	def test_replace_str_notstrict(self):
		D = self.D.copy()
		D.replace('cc', 'bb', cols=['d'], strict=False)
		x = self.D.copy()['d']
		x = [row.replace('cc','bb') for row in x]
		self.assert_(all(D['d'] == x))

	def test_replace_rows(self):
		D = self.D.copy()
		D.replace('cc', 'bb', cols=['d'], rows=D['a']==2)
		x = self.D.copy()['d']
		x[(x == 'cc') & (D['a']==2)] = 'bb'
		self.assert_(all(D['d'] == x))
	
	execfile('tests/tabularTesterCore.py')
	
	def test_load_HSVlist(self):
		fname = TestDataDir + self.Root + '0.hsv/'
		self.D.saveHSV(fname)
		flist = [fname + f for f in ['boo.hsv/', 'c.str.csv']]
		D = tb.tabarray(HSVlist = flist)
		self.assert_(all(self.D['boo'].hstack(D[['c']]) == D))
		
	def test_aggregate_AggFunc(self):
		AggFunc=np.mean
		[D1,s] = self.D[['a','b','e']].aggregate(On=['e'], AggFunc=AggFunc, returnsort=True)
		e = utils.uniqify(self.D['e'][s])
		a = []
		b = []
		for i in e:
			boolvec = self.D['e'][s] == i
			a += [AggFunc(self.D['a'][s][boolvec])]
			b += [AggFunc(self.D['b'][s][boolvec])]
		D2 = tb.tabarray(columns=[a,b,e], names=['a','b','e'], coloring=D1.coloring, rowdata=D1.rowdata)
		self.assert_(eq(D1,D2))
		
	def test_aggregate1(self):
		AggFuncDict = {'d': ','.join}
		[D1,s] = self.D[['a','b','d']].aggregate(On=['a'], AggFuncDict=AggFuncDict, returnsort=True)
		a = utils.uniqify(self.D['a'][s])
		AggFuncDict.update({'b': sum})
		b = []
		d = []
		for i in a:
			boolvec = self.D['a'][s] == i
			b += [AggFuncDict['b'](self.D['b'][s][boolvec])]
			d += [AggFuncDict['d'](self.D['d'][s][boolvec])]
		D2 = tb.tabarray(columns=[a,b,d], names=['a','b','d'], coloring=D1.coloring, rowdata=D1.rowdata)
		self.assert_(eq(D1, D2))
		
	def test_aggregate2(self):
		AggFuncDict = {'c': '+'.join, 'd': ','.join}
		[D1,s] = self.D[['a','c','b','d']].aggregate(On=['a','b'], AggFuncDict=AggFuncDict, returnsort=True)
		ab = utils.uniqify(zip(self.D['a'][s], self.D['b'][s]))
		c = []
		d = []
		for i in ab:		
			boolvec = np.array([tuple(self.D[['a','b']][s][ind])==i for ind in range(len(self.D))])
			c += [AggFuncDict['c'](self.D['c'][s][boolvec])]
			d += [AggFuncDict['d'](self.D['d'][s][boolvec])]
		D2 = tb.tabarray(columns=[[x[0] for x in ab],c,[x[1] for x in ab],d], names=['a','c','b','d'], coloring=D1.coloring, rowdata=D1.rowdata)
		self.assert_(eq(D1, D2))

	def test_aggregate_in(self):
		AggFuncDict = {'c': '+'.join, 'd': ','.join}
		[D, s] = self.D.aggregate(On=['a','b'], AggFuncDict=AggFuncDict, returnsort=True)
		D1 = self.D[s].aggregate_in(On=['a','b'], AggFuncDict=AggFuncDict, interspersed=False)
		D2 = self.D[s].vstack(D)
		self.assert_(all(D1==D2))

class TestBasic_rowdata(unittest.TestCase):

	def setUp(self):
		D = tb.tabarray(array=[(2, 'a', 2, 'cc', 3.0), (2, 'b', 5, 'dcc', 2.0), (7, 'e', 2, 'cjc', 8.0), (2, 'e', 2, 'ccj', 3.0)], names=['a','c','b','d','e'], formats='i4,|S1,i4,|S3,f8', coloring={'moo': ['a', 'b'], 'boo': ['a', 'd', 'e']})
		AggFuncDict = {'c': '+'.join, 'd': ','.join}
		D = D.aggregate_in(On=['a','b'], AggFuncDict=AggFuncDict, interspersed=False)
		self.D = D
		self.Root = 'basic_rowdata'
		
	execfile('tests/tabularTesterCore.py')

def TestPivot():
	# this is a lame test
	X = tb.tabarray(records=[('x',1,3,6),('y',1,5,3),('y',0,3,1),('x',0,3,5)], names=['a','b','c','d'])
	Y = X.pivot('b','a')
	Z = tb.tabarray(records=[(0, 3, 3, 5, 1), (1, 3, 5, 6, 3)], names=['b','x_c','y_c','x_d','y_d'])
	assert(all(Y==Z))

class TestBigNum(unittest.TestCase):

	def setUp(self):
		self.D = tb.tabarray(array = np.random.rand(10**3 + 50, 10**2))
		self.Root = 'big'
		
	def test_extract(self):
		self.assert_(isinstance(np.sum(self.D.extract()), float))
		
	execfile('tests/tabularTesterCore.py')

# n = ndarray, recarray or tabarray
# F = field name
# C = complex field name
# S = slice
# i = complex index

class TestBasic_TabarrayVsRecarrayVsArray(unittest.TestCase):
	
	def setUp(self):
		X = [(1, 'a', 4, 'ccc', 3.0), (2, 'b', 5, 'd', 4.0), (7, 'e', 2, 'j', 8.0), (2, 'e', 2, 'j', 3.0)]
		names=['f' + str(i) for i in range(len(X[0]))]
		formats='i4,|S1,i4,|S3,f8'.split(',')
		dtype = np.dtype({'names': names, 'formats': formats})
		self.A = np.array(X, dtype=dtype)
		self.R = np.rec.fromrecords(X)
		self.D = tb.tabarray(records=X)
		self.A1 = self.A.copy()
		self.R1 = self.R.copy()
		self.D1 = self.D.copy()

	execfile('tests/tabularTesterGetSet.py')
	
class TestBig_TabarrayVsRecarrayVsArray(unittest.TestCase):
	
	def setUp(self):
		X = np.random.rand(10**3, 10**2)
		names=['f' + str(i) for i in range(len(X[0]))]
		formats=['f8']*len(X[0])
		dtype = np.dtype({'names': names, 'formats': formats})
		self.A = np.array([tuple(row) for row in X], dtype=dtype)
		self.R = np.rec.fromrecords(X)
		self.D = tb.tabarray(array=X)		
		self.A1 = self.A.copy()
		self.R1 = self.R.copy()
		self.D1 = self.D.copy()

	execfile('tests/tabularTesterGetSet.py')

def nullvalue(test):
	return False if isinstance(test,bool) else 0 if isinstance(test,int) else 0.0 if isinstance(test,float) else ''

def eq(x,y):
# x and y are tb.tabarrays 
	b = x==y
	r = x.rowdata == y.rowdata
	if isinstance(b, bool):
		if isinstance(r, bool):
			return b and x.coloring == y.coloring and r
		else:
			return b and x.coloring == y.coloring and all(r)
	else:
		if isinstance(r, bool):
			return all(b) and x.coloring == y.coloring and r
		else:
			return all(b) and x.coloring == y.coloring and all(r)

def eq3(X):
	return (all(X.A == X.A1) and all(X.R == X.R1) and all(X.D == X.D1))
	
def neq3(X):
	return (any((X.A != X.A1)) and any((X.R != X.R1)) and any((X.D != X.D1)))