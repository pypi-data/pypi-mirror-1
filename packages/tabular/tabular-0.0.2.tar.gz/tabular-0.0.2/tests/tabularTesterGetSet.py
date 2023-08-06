def test_eq(self):
	self.assert_(eq3(self))

def test_SF(self):
	# n[S][F] = something -- resets n
	x = self.A[1:]['f2']
	self.A[1:]['f2'] = x + 1
	self.R[1:]['f2'] = x + 1
	self.D[1:]['f2'] = x + 1
	self.assert_(neq3(self))
	
def test_FS(self):
	# n[F][S] = something -- resets n
	x = self.A['f2'][1:]
	self.A['f2'][1:] = x + 1
	self.R['f2'][1:] = x + 1
	self.D['f2'][1:] = x + 1
	self.assert_(neq3(self))
	
def test_Fi(self):
	# n[F][i] = something -- resets n
	x = self.A['f2'][[1,3]]
	self.A['f2'][[1,3]] = x + 1
	self.R['f2'][[1,3]] = x + 1
	self.D['f2'][[1,3]] = x + 1
	self.assert_(neq3(self))
	
def test_iF(self):
	# n[i][F] = something -- does nothing
	x = self.A[[1,3]]['f2']
	self.A[[1,3]]['f2'] = x + 1
	self.R[[1,3]]['f2'] = x + 1
	self.D[[1,3]]['f2'] = x + 1
	self.assert_(eq3(self))
	
def test_FS_(self):
	# V = n[F][S], V = something -- does nothing
	x = self.A.copy()['f2'][1:]
	A = self.A['f2'][1:]
	R = self.R['f2'][1:]
	D = self.R['f2'][1:]
	A = x + 1
	R = x + 1
	D = x + 1
	self.assert_(eq3(self))
	
def test_Fi_(self):
	# V = n[F][i], V = something -- does nothing
	x = self.A.copy()['f2'][[1,3]]
	A = self.A['f2'][[1,3]]
	R = self.R['f2'][[1,3]]
	D = self.R['f2'][[1,3]]
	A = x + 1
	R = x + 1
	D = x + 1
	self.assert_(eq3(self))
	
def test_iF_(self):
	# V = n[i][F], V = something -- does nothing
	x = self.A.copy()[[1,3]]['f2']
	A = self.A[[1,3]]['f2']
	R = self.R[[1,3]]['f2']
	D = self.R[[1,3]]['f2']
	A = x + 1
	R = x + 1
	D = x + 1
	self.assert_(eq3(self))
	
def test_Fi_S(self):
	# V = n[F][i], V[S] = something -- does nothing
	x = self.A.copy()['f2'][[1,3]]
	A = self.A['f2'][[1,3]]
	R = self.R['f2'][[1,3]]
	D = self.R['f2'][[1,3]]
	A[:] = x + 1
	R[:] = x + 1
	D[:] = x + 1
	self.assert_(eq3(self))

def test_FS_S(self):
	# V = n[F][S], V[S] = something -- resets n
	x = self.A.copy()['f2'][1:]
	A = self.A['f2'][1:]
	R = self.R['f2'][1:]
	D = self.D['f2'][1:]
	A[:] = x + 1
	R[:] = x + 1
	D[:] = x + 1
	self.assert_(neq3(self))
	
def test_FS_i(self):
	# V = n[F][S], V[i] = something -- resets n
	x = self.A.copy()['f2'][1:]
	A = self.A['f2'][1:]
	R = self.R['f2'][1:]
	D = self.D['f2'][1:]
	i = range(len(A)-1)
	A[i] = x + 1
	R[i] = x + 1
	D[i] = x + 1
	self.assert_(neq3(self))