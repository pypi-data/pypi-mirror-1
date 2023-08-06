def assert_io(self, expr, fname):
	if expr:
		delete(fname)
		self.assert_(expr)
	else:
		self.assert_(expr)

def test_empty(self):
	D = tb.tabarray(dtype=self.D.dtype, coloring=self.D.coloring)
	self.assert_(self.D.dtype==D.dtype)

def test_save_load_TSV(self):
	fname = TestDataDir + self.Root + '.tsv'
	self.D.saveSV(fname)
	D = tb.tabarray(SVfile = fname)
	self.assert_io(eq(self.D, D), fname)

def test_save_load_CSV(self):
	fname = TestDataDir + self.Root + '.csv'
	self.D.saveSV(fname)
	D = tb.tabarray(SVfile = fname)
	self.assert_io(eq(self.D, D), fname)

def test_save_load_binary(self):
	fname = TestDataDir + self.Root + '.npz'
	self.D.savebinary(fname)
	D = tb.tabarray(binary = fname)
	self.assert_io(eq(self.D, D), fname)

def test_save_load_binary_data_only(self):
	fname = TestDataDir + self.Root + '.npy'
	self.D.savebinary(fname)
	D = tb.tabarray(binary = fname)
	self.assert_io(all(self.D == D), fname)

def test_save_load_HSV(self):
	fname = TestDataDir + self.Root + '.hsv/'
	self.D.saveHSV(fname)
	D = tb.tabarray(HSVfile = fname)
	self.assert_io(eq(self.D, D), fname)

def test_appendHSV_nocoloring(self):
	fname = TestDataDir + self.Root + '1.hsv/'
	D1 = self.D.copy()
	D1.coloring = {}
	ind = len(D1)/2
	D1[:ind].saveHSV(fname)
	D1[ind:].appendHSV(fname)
	D2 = tb.tabarray(HSVfile = fname)
	self.assert_io(eq(D1, D2), fname)

def test_savecolumns(self):
	fname = TestDataDir + self.Root + '2.hsv/'
	makedir(fname)
	D1 = self.D.copy()
	D1.coloring = {}
	names = list(D1.dtype.names)
	ind = len(names)/2		
	D1[names[:ind]].savecolumns(fname)
	D1[names[ind:]].savecolumns(fname)
	F = open(fname + 'header.txt', 'w')
	F.write('\n'.join(names))
	F.close()
	D2 = tb.tabarray(HSVfile = fname)
	self.assert_io(eq(D1, D2), fname)
	
def test_appendHSV_coloring(self):
	fname = TestDataDir + self.Root + '3.hsv/'
	D1 = self.D.copy()
	ind = len(D1)/2
	D1[:ind].saveHSV(fname)
	D1[ind:].appendHSV(fname)
	D2 = tb.tabarray(HSVfile = fname)
	self.assert_io(eq(D1, D2), fname)
	
# def test_web(self):
# 	fname = TestDataDir + self.Root + '10.hsv/'
# 	self.D.saveHSV(fname)
# 	dname = TestDataDir + self.Root + '_web/'
# 	makedir(dname)
# 	from System.config.SetupFunctions import SERVERNAME
# 	tb.tabular2html(htmlFile = dname + self.Root + '.html', FileInName = fname, SERVERNAME = SERVERNAME)

def test_addrecords_tuple(self):
	D = self.D[:-1].copy()
	x = self.D[-1].tolist()
	D1 = D.addrecords(x)
	self.assert_(isinstance(x, tuple) & eq(D1,self.D))
	
def test_addrecords_void(self):
	D = self.D[:-1].copy()
	x = np.array([self.D[-1]], dtype=self.D.dtype.descr)[0]
	D1 = D.addrecords(x)
	self.assert_(isinstance(x, np.void) & eq(self.D, D1))

def test_addrecords_record(self):
	D = self.D[:-1].copy()
	x = self.D[-1]
	D1 = D.addrecords(x)
	self.assert_(isinstance(x, np.record) & eq(self.D, D1))

def test_addrecords_tuples(self):
	ind = len(self.D)/2
	D = self.D[:ind].copy()
	x = self.D[ind:].tolist()
	D1 = D.addrecords(x)
	self.assert_(isinstance(x[0], tuple) & eq(self.D, D1))
	
def test_addrecords_voids(self):
	ind = len(self.D)/2
	D = self.D[:ind].copy()
	x = np.array([rec for rec in self.D[ind:].tolist()], dtype=self.D.dtype.descr)
	x = [v for v in x]
	D1 = D.addrecords(x)
	self.assert_(isinstance(x[0], np.void) & eq(self.D, D1))

def test_addrecords_records(self):
	ind = len(self.D)/2
	D = self.D[:ind].copy()
	x = self.D[ind:]
	D1 = D.addrecords(x)
	self.assert_(isinstance(x[0], np.record) & eq(self.D, D1))

def test_rowstack(self):
	ind = len(self.D)/2
	self.assert_(eq(self.D, (self.D[:ind]).rowstack(self.D[ind:])))
	
def test_colstack(self):
	names = list(self.D.dtype.names)
	ind = len(names)/2
	self.assert_(all(self.D == (self.D[names[:ind]]).colstack(self.D[names[ind:]])))
	
def test_equals(self):
	D = self.D
	self.assert_(eq(self.D, D) and self.D is D)
	
def test_equals_copy(self):
	D = self.D.copy()
	self.assert_(eq(self.D, D) and not self.D is D)		