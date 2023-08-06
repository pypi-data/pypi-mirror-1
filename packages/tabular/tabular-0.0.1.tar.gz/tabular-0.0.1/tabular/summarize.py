"""
Functions for manipulating :class:`tabular.tabarray.tabarray` 
objects:  aggregate, aggregate_in, pivot. 
"""

__all__ = ['aggregate', 'aggregate_in', 'pivot']

import numpy
import tabular as tb
from tabular import utils as utils
from tabular.colors import GrayScale

def aggregate(X, On=None, AggFuncDict=None, AggFunc=None, returnsort=False):
	"""
	Aggregate a tabarray on a set of specified factors, using 
	specified aggregation functions. 
	
	Intuitively, this function will aggregate the dataset *X* on a 
	set of columns, whose names are listed in *On*, so that the 
	resulting aggregate data set has one record for each unique 
	tuples of values in those columns.   
	
	The more factors listed in *On* argument, the "finer" is the 
	aggregation, the fewer factors, the "coarser" the aggregation.    
	For example, if::
	
		On = ['A','B']
		
	the resulting data set will have one record for each unique 
	value of pairs (a,b) in:: 
	
		X[['A','B']]
	
	The *AggFuncDict* argument specifies how to aggregate the 
	factors _not_ listed in *On*, e.g. the so-called *Off* columns. 
	For example, if 
	
		On = ['A','B'] 
		
	and *C* is some other column, then:: 
	
		AggFuncDict['C'] 
		
	is the function that will be used to reduce to a single value the 
	(potentially multiple) values in the *C* column corresponding 
	to unique values in the *A*, *B* columns.   
	
	For instance, if::

		AggFuncDict['C'] = numpy.mean

	then the result will be that the values in the *C* column 
	corresponding to a single *A*, *B* value will be averaged.  
	
	If an *Off* column is _not_ provided as a key in *AggFuncDict*, 
	a default aggregator function will be used:  the sum function 
	for numerical columns, concatenation for string columns.    	
	
	Implemented by the tabarray method :func:`tabular.tabarray.tabarray.aggregate`.
	
	**Parameters**
	
		**X** :  tabarray
		
			The tabarray to aggregate. 
	
		**On** :  list of  strings, optional
		
			List of column names in *X*.
	
		**AggFuncDict** :  dictionary, optional 
		
			Dictionary where
			
			*	keys are some (all) column names of *X* that are NOT 
				in *On*
		
			*	values are functions that can be applied to lists or 
				numpy arrays.
			
			This specifies how to aggregate the factors _not_ listed in 
			*On*, e.g. the so-called *Off* columns.
			
		**AggFunc**:  function, optional
		
			Function that can be applied to lists or numpy arrays, 
			specifying how to aggregate factors not listed in either 
			*On* or the keys of *AggFuncDict*, e.g. a "default" 
			aggregation function for the *Off* columns not explicitly 
			listed in *AggFuncDict*.
	
		**returnsort** :  boolean, optional
		
			Because the aggregation function sorts the original data, 
			there's an argsort that can be returned.  
			
			*	If this boolean is *True* the return value is	[A,s] where 
			
				*	A is the aggregated tabarray and 
				
				*	s is the sorting permutation on the original data set.  
			
			*	If *False* (the default) the return value is just A.
			
	**See also:** :func:`tabular.summarize.aggregate_in`
		
	"""
	
	names = X.dtype.names
	
	if On == None:
		On = []
	elif isinstance(On,str):
		On = On.split(',')
		
	assert all([o in names for o in On]), "Axes " + str([o for o in On if o not in names]) + " can't be found."
	Off = set(names).difference(On)
	
	if AggFuncDict == None:
		AggFuncDict = {}
		
	if AggFunc != None:
		AggFuncDict.update( dict([(o,AggFunc) for o in Off if o not in AggFuncDict.keys()]) )
		
	NotProvided = Off.difference(AggFuncDict.keys()) if AggFuncDict else Off
	if len(NotProvided) > 0:
		print 'No aggregation function provided for axes: ' , NotProvided, 'so assuming "sum".'
		AggFuncDict.update(dict([(o,sum) for o in NotProvided]))

	if len(On) > 0:	
		if len(On) == 1:
			[D,s] = utils.FastRecarrayUniqify(X[On[0]])
		else:
			[D,s] = utils.FastRecarrayUniqify(X[On])
		X = X[s]
		Diffs = numpy.append(numpy.append([-1],D[1:].nonzero()[0]),[len(D)])
	else:
		Diffs = numpy.array([-1,len(X)])

	ColDict = dict([(o,X[o][Diffs[:-1]+1]) for o in On])
	ColDict.update(dict([(o,[AggFuncDict[o](X[o][Diffs[i]+1:Diffs[i+1]+1]) for i in range(len(Diffs) - 1)]) for o in Off]))

	Columns = [ColDict[n] for n in names]
	
	if returnsort:
		return [tb.tabarray(columns=Columns, names=names, coloring=X.coloring), s]
	else:
		return tb.tabarray(columns=Columns, names=names, coloring=X.coloring)

def aggregate_in(Data, On=None, AggFuncDict=None, AggFunc=None, interspersed=True):
	"""
	Take aggregate of data set on specified columns, then add the 
	resulting rows back into data set to make a composite object 
	containing both original non-aggregate data rows as well as 
	the aggregate rows. 
	
	First read comments for :func:`tabular.summarize.aggregate`.
	
	This function returns a tabarray, with the number of rows 
	equaling::
	
		len(Data) + len(A)
	
	where *A* is the the result of::
	
		Data.aggregate(On,AggFuncDict)
	
	*A* represents the aggregate rows; the other rows were the 
	original data rows. 
			
	This function supports _multiple_ aggregation, meaning that 
	one can first aggregate on one set of factors, then repeat
	aggregation on the result for another set of factors, without 
	the results of the first aggregation interfering the second.  To 
	achieve this, the method adds (or augments, if already 
	present), some :attr:`rowdata` information, i.e. from 
	Data.rowdata. (See :func:`tabular.tabarray.tabarray.__new__` 
	for more information about rowdata). The specific rowdata 
	information added by :func:`tabular.summarize.aggregate_in` is a 
	column called "Aggregates" specifying on which factors the 
	rows that are aggregate rows were aggregated.  Rows added 
	by aggregating on factor *A* (a column in the original data 
	set) will have *A* in the "Aggregates" column of the 
	Data.rowdata array.  When multiple factors *A1*, *A2* , ... are 
	aggregated on, the notation is a comma-separated list::
	
		'A1,A2,...'
	
	This way, when you call :func:`tabular.summarize.aggregate_in`
	again, the function only aggregates on the columns that have 
	the empty char '' in their "Aggregates" rowdata.   
	
	The function also adds (or adds rows to) a '__color__' column to 
	Data.rowdata, specifying Gray-Scale colors for aggregated
	rows that will be used by the Data Environment system 
	browser for colorizing the  data.   When there are multiple 
	levels of aggregation, the coarser aggregate groups (e.g. on 
	fewer factors) get darker gray color then those on finer 
	aggregate groups (e.g. more factors).  
	
	Implemented by the tabarray method :func:`tabular.tabarray.tabarray.aggregate_in`.
	
	**Parameters**

		**Data** :  tabarray
			
			The tabarray to aggregate in. 
	
		**On** :  list of  strings, optional
		
			List of column names in *X*.
	
		**AggFuncDict** :  dictionary, optional 
		
			Dictionary where
			
			*	keys are some (all) column names of *X* that are NOT 
				in *On*
		
			*	values are functions that can be applied to lists or 
				numpy arrays.
			
			This specifies how to aggregate the factors _not_ listed in 
			*On*, e.g. the so-called *Off* columns.
			
		**AggFunc** :  function, optional
		
			Function that can be applied to lists or numpy arrays, 
			specifying how to aggregate factors not listed in either 
			*On* or the keys of *AggFuncDict*, e.g. a "default" 
			aggregation function for the *Off* columns not explicitly 
			listed in *AggFuncDict*.
			
		**interspersed** :  boolean, optional
		
			*	If *True*, aggregate rows are interleaved with the data 
				of which they are aggregates.
				
			*	If *False*, all aggregate rows placed at the end of the 
				array. 
				
	**See also:**  :func:`tabular.summarize.aggregate`
	
	"""
	
	#see if there's an Aggregates column in rowdata.  If so, strip off all those that atre non trivial 
	
	if Data.rowdata != None and 'Aggregates' in Data.rowdata.dtype.names:
			X = Data[Data.rowdata['Aggregates'] == ''][:]
			OldAggregates = Data[Data.rowdata['Aggregates'] != ''][:]
			AggVars = utils.uniqify(utils.ListUnion([x.split(',') for x in OldAggregates.rowdata['Aggregates']]))
	else:
		X = Data
		OldAggregates = Data[0:0]
		AggVars = []

	if On == None:
		On = []
		
	NewAggregates = aggregate(X, On, AggFuncDict=AggFuncDict, AggFunc=AggFunc)
	on = ','.join(On)
	NewAggregates.rowdata = numpy.rec.fromarrays([[on]*len(NewAggregates)], names=['Aggregates'])
	AggVars = utils.uniqify(AggVars + On)
	
	Aggregates = tb.datavstack([OldAggregates,NewAggregates])
	
	ANLen = numpy.array([len(x.split(',')) for x in Aggregates.rowdata['Aggregates']])
	U = numpy.array(utils.uniqify(ANLen)); U.sort()
	[A,B] = utils.fastequalspairs(ANLen,U)
	Grays = numpy.array(GraySpec(len(U)))
	AggColor = numpy.rec.fromarrays([Grays[A]],names = ['__color__'])
	
	Aggregates.rowdata = AddOrReplaceColumns(Aggregates.rowdata,AggColor)
	
	if not interspersed or len(AggVars) == 0:
		return tb.datavstack([X,Aggregates])
	else:
		#s = len(ANLen) - ANLen.argsort() - 1
		s = ANLen.argsort()
		Aggregates = Aggregates[s[range(len(Aggregates)-1,-1,-1)]]
		X.sort(order = AggVars)
		Diffs = numpy.append(numpy.append([0],1 + (X[AggVars][1:] != X[AggVars][:-1]).nonzero()[0]),[len(X)])		
		DiffAtts = ([[t for t in AggVars if X[t][Diffs[i]] != X[t][Diffs[i+1]]] for i in range(len(Diffs) - 2)] if len(Diffs) > 2 else []) + [AggVars]
		
		HH = {}
		for l in utils.uniqify(Aggregates.rowdata['Aggregates']):
			Avars = l.split(',')
			HH[l] = utils.FastRecarrayEqualsPairs(X[Avars][Diffs[:-1]], Aggregates[Avars])
		
		Order = []
		for i in range(len(Diffs)-1):
			Order.extend(range(Diffs[i],Diffs[i+1]))
			
			Get = []
			for l in HH.keys():
				Get += [len(X) + j  for j in HH[l][2][range(HH[l][0][i],HH[l][1][i])] if len(set(DiffAtts[i]).intersection(Aggregates.rowdata['Aggregates'][j].split(','))) > 0 and set(Aggregates.rowdata['Aggregates'][j].split(',')) == set(l.split(','))]

			Order.extend(Get)
		
		return tb.datavstack([X,Aggregates])[Order]

def AddOrReplaceColumns(X,Cols):
	"""
	Technical dependency of :func:`tabular.summarize.aggregate_in`. 
	
	**Parameters**
	
		**X** :  array with structured dtype
		
		**Cols**:  array with structured dtype
	
	"""
	return numpy.rec.fromarrays([X[a] for a in X.dtype.names if a not in Cols.dtype.names] + [Cols[a] for a in Cols.dtype.names], names = [a for a in X.dtype.names if a not in Cols.dtype.names] + list(Cols.dtype.names))
		
def GraySpec(k):
	"""
	For integer argument k, returns list of k gray-scale colors, 
	increasingly light, linearly in the HSV color space, as web hex triplets.  
	
	Technical dependency of :func:`tabular.summarize.aggregate_in`. 
	
	**Parameters**
	
		**k** :  positive integer
	
	"""
	ll = .5
	ul = .8
	delta = (ul - ll)/k
	return [GrayScale(t) for t in numpy.arange(ll,ul,delta)]

def pivot(X, a, b, Keep=None):
	'''
	Implements pivoting on tabarrays.  
	
	See http://en.wikipedia.org/wiki/Pivot_table for information 
	about pivot tables.

	Returns *X* pivoted on (a,b) with *a* as the row axis and *b* 
	values as the column axis. 
	
	So-called "nontrivial columns relative to *b*" in *X* are added 
	as color-grouped sets of columns, and "trivial columns relative 
	to *b*"  are also retained as cross-grouped sets of columns if 
	they are listed in *Keep* argument.   
	
	Note that a column *c* in *X* is "trivial relative to *b*" if for 
	all rows i, X[c][i] can be determined from X[b][i], e.g the 
	elements in X[c] are in many-to-any correspondence with the 
	values in X[b].
		
	The function will raise an exception if the list of pairs of values
	in X[[a,b]] is not the product of the individual columns values, e.g.::
	
		X[[a,b]] == set(X[a]) x set(X[b])
	
	in some ordering. 
	
	Implemented by the tabarray method :func:`tabular.tabarray.tabarray.pivot`
	
	**Parameters**
	
		**X** :  tabarray 
	
		**a** : string
		
			Column name in *X*.
			
		**b** : string
		
			Another column name in *X*.
	
		**Keep** :  list of strings, optional
		
			List of other columns names in *X*.
	
	'''

	for c in [a,b]:
		assert c in X.dtype.names, 'Column ' + c + ' not found'
		
	assert len(X) == len(set(X[[a,b]].tolist())) , 'Pairs of values in columns ' + a + ' and ' + b +  ' must be unique'
	Da = len(set(X[a]))
	Db = len(set(X[b]))
	assert len(X) == Da * Db, 'The set of pairs of values in columns ' + a + ' and ' + b +  ' must be the product of the two sets of values.'	
	X.sort(order = [a,b])
	Bvals = X[b][:Db]
	bnames = [str(bv).replace(' ','') for bv in Bvals]

	othernames = [o for o in X.dtype.names if o not in [a,b]]
	
	assert len(set(othernames).intersection(bnames)) == 0 and a not in bnames, 'Processed values of column ' + b + ' musn\'t intersect with other column names.'

	acol = X[a][::Db]

	Cols = [acol]
	names = [a]
	Trivials = []
	NonTrivials = []
	for c in othernames:
		Z = X[c].reshape((Da,Db)) 
		
		if all([len(set(Z[:,i])) == 1 for i in range(Z.shape[1])]):
			Trivials.append(c)
		else:
			NonTrivials.append(c)
			Cols += [Z[:,i] for i in range(Z.shape[1])]
			names += [bn + '_' + c for bn in bnames]
	D = tb.tabarray(columns=Cols, names=names)
	
	if Keep != None:
		Trivials = set(Trivials).intersection(Keep)
		for c in Trivials:
			X.sort(order=[c])
			cvals = numpy.array(uniqify(X[c]))
			[AA,BB] = utils.fastequalspairs(cvals,X[c])
			
			for (i,cc) in enumerate(cvals):
				blist = [str(bv).replace(' ','') for bv in Bvals if bv in X[b][AA[i]:BB[i]]]
				D.coloring[str(cc)] = [a] + [bn + '_' + d for bn in blist for d in NonTrivials]
				for d in NonTrivials:
					D.coloring[str(cc) + '_'  + d]  = [a] + blist
				
	for c in NonTrivials:
		D.coloring[c] = [a] + [bn + '_' + c for bn in bnames]
	for bn in bnames:
		D.coloring['_' + bn] = [a] + [bn + '_' + c for c in NonTrivials]
		
	return D