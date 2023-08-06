"""
Run from tabular/

"""

import tabular as tb
import tabular.utils as utils
import numpy as np
import unittest, cPickle, os, shutil
import tabular.spreadsheet as spreadsheet

			
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

assert os.path.isdir('tests'), "\n\nYou must run these tests from the parent directory of the directory 'tests', which is assumed to contain this ('tabularTester.py') and other test modules."

TestDataDir = 'tests/tabularTestData/'
makedir(TestDataDir)

class TestBasic(unittest.TestCase):

	def setUp(self):
		self.D = tb.tabarray(array=[(2, 'a', 2, 'cc', 3.0), (2, 'b', 5, 'dcc', 2.0), (7, 'e', 2, 'cjc', 8.0), (2, 'e', 2, 'ccj', 3.0)], names=['a','c','b','d','e'], formats='i4,|S1,i4,|S3,f8', coloring={'moo': ['a', 'b'], 'boo': ['a', 'd', 'e']})
		self.Root = 'basic'

	def tearDown(self):
		self.D = None
		self.Root = None			
	
	def test_getitem_list_order(self):
		self.assert_(eq(self.D[['a','b']], self.D[['b','a']]))
	
	def test_getitem_color(self):
		self.assert_(eq(self.D['moo'], self.D[['a','b']]))
		
	def test_getitem_color_threshold(self):
		self.assertEqual(self.D[['a','b']].coloring, {'boo':['a']})
		
	def test_getitem_list_colors(self):
		self.assert_(eq(self.D[['a','boo']], self.D['boo']))
		
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
	
	def test_toload_tsv(self):				
		toload = ['boo', 'c']
		fname = TestDataDir + self.Root + '5.tsv'
		self.D.saveSV(fname)
		D = tb.tabarray(SVfile = fname, toload = toload)
		self.assert_io(eq(self.D[toload], D), fname)

	def test_toload_hsv(self):				
		toload = ['boo', 'c']
		fname = TestDataDir + self.Root + '5.hsv/'		
		self.D.saveHSV(fname)
		D = tb.tabarray(HSVfile = fname, toload = toload)
		self.assert_io(eq(self.D[toload], D), fname)
		
	def test_toload_redundant_tsv(self):				
		toload = ['a', 'boo']
		fname = TestDataDir + self.Root + '6.tsv'
		self.D.saveSV(fname)
		D = tb.tabarray(SVfile = fname, toload = toload)
		self.assert_io(eq(self.D[toload], D), fname)	
		
	def test_toload_redundant_hsv(self):				
		toload = ['a', 'boo']
		fname = TestDataDir + self.Root + '6.hsv/'		
		self.D.saveHSV(fname)
		D = tb.tabarray(HSVfile = fname, toload = toload)
		self.assert_io(eq(self.D[toload], D), fname)	
	
	def test_load_HSVlist(self):
		fname = TestDataDir + self.Root + '0.hsv/'
		self.D.saveHSV(fname)
		flist = [fname + f for f in ['boo.hsv/', 'c.str.csv']]
		D = tb.tabarray(HSVlist = flist)
		self.assert_io(all(self.D['boo'].colstack(D[['c']]) == D), fname)
		
	def test_aggregate_AggFunc(self):
		AggFunc=np.mean
		[D1,s] = self.D[['a','b','e']].aggregate(On=['e'], AggFunc=AggFunc,returnsort=True)
		e = utils.uniqify(self.D['e'][s])
		a = []
		b = []
		for i in e:
			boolvec = self.D['e'][s] == i
			a += [AggFunc(self.D['a'][s][boolvec])]
			b += [AggFunc(self.D['b'][s][boolvec])]
		D2 = tb.tabarray(columns=[a,b,e], names=['a','b','e'], coloring=D1.coloring)
		self.assert_(eq(D1,D2))
		
	def test_aggregate1(self):
		AggFuncDict = {'d': ','.join}
		[D1,s] = self.D[['a','b','d']].aggregate(On=['a'], AggFuncDict=AggFuncDict,returnsort=True)
		a = utils.uniqify(self.D['a'][s])
		AggFuncDict.update({'b': sum})
		b = []
		d = []
		for i in a:
			boolvec = self.D['a'][s] == i
			b += [AggFuncDict['b'](self.D['b'][s][boolvec])]
			d += [AggFuncDict['d'](self.D['d'][s][boolvec])]
		D2 = tb.tabarray(columns=[a,b,d], names=['a','b','d'], coloring=D1.coloring)
		self.assert_(eq(D1, D2))
		
	def test_aggregate2(self):
		AggFuncDict = {'c': '+'.join, 'd': ','.join}
		[D1,s] = self.D[['a','c','b','d']].aggregate(On=['a','b'], AggFuncDict=AggFuncDict,returnsort = True)
		ab = utils.uniqify(zip(self.D['a'][s], self.D['b'][s]))
		c = []
		d = []
		for i in ab:		
			boolvec = np.array([tuple(self.D[['a','b']][s][ind])==i for ind in range(len(self.D))])
			c += [AggFuncDict['c'](self.D['c'][s][boolvec])]
			d += [AggFuncDict['d'](self.D['d'][s][boolvec])]
		D2 = tb.tabarray(columns=[[x[0] for x in ab],c,[x[1] for x in ab],d], names=['a','c','b','d'], coloring=D1.coloring)
		self.assert_(eq(D1, D2))

	def test_aggregate_in(self):
		AggFuncDict = {'c': '+'.join, 'd': ','.join}
		D = self.D.aggregate(On=['a','b'], AggFuncDict=AggFuncDict)
		D1 = self.D.aggregate_in(On=['a','b'], AggFuncDict=AggFuncDict, interspersed=False).deletecols(['__aggregates__','__color__'])
		D2 = self.D.rowstack(D)
		self.assert_(all(D1==D2))
		
class TestAddCols(unittest.TestCase):
	def setUp(self):
		V1 = ['North','South','East','West']
		V2 = ['Service','Manufacturing','Education','Healthcare']
		Recs = [(a,b,np.random.rand()*100,np.random.randint(100000),np.random.rand(),'Yes' if np.random.rand() < .5 else 'No') for a in V1 for b in V2]
		self.Y = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population','Importance','Modernized'])
		self.n1 = 'Importance'
		self.n2 = 'Modernized'
		self.X = self.Y[[o for o in self.Y.dtype.names if o != self.n1 and o != self.n2]]
				
	def test_1(self):
		Y = self.X.addcols(self.Y[self.n1],names=self.n1)
		self.assert_(eq(Y,self.Y[[o for o in self.Y.dtype.names if o !=  self.n2]]))
	
	def test_2(self):
		Y = self.X.addcols(list(self.Y[self.n1]),names=[self.n1])
		self.assert_(eq(Y,self.Y[[o for o in self.Y.dtype.names if o !=  self.n2]]))
		
	def test_3(self):
		z = np.rec.fromarrays([self.Y[self.n1]],names = [self.n1])
		Y = self.X.addcols(z)
		self.assert_(eq(Y,self.Y[[o for o in self.Y.dtype.names if o !=  self.n2]]))

	def test_4(self):
		Y =  self.X.addcols([self.Y[self.n1],self.Y[self.n2]],names =[self.n1,self.n2])
		self.assert_(eq(Y,self.Y))
	
	def test_5(self):
		Y = self.X.addcols([self.Y[self.n1],list(self.Y[self.n2])],names = self.n1 + ',' + self.n2)
		self.assert_(eq(Y,self.Y))
		
	def test_6(self):
		Y = self.X.addcols([list(self.Y[self.n1]),list(self.Y[self.n2])],names = self.n1 + ', ' + self.n2)
		self.assert_(eq(Y,self.Y))
		
	def test_7(self):
		Y = self.X.addcols(self.Y[[self.n1,self.n2]])
		self.assert_(eq(Y,self.Y))


class TestJoin(unittest.TestCase):
	def setUp(self):
		V1 = ['North','South','East','West']
		V2 = ['Service','Manufacturing','Education','Healthcare']
		Recs = [(a,b,np.random.rand()*100,np.random.randint(100000),np.random.rand(),'Yes' if np.random.rand() < .5 else 'No') for a in V1 for b in V2]
		self.X = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population','Importance','Modernized'])
		self.keycols = ['Region','Sector']
		self.others = [['Amount','Population'],['Importance','Modernized']]
				

	def test_strictjoin(self):		
		ToMerge = [self.X[self.keycols + n] for n in self.others]
		Y = spreadsheet.strictjoin(ToMerge,self.keycols)
		Z = self.X.copy()
		Z.sort(order  = self.keycols)
		Y.sort(order = self.keycols) 
		self.assert_((Z == Y).all())
		
	def test_strictjoin2(self):
		ToMerge = [self.X[self.keycols + [x]] for x in self.X.dtype.names if x not in self.keycols]
		Y = spreadsheet.strictjoin(ToMerge,self.keycols)
		Z = self.X.copy()
		Z.sort(order = self.keycols)
		Y.sort(order = self.keycols)
		self.assert_((Z == Y).all())
		
	def test_strictjoin3(self):
		X = self.X ; keycols = self.keycols ; others = self.others
		X1 = X[:(3*len(X))/4][keycols + others[0]] ; X2 = X[len(X)/4:][keycols + others[1]]
		Y = spreadsheet.strictjoin([X1,X2],self.keycols)
		Y.sort(order = keycols)
		
		nvf = spreadsheet.DEFAULT_NULLVALUEFORMAT
		nvf1 = nvf(X[others[1][0]].dtype.descr[0][1])
		nvf2 = nvf(X[others[1][1]].dtype.descr[0][1])
		nvf3 = nvf(X[others[0][0]].dtype.descr[0][1])
		nvf4 = nvf(X[others[0][1]].dtype.descr[0][1])
				
		Recs = [(a,b,c,d,nvf1,nvf2) for (a,b,c,d,e,f) in X[:len(X)/4]] + [(a,b,c,d,e,f) for (a,b,c,d,e,f) in X[len(X)/4:(3*len(X))/4]] + [(a,b,nvf3,nvf4,e,f) for (a,b,c,d,e,f) in X[3*len(X)/4:]] 
		Z = tb.tabarray(records = Recs,names = X.dtype.names)
		Z.sort(order = self.keycols)
		
		self.assert_((Y == Z).all())
		
	def test_strictjoin4(self):		
		ToMerge = dict([('d' + str(i) , self.X[self.keycols + n]) for (i,n) in enumerate(self.others)])
		Y = spreadsheet.strictjoin(ToMerge,self.keycols)
		Y.sort(order = self.keycols)
		Z = self.X.copy()
		Z.sort(order  = self.keycols)
		self.assert_((Z == Y).all())
		

	def test_join(self):
		ToMerge = [self.X[self.keycols + n] for n in self.others]
		Y = spreadsheet.join(ToMerge)
		Y.sort(order = self.keycols)
		Z = self.X.copy()
		Z.sort(order  = self.keycols)
		self.assert_((Z == Y).all())
		
	def test_join2(self):
		Y1 = self.X[['Region','Sector','Amount']].copy()
		Y2 = self.X[['Region','Sector','Modernized']].copy()
		Y1.renamecol('Amount','Modernized')
		Z = spreadsheet.join([Y1,Y2],['Region','Sector'])
		
		Z1 = self.X[['Region','Sector','Modernized','Amount']]
		Z1.sort()
		Z1.renamecol('Amount','Modernized_0')
		Z1.renamecol('Modernized','Modernized_1')
		
		self.assert_((Z1 == Z).all())
		
	def test_join3(self):
		Recs1 = [('North', 'Service', 80.818237828506838),('North', 'Manufacturing', 67.065114829789664), ('North', 'Education', 31.043641435185123), ('North', 'Healthcare', 14.196823211749276), ('South', 'Service',2.3583798234914521)]
		Recs2 = [('North', 'Service', 33.069022471086903), ('North', 'Manufacturing', 63.155520758932305), ('North', 'Education', 70.80529023970098), ('North', 'Healthcare', 40.301231798570171), ('South', 'Service', 13.095729670745381)]
		X1 = tb.tabarray(records = Recs1,names=['Region','Sector','Amount'])
		X2 = tb.tabarray(records = Recs2,names=['Region','Sector','Amount'])
		Z = spreadsheet.join([X1,X2],keycols=['Region','Sector'],Names = ['US','China'])
		
		Recs = [(a,b,c,d) for ((a,b,c),(x1,x2,d)) in zip(Recs1,Recs2)]
		X = tb.tabarray(records = Recs,names = ['Region','Sector','Amount_US','Amount_China'])
		
		X.sort(order=['Region','Sector'])
		Z.sort(order=['Region','Sector'])
		assert (X == Z).all()
	
	def test_joinmethod(self):
		X = self.X.copy(); keycols = self.keycols ; others = self.others
		Y = X[keycols + others[0]]
		Z = Y.join([X[keycols + n] for n in others[1:]])
		X.sort(order = keycols)
		Z.sort(order = keycols)
		self.assert_(eq(X,Z))

	def test_joinmethod2(self):
		X = self.X.copy(); keycols = self.keycols ; others = self.others
		X.coloring['Numerical'] = ['Amount','Population','Importance']		
		
		Y1 = X[['Region','Sector','Amount']].copy()
		Y2 = X[['Region','Sector','Modernized']].copy()
		Y1.renamecol('Amount','Modernized')
		Z = Y1.join(Y2,keycols=['Region','Sector'])
		
		Z1 = X[['Region','Sector','Modernized','Amount']]
		Z1.sort()
		Z1.renamecol('Amount','Modernized_0')
		Z1.renamecol('Modernized','Modernized_1')
		
		self.assert_(eq(Z,Z1))


class TestLoadSaveSV(unittest.TestCase):	# test non-default use cases

	def assert_io(self, expr, fname):
		if expr:
			delete(fname)
			self.assert_(expr)
		else:
			self.assert_(expr)

	def setUp(self):
		V1 = ['North','South','East','West']
		V2 = ['Service','Manufacturing','Education','Healthcare']
		Recs = [(a,b,np.random.rand()*100,np.random.randint(100)) for a in V1 for b in V2]
		self.X = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population'], coloring={'zoo': ['Region','Sector'], 'york': ['Population','Sector','Region']})

	def test_load_save_CSV_infer(self):
		fname = 'test.csv'
		self.X.saveSV(fname)
		X2 = tb.tabarray(SVfile = fname)
		self.assert_io(eq(self.X, X2), fname)
	
	def test_load_save_TSV_infer(self):
		fname = 'test.tsv'
		self.X.saveSV(fname)
		X2 = tb.tabarray(SVfile = fname)
		self.assert_io(eq(self.X, X2), fname)
		
	def test_load_save_CSV_infer1(self):
		fname = 'test1.csv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['names'])
		X2 = tb.tabarray(SVfile = fname)
		Z = self.X.copy()
		Z.coloring = {}
		self.assert_io(eq(Z, X2), fname)
	
	def test_load_save_TSV_infer1(self):
		fname = 'test1.tsv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['names'])
		X2 = tb.tabarray(SVfile = fname)
		Z = self.X.copy()
		Z.coloring = {}
		self.assert_io(eq(Z, X2), fname)
		
	def test_load_save_CSV_infer2(self):
		fname = 'test2.csv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['coloring', 'names'])
		X2 = tb.tabarray(SVfile = fname, metadatadict={'coloring': 0, 'names': 1})
		self.assert_io(eq(self.X, X2), fname)
	
	def test_load_save_TSV_infer2(self):
		fname = 'test2.tsv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['coloring', 'names'])
		X2 = tb.tabarray(SVfile = fname, metadatadict={'coloring': 0, 'names': 1})
		self.assert_io(eq(self.X, X2), fname)		
		
	def test_load_save_CSV_skiprows(self):
		fname = 'test3.csv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['coloring', 'names'])
		X2 = tb.tabarray(SVfile = fname, skiprows=1)
		Z = self.X.copy()
		Z.coloring = {}
		self.assert_io(eq(Z, X2), fname)
	
	def test_load_save_TSV_skiprows(self):
		fname = 'test3.tsv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['coloring', 'names'])
		X2 = tb.tabarray(SVfile = fname, skiprows=1)
		Z = self.X.copy()
		Z.coloring = {}
		self.assert_io(eq(Z, X2), fname)		

	def test_load_save_CSV_nocomments(self):
		fname = 'test4.csv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['coloring', 'names'], comments='')
		X2 = tb.tabarray(SVfile = fname, comments='', headerlines=2)
		Z = self.X.copy()
		Z.coloring = {}
		self.assert_io(eq(Z, X2), fname)
	
	def test_load_save_TSV_nocomments(self):
		fname = 'test4.tsv'
		self.X.saveSV(fname, printmetadatadict=False, metadatakeys=['coloring', 'names'], comments='')
		X2 = tb.tabarray(SVfile = fname, comments='', headerlines=2)
		Z = self.X.copy()
		Z.coloring = {}
		self.assert_io(eq(Z, X2), fname)		
		
		
def TestReplace():
	V1 = ['North','South','East','West']
	V2 = ['Service','Manufacturing','Education','Healthcare']
	Recs = [(a,b,np.random.rand()*100,np.random.randint(100000)) for a in V1 for b in V2]
	Recs2 = [(a,b.replace('Education','Taxes'),c,d) for (a,b,c,d) in Recs]
	X = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population'])
	X2 = tb.tabarray(records = Recs2,names=['Region','Sector','Amount','Population'])
	
	X.replace('Education','Taxes')
	assert((X==X2).all())
	
def TestReplace2():
	V1 = ['North','South','East','West']
	V2 = ['Service','Manufacturing','Education','Healthcare']
	Recs = [(a,b,np.random.rand()*100,np.random.randint(100000)) for a in V1 for b in V2]
	X = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population'])
	X2 = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population'])
	
	X.replace('S','M')
	assert((X==X2).all())
	
def TestReplace3():
	V1 = ['North','South','East','West']
	V2 = ['Service','Manufacturing','Education','Healthcare']
	Recs = [(a,b,np.random.rand()*100,np.random.randint(100000)) for a in V1 for b in V2]
	Recs2 = [(a.replace('e','B'),b.replace('e','B'),c,d) for (a,b,c,d) in Recs]
	X = tb.tabarray(records = Recs,names=['Region','Sector','Amount','Population'])
	X2 = tb.tabarray(records = Recs2,names=['Region','Sector','Amount','Population'])
	
	X.replace('e','B',strict = False)
	assert((X==X2).all())

def TestPivot1():
	X = tb.tabarray(records=[('x',1,3,6),('y',1,5,3),('y',0,3,1),('x',0,3,5)], names=['a','b','c','d'])
	Y = X.pivot('b','a')
	Z = tb.tabarray(records=[(0, 3, 3, 5, 1), (1, 3, 5, 6, 3)], names=['b','x_c','y_c','x_d','y_d'])
	assert (Y==Z).all()

def TestPivot2():
	X = tb.tabarray(records=[('x',1,3,6),('y',0,3,1),('x',0,3,5)], names=['a','b','c','d'])
	Y = X.pivot('b','a')
	Z = tb.tabarray(records=[(0, 3, 3, 5, 1), (1, 3, 0, 6, 0)], names=['b','x_c','y_c','x_d','y_d'])
	assert (Y==Z).all()	

def TestPivot3():
	V1 = ['NorthAmerica','SouthAmerica','Europe','Asia','Australia','Africa','Antarctica']
	V1.sort()
	V2 = ['House','Car','Boat','Savings','Food','Entertainment','Taxes']
	V2.sort()
	Recs = [(a,b,100*np.random.rand()) for a in V1 for b in V2]
	X = tb.tabarray(records = Recs,names = ['Region','Source','Amount'])
	Y = X.pivot('Region','Source')
	Z = utils.uniqify(X['Source']) ; Z.sort()
	Cols = [[y['Amount'] for y in X if y['Source'] == b] for b in Z]
	W = tb.tabarray(columns = [V1] + Cols, names = ['Region'] + [b + '_Amount' for b in Z])
	assert (W == Y).all()

def TestPivot4():
	V1 = ['NorthAmerica','SouthAmerica','Europe','Asia','Australia','Africa','Antarctica']
	V1.sort()
	V2 = ['House','Car','Boat','Savings','Food','Entertainment','Taxes']
	V2.sort()
	Recs = [(a,b,100*np.random.rand()) for a in V1 for b in V2]
	X = tb.tabarray(records = Recs[:-1],names = ['Region','Source','Amount'])
	Y = X.pivot('Region','Source',NullVals = dict([(o,-999) for o in X.dtype.names]))
	X2 = tb.tabarray(records = Recs,names = ['Region','Source','Amount'])
	Y2 = X.pivot('Region','Source')
	Y2[V2[-1] + '_Amount'][-1] = -999
	
	assert (Y == Y2).all()
	
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
	
from tabular.utils import uniqify,ListUnion,PermInverse
def TestUniqify():
	Input  = [2,3,4,4,4,5,5,1,1,2,3,6,6,5]
	Output = [2,3,4,5,1,6]
	assert (Output == uniqify(Input))

def TestUniqify2():
	Input  = [2,3,4,4,4,5,5,1,1,2,3,6,6,5]
	Output = [2,3,4,5,1,6]
	assert (Output == uniqify(Input))

def TestListUnion():
	Input = [[2,3,4],[4,5,6],[6,4,2]]
	Output = [2,3,4,4,5,6,6,4,2]
	assert (Output == ListUnion(Input))
	
def TestPermInverse():
	X = np.random.randint(0,10000,size = (5000,))
	s = X.argsort()
	assert (s[PermInverse(s)] == np.arange(len(X))).all()

from tabular.fast import *


def TestArrayUniqify():
	A = np.array([2,3,4,4,4,4,4,2,2,2,2,2,3,3,3,3,8,9,9,8,8,8,2,2,2,2,3,3,1,1,1,-1])
	[D,s] = arrayuniqify(A)
	C = A[s]
	B = np.array([i for i in range(len(C)) if C[i] not in C[:i]])

	ind = arrayuniqify(A,retainorder = True)
	E = [i for i in range(len(A)) if A[i] not in A[:i]]
	
	return (D.nonzero()[0] == B).all()  and (ind == E)
	
def TestRecarrayUniqify():
	A = np.rec.fromrecords([(3,4,'b'),(2,3,'a'),(2,3,'a'),(3,4,'b')],names = ['A','B','C'])
	[D,s] = recarrayuniqify(A)
	C = A[s]
	B = np.array([i for i in range(len(C)) if C[i] not in C[:i]])

	ind = arrayuniqify(A,retainorder = True)
	E = [i for i in range(len(A)) if A[i] not in A[:i]]
	
	return (D.nonzero()[0] == B).all()  and (ind == E)

def TestEqualsPairs():
	N = 100
	Y = np.random.randint(0,10,size=(N,))
	Y.sort()
	X = np.random.randint(0,10,size=(N,))
	
	A = np.array([min((Y == k).nonzero()[0]) for k in X])
	B = np.array([1 + max((Y == k).nonzero()[0]) for k in X])
	[C,D] = equalspairs(X,Y)
	
	assert (A == C).all() and (B == D).all()

def TestRecarrayEqualsPairs():
	N = 100
	C1 = np.random.randint(0,3,size=(N,))
	ind = np.random.randint(0,3,size=(N,))
	v = np.array(['a','b','c'])
	C2 = v[ind]
	Y = np.rec.fromarrays([C1,C2],names = ['A','B'])
	
	C1 = np.random.randint(0,3,size=(N,))
	ind = np.random.randint(0,3,size=(N,))
	v = np.array(['a','b','c'])
	C2 = v[ind]
	X = np.rec.fromarrays([C1,C2],names = ['A','B'])	
	
	[C,D,s] = recarrayequalspairs(X,Y)
	Y = Y[s]	
	A = np.array([min((Y == k).nonzero()[0]) for k in X])
	B = np.array([1 + max((Y == k).nonzero()[0]) for k in X])
	
	assert (A == C).all() and (B == D).all()

def TestIsIn():
	Y = np.random.randint(0,10000,size = (100,))
	X = np.arange(10000)
	Z = isin(X,Y)
	D = np.array(uniqify(Y))
	D.sort()
	T1 = (X[Z] == D).all()
	
	X = np.array(range(10000) + range(10000))
	Z = isin(X,Y)
	T2 = (X[Z] == np.append(D,D.copy())).all()
	
	assert T1 & T2
	

def nullvalue(test):
	return False if isinstance(test,bool) else 0 if isinstance(test,int) else 0.0 if isinstance(test,float) else ''

def eq(x,y):
# x and y are tb.tabarrays 
	b = x==y
	if isinstance(b, bool):
		return b and ColorEq(x,y)
	else:
		return all(b) and ColorEq(x,y)

def ColorEq(x,y):
	return x.coloring.keys() == y.coloring.keys()  and all([x[k].dtype.names == y[k].dtype.names for k in x.coloring.keys()])

def eq3(X):
	return (all(X.A == X.A1) and all(X.R == X.R1) and all(X.D == X.D1))
	
def neq3(X):
	return (any((X.A != X.A1)) and any((X.R != X.R1)) and any((X.D != X.D1)))