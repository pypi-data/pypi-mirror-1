'''
Class and functions pertaining to the :class:`tabarray` class, a 
column-oriented hierarchical data object and subclass of 
`numpy.recarray <http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html?highlight=recarray#numpy.recarray>`_. 

The basic structure of this module is that it contains:

*	The tabarray class.

*	Some helper functions for tabarray.  The helper functions are 
	precisely those necessary to wrap functions from the 
	:mod:`tabular.spreadsheet` module that operate on lists of 
	arrays, to handle tabular's additional structure.   These functions 
	are named with the convention "tab_FNAME", e.g. "tab_rowstack", 
	"tab_join" &c.    The functions in :mod:`tabular.spreadsheet` that 
	only take a single array are all wrapped JUST as methods of 
	tabarray, and not as separate functions.    

'''

__all__ = ['tabarray', 'tab_colstack', 'tab_rowstack','tab_join']

import numpy, os
import tabular.io as io
import tabular.spreadsheet as spreadsheet
import tabular.utils as utils

def modifydocs(a, b, desc=''):
	"""
	Convenience function for writing documentation. 
	
	For a class method `a` that is essentially a wrapper for an 
	outside function `b`, rope in the docstring from `b` and append 
	to that of `a`.  Also modify the docstring of `a` to get the
	indentation right. 
	
	**Parameters**
	
		**a** :  class method
		
			Class method wrapping `b`.
		
		**b** :  function

			Function wrapped by `a`.

		**desc** :  string, optional
		
			Description of `b`, e.g. restructured text providing a link
			to the documentation for `b`.  Default is an empty string.

	**Returns**
	
		**newdoc** :  string
		
			New docstring for `a`.
	
	"""
	newdoc = a.func_doc.replace('\t\t', '\t')
	newdoc += "Documentation from " + desc + ":\n" + b.func_doc
	return newdoc

def tab_colstack(ListOfTabArrays, mode='abort'):
	'''
	"Horizontal stacking" of tabarrays, e.g. adding columns. 
	
	Wrapper for :func:`tabular.spreadsheet.colstack` that deals 
	with the coloring and returns the result as a tabarray.
	
	Method calls::
	
		data = tabular.spreadsheet.colstack(ListOfTabArrays, mode=mode)
	
	'''

	data = spreadsheet.colstack(ListOfTabArrays, mode=mode)

	coloring = {}
	for a in ListOfTabArrays:
		for k in a.coloring:
			if k in coloring.keys():
				coloring[k] = utils.uniqify(coloring[k] + a.coloring[k])
			else:
				coloring[k] = a.coloring[k]
		
	for k in coloring.keys():
		s = [x for x in coloring[k] if x in data.dtype.names]
		if len(s) > 0:
			coloring[k] = s
		else:
			coloring.pop(k)
	
	data = data.view(tabarray)
	data.coloring = coloring
	return data
tab_colstack.func_doc = modifydocs(tab_colstack, spreadsheet.colstack, ":func:`tabular.spreadsheet.colstack`")

def tab_rowstack(ListOfTabArrays, mode='nulls'):
	'''
	"Vertical stacking" of tabarrays, e.g. adding rows. 

	Wrapper for :func:`tabular.spreadsheet.rowstack` that deals 
	with the coloring and returns the result as a tabarray.
	
	Method calls::
	
		data = tabular.spreadsheet.rowstack(ListOfTabArrays, mode=mode)

	'''

	data = spreadsheet.rowstack(ListOfTabArrays, mode=mode)
	
	coloring = {}
	for a in ListOfTabArrays:
		for k in a.coloring:
			if k in coloring.keys():
				coloring[k] = utils.uniqify(coloring[k] + a.coloring[k])
			else:
				coloring[k] = a.coloring[k]
	for k in coloring.keys():
		s = [x for x in coloring[k] if x in data.dtype.names]
		if len(s) > 0:
			coloring[k] = s
		else:
			coloring.pop(k)

	data = data.view(tabarray)
	data.coloring = coloring
	return data		
tab_rowstack.func_doc = modifydocs(tab_rowstack, spreadsheet.rowstack, ":func:`tabular.spreadsheet.rowstack`")	

def tab_join(ToMerge,keycols=None,nullvals=None,renamer=None,returnrenaming=False,Names = None):

	'''
	Database-join for tabular arrays.

	Wrapper for :func:`tabular.spreadsheet.join` that deals 
	with the coloring and returns the result as a tabarray.
	
	Method calls::
	
		data = tabular.spreadsheet.join

	'''

	[Result,Renaming] = spreadsheet.join(ToMerge,keycols=keycols,nullvals=nullvals,renamer=renamer,returnrenaming=True,Names = Names)
	
	if isinstance(ToMerge,dict):
		Names = ToMerge.keys()
	else:
		Names = range(len(ToMerge))
		
	Colorings = dict([(k,ToMerge[k].coloring) if 'coloring' in dir(ToMerge[k]) else {} for k in Names])
	for k in Names:
		if k in Renaming.keys():
			l = ToMerge[k]
			Colorings[k] = dict([(g,[n if not n in Renaming[k].keys() else Renaming[k][n] for n in l.coloring[g]]) for g in Colorings[k].keys()])
	Coloring = {}
	for k in Colorings.keys():
		for j in Colorings[k].keys():
			if j in Coloring.keys():
				Coloring[j] = utils.uniqify(Coloring[j] + Colorings[k][j])
			else:
				Coloring[j] = utils.uniqify(Colorings[k][j])
	
	Result = Result.view(tabarray)
	Result.coloring = Coloring

	if returnrenaming:
		return [Result,Renaming]
	else:
		return Result

	
class tabarray(numpy.core.records.recarray):
	"""
	Subclass of the numpy recarray with extra structure and functionality.
	
	tabarray is a column-oriented data object based on the numpy 
	recarray (a tabular data object with named columns, each a 
	uniform Python type), with added functionality and ability to 
	define named groups of columns.
	
	tabarray supports several i/o methods to/from a number of file 
	formats, including (separated variable) text (e.g. ``.txt``, 
	``.tsv``, ``.csv``), numpy binary (``.npz``) and hierarchical separated 
	variable (``.hsv``). 
	
	Added functionality includes spreadsheet style operations 
	such as "pivot", "aggregate" and "replace".

	**Invariants**

		The names of all columns are distinct (unique) within one 
		:mod:`tabarray`.
		
	"""

	def __new__(subtype, array=None, records=None, columns=None, SVfile=None, binary=None, HSVfile=None, HSVlist=None, shape=None, dtype=None, formats=None, names=None, titles=None, aligned=False, byteorder=None, comments='#', delimiter=None, delimiter_regex=None, linebreak=None, skiprows=0, usecols=None, toload=None, metadatadict=None, namesinheader=True, headerlines=None, valuefixer=None, linefixer=None, coloring=None, wrap=None):
		"""		   	
		**Unified constructor for tabarrays.** 
		
		**Specifying the data** 
		
			Data can be passed to the constructor, or loaded from 
			several different file formats. The constructor first 
			creates a :class:`numpy.rec.recarray`. If provided, the 
			constructor adds the **coloring** attribute, which is
			a dictionary that represents hierarchical structure on
			the columns, (e.g. groups of column names). 
		
			**array** :  two-dimensional arrays (:class:`numpy.ndarray`)
				
				Load data to a :class:`numpy.rec.recarray` by calling::
				
					numpy.rec.fromrecords(array, dtype, shape, formats, 
								names, titles, aligned, byteorder)
				 
				unless creating an empty data structure.

				>>> x = numpy.array([[1,2,3],[4,5,6]])
				>>> tabarray(array=x)
				tabarray([(1, 2, 3), (4, 5, 6)], 
				      dtype=[('f0', '<i4'), ('f1', '<i4'), ('f2', '<i4')])
				
				**See also:**  `numpy.rec.fromrecords <http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.records.fromrecords.html#numpy.core.records.fromrecords>`_
		
			**records** :  list of records
			
				Load data to a :class:`numpy.rec.recarray` by calling::
				
					numpy.rec.fromrecords(records, dtype, shape, formats, 
								names, titles, aligned, byteorder)
		
				Notes from :func:`numpy.rec.fromrecords`:  The data in 
				the same field can be heterogeneous, they will be 
				promoted to the highest data type. This method is 
				intended for creating smaller record arrays. If used to 
				create large array without formats defined, e.g.::
		
					r = fromrecords([(2,3.,'abc')]*100000)
		
				it can be slow. If formats is *None*, then this will 
				auto-detect formats. Use list of tuples rather than list 
				of lists for faster processing.
				
				>>> tabarray(records=[('bork', 1, 3.5), ('stork', 2, -4.0)], names=['x','y','z'])
				tabarray([('bork', 1, 3.5), ('stork', 2, -4.0)], 
				      dtype=[('x', '|S5'), ('y', '<i4'), ('z', '<f8')])
				
				**See also:**  `numpy.rec.fromrecords <http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.records.fromrecords.html#numpy.core.records.fromrecords>`_
		
			**columns** :  list of one-dimensional arrays (:class:`numpy.ndarray`)
			
				Load data to a :class:`numpy.rec.recarray` by calling::
				
					numpy.rec.fromarrays(records, dtype, shape, formats, 
								names, titles, aligned, byteorder)
				
				Fastest when passed a list of numpy arrays, rather than 
				a list of lists. 
				
				>>> tabarray(columns=[['bork', 'stork'], [1, 2], [3.5, -4.0]], names=['x','y','z'])
				tabarray([('bork', 1, 3.5), ('stork', 2, -4.0)], 
				      dtype=[('x', '|S5'), ('y', '<i4'), ('z', '<f8')])
			
			**See also:**  `numpy.rec.fromarrays <http://docs.scipy.org/doc/numpy/reference/generated/numpy.core.records.fromrecords.html#numpy.core.records.fromarrays>`_
			
			**SVfile** :  string 
			
				File path to a separated variable (SV) text file.  Load 
				data from a SV by calling::
				
					tabular.io.loadSV(SVfile, comments, delimiter, delimiter_regex,
								linebreak, skiprows, usecols, toload, structuredheader,
								namesinheader, valuefixer, linefixer)	
				
				**See also:**  :func:`saveSV`, :func:`tabular.io.loadSV`

		
			**binary** :  string 
			
				File path to a binary file. Load a ``.npz`` binary file created by the 
				:func:`savebinary` by calling::
				
					tabular.io.loadbinary(binary)
				
				which uses :func:`numpy.load`.
								
				**See also:** :func:`savebinary`, :func:`tabular.io.loadbinary`
		
			**HSVfile** :  string 
			
				File path to a hierarchical separated variable (``.hsv``) 
				directory, or a separated variable (SV) text file inside of 
				a HSV directory corresponding to a single column of 
				data.  Load a structured directory or single file defined 
				by the :func:`saveHSV` method by calling::
				
					tabular.io.loadHSV(HSVfile, toload)
				
				**See also:** :func:`saveHSV`, :func:`tabular.io.loadHSV`, :func:`tabular.io.loadHSVlist`
		
			**HSVlist** :  list of strings 
			
				List of file paths to hierarchical separated variable 
				(``.hsv``) files and/or individual comma-separated 
				variable (``.csv``) text files inside of HSV directories, all 
				with the same number of records.  Load a list of file 
				paths created by the :func:`saveHSV` method by 
				calling::
				
					tabular.io.loadHSVlist(HSVlist)
				
				**See also:**  :func:`saveHSV`,  :func:`tabular.io.loadHSV`, :func:`tabular.io.loadHSVlist`

		**Additional parameters**

			**coloring**:  dictionary
			
				Hierarchical column-oriented structure

			*	Colorings can be passed as argument:
			
				*	In the *coloring* argument, pass a dictionary. Each 
					key is a string naming a color whose corresponding 
					value is a list of column names (strings) in that 
					color.
			
				*	If colorings are passed as argument, they override 
					any colorings inferred from the input data.
				
			*	Colorings can be inferred from the input data:
			
				*	If constructing from a ``.hsv`` directory, colorings will 	
					be automatically inferred from the directory tree.
					
				*	If constructing from a SV file (e.g. ``.tsv``, ``.csv``) 
					created by :func:`saveSV`, colorings are 
					automatically parsed from the header.
					
				*	If constructing from a numpy binary file (e.g. ``.npz``)
					created by :func:`savebinary`, colorings are 
					automatically loaded from a binary file 
					(``coloring.npy``) in the ``.npz`` directory.
					
			**wrap**:  string 
				
				Adds a color with name 	*wrap* listing all column 
				names. (When this  :class:`tabarray` is saved to a 
				``.hsv`` directory, all columns will be nested in an 
				additional directory, ``wrap.hsv``.)					
	
			**subtype**:  class
			
				The class object for the actual type of the newly 
				created type(:class:`tabarray`) object; this will be 
				either type(:class:`tabarray`) or the type of a subclass).
			
		**Special column names**
				
				Column names that begin and end with double
				underscores, e.g. '__column_name__' may be used 
				to hold row-by-row metadata.  
			
				One use of these special columns is for formatting 
				and communicating "side" information to other 
				:class:`tabarray` methods. For instance, various 
				specially designated columns can be used to tell 
				other applications that use :class:`tabarray` objects 
				how to interpret the rows in a way that would be 
				tedious for the user to have to remember to supply. 
				
				Two instances of this are used by the `aggregate_in` 
				function, :func:`tabular.spreadsheet.aggregate_in`:
					
				*	A '__color__' column can be interpreted by a 
					browser's tabular-to-html representation. It is 
					expected in each row to contain a web-safe hex 
					triplet color specification, e.g. a string of the form 
					'#XXXXXX' (see http://en.wikipedia.org/wiki/Web_colors).  
				
				*	The '__aggregates__' column is used to disambiguate 	
					rows that are aggregates of data in other sets of 
					rows for the ``.aggregate_in`` method (see 
					comments on that below). 
				
				This row-by-row information can also be used to specify 
				arbitrary higher-level groups of rows, in analogy to how 
				the `coloring` attribute specifies groupings of columns.   
				This would work either by: 
			
				*	storing in a special column whose name specifies
					group name, a boolean in each row as to whether the 
					row belongs to that group, or
					
				*	for a "type" of grouping consisting of several 
					nonintersecting row groups, a single column 
					specifying by some string or integer code which 
					group the row belongs to.  (An example of this is the 
					"__aggregates__" column used by the ``.aggregate_in``
					method, see below for info about this.) 

		"""
		
		if not array is None:
			if len(array) > 0:
				DataObj = numpy.rec.fromrecords(array, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
			else:
				DataObj = numpy.rec.fromarrays([[]]*len(array.dtype), dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not records is None:
			DataObj = numpy.rec.fromrecords(records, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not columns is None:
			DataObj = numpy.rec.fromarrays(columns, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not SVfile is None:
			chkExists(SVfile)
			# Returned DataObj is a list of numpy arrays
			[DataObj, givennames, givencoloring] = io.loadSV(fname=SVfile, comments=comments, delimiter=delimiter, delimiter_regex=delimiter_regex, skiprows=skiprows, usecols=usecols, toload=toload, metadatadict=metadatadict, namesinheader=namesinheader, headerlines=headerlines, valuefixer=valuefixer, linefixer=linefixer)		
			if (names is None) and (not givennames is None):
				names = givennames
			if (coloring is None) and (not givencoloring is None):
				coloring = givencoloring
			DataObj = numpy.rec.fromarrays(DataObj, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not binary is None:
			# This uses numpy.load, which for .npz files creates a temporary directory somewhere. 
			# Find out where this is and if the System requires a work-around.
			chkExists(binary)
			# Returned DataObj is a numpy ndarray with structured dtype
			[DataObj, givendtype, givencoloring] = io.loadbinary(fname=binary)
			if (dtype is None) and (not givendtype is None):
				dtype = givendtype
			if (coloring is None) and (not givencoloring is None):
				coloring = givencoloring
			DataObj = numpy.rec.fromrecords(DataObj, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not HSVfile is None:
			chkExists(HSVfile)	
			# Returned DataObj is a list of numpy arrays
			[DataObj, givennames, givencoloring] = io.loadHSV(path=HSVfile, toload=toload)
			if (names is None) and (not givennames is None):
				names = givennames
			if (coloring is None) and (not givencoloring is None):
				coloring = givencoloring
			DataObj = numpy.rec.fromarrays(DataObj, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not HSVlist is None:
			[chkExists(x) for x in HSVlist]
			return io.loadHSVlist(flist=HSVlist)
		else:
			DataObj = numpy.core.records.recarray.__new__(numpy.core.records.recarray, shape, dtype=dtype, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)

		self = numpy.core.records.recarray.__new__(subtype, DataObj.shape, dtype=DataObj.dtype, names=names)
		if not coloring is None:
			coloringsInNames = list(set(coloring.keys()).intersection(set(self.dtype.names)))
			if len(coloringsInNames) == 0:
				self.coloring = coloring				
			else:
				print "Warning: the following coloring keys,", coloringsInNames, ", are also attribute (column) names in the tabarray. This is not allowed, and so these coloring keys will be deleted. The corresponding columns of data will not be lost and will retain the same names."
				for c in coloringsInNames:
					coloring.pop(c)
				self.coloring = coloring
		else:
			self.coloring = {}		


		if not wrap is None:
			self.coloring[wrap] = self.dtype.names
	
		if not self.dtype.names is None:
			for attrib in self.dtype.names:
				self[attrib] = DataObj[attrib]	
			return self
		else:
			return DataObj

	def __array_finalize__(self, obj):
		"""
		Used to set default attributes (e.g. `coloring`) if 
		`obj` does not have them.  
		
		Note:  this is called when you view a :class:`numpy.ndarray` 
		as a :class:`tabarray`.
		
		"""
		self.coloring = getattr(obj, 'coloring', {})
		
	def extract(self):
		"""
		Creates a copy of this :class:`tabarray` in the form of a 
		:class:`numpy.ndarray`.

		Useful if you want to do math on array elements, e.g. if you 
		have a subset of the columns that are all numerical, you can 
		construct a numerical matrix and do matrix operations.		
		
		"""
		return numpy.vstack([self[r] for r in self.dtype.names]).T.squeeze()		
		
	def __getitem__(self,ind):
		"""
		Returns a subrectangle of the table.

		The representation of the subrectangle depends on 
		`type(ind)`. Also, whether the returned object represents 
		a new independent copy of the subrectangle, or a "view" 
		into this self object, depends on `type(ind)`.

		*	If you pass the name of an existing coloring, you get a 
			tabarray consisting of copies of columns in that 
			coloring.

		*	If you pass a list of existing coloring names and/or column 
			names, you get a tabarray consisting of copies of columns 
			in the list (name of coloring is equivalent to list of names 
			of columns in that coloring; duplicate columns are 
			deleted).

		*	If you pass a :class:`numpy.ndarray`, you get a tabarray 
			consisting a subrectangle of the tabarray, as handled by 
			:func:`numpy.core.recarray.__getitem__`:
			
			*	if you pass a 1D NumPy ndarray of booleans of 
				`len(self)`, 	the rectangle contains copies of the rows 
				for which the corresponding entry is `True`. 
				
			*	if you pass a list of row numbers, you get a tabarray
				containing copies of these rows.
		
		"""
		if ind in self.coloring.keys():
			return self[self.coloring[ind]]
		elif isinstance(ind,list) and all([a in self.dtype.names or a in self.coloring.keys() for a in ind]) and set(self.coloring.keys()).intersection(ind):
			ns = utils.uniqify(utils.ListUnion([[a] if a in self.dtype.names else self.coloring[a] for a in ind]))
			return self[ns]
		else:
			D = numpy.core.records.recarray.__getitem__(self,ind)
			if isinstance(D,numpy.ndarray) and not D.dtype.names is None:
				D = D.view(tabarray)				
				D.coloring = dict([(k,list(set(self.coloring[k]).intersection(set(D.dtype.names)))) for k in self.coloring.keys() if len(set(self.coloring[k]).intersection(set(D.dtype.names))) > 0 and len(set(D.dtype.names).difference(self.coloring[k])) > 0])		
				#D.coloring = dict([(k,self.coloring[k]) for k in self.coloring.keys() if set(self.coloring[k]) < set(D.dtype.names)])		
			return D	
			

	def addrecords(self, new):
		"""
		Append one or more records to the end of the array. 
		
		Method wraps:: 
		
			tabular.spreadsheet.addrecords(self, new)
		
		"""
		data = spreadsheet.addrecords(self,new)
		data = data.view(tabarray)
		data.coloring = self.coloring
		return data
	addrecords.func_doc = modifydocs(addrecords, spreadsheet.addrecords, ":func:`tabular.spreadsheet.addrecords`")

	def addcols(self, cols, names=None):
		"""
		Add one or more new columns.  
		
		Method wraps:: 
		
			tabular.spreadsheet.addcols(self, cols, names)
		
		"""
		data = spreadsheet.addcols(self, cols, names)
		data = data.view(tabarray)
		data.coloring = self.coloring
		return data
	addcols.func_doc = modifydocs(addcols, spreadsheet.addcols, ":func:`tabular.spreadsheet.addcols`")
		
	def deletecols(self, cols):
		"""
		Delete columns and/or colors.  
		
		Method wraps:: 
		
			tabular.spreadsheet.deletecols(self, cols)
			
		"""	
		deletenames = utils.uniqify(utils.ListUnion([[c] if c in self.dtype.names else self.coloring[c] for c in cols]))
		return spreadsheet.deletecols(self,deletenames)
	deletecols.func_doc = modifydocs(deletecols, spreadsheet.deletecols, ":func:`tabular.spreadsheet.deletecols`")		
		
	def renamecol(self, old, new):
		"""
		Rename column or color in-place. 
		
		Method wraps:: 
		
			tabular.spreadsheet.renamecol(self, old, new)
			
		"""	
		spreadsheet.renamecol(self,old,new)
		for x in self.coloring.keys():
			if old in self.coloring[x]:
				ind = self.coloring[x].index(old)
				self.coloring[x][ind] = new 
	renamecol.func_doc = modifydocs(renamecol, spreadsheet.renamecol, ":func:`tabular.spreadsheet.renamecol`")		
			
	def saveSV(self, fname, comments='#', delimiter=None, linebreak=None, metadatakeys=['coloring','types','names'], printmetadatadict=True, strongmetadata=False):
		"""
		Save the tabarray to a single flat file.  Column headers are 
		kept, but colorings are lost.
		
		Method wraps:: 	
		
			tabular.io.saveSV(fname, self, comments, delimiter, linebreak, metadatakeys, printmetadatadict, strongmetadata)
		
		"""
		io.saveSV(fname=fname, X=self, comments=comments, delimiter=delimiter, linebreak=linebreak, metadatakeys=metadatakeys, printmetadatadict=printmetadatadict, strongmetadata=strongmetadata)
	saveSV.func_doc = modifydocs(saveSV, io.saveSV, ":func:`tabular.io.saveSV`")
		
	def savebinary(self, fname, savecoloring=True):
		"""
		Save the tabarray to a ``.npz`` zipped file containing ``.npy`` 
		binary files for data, plus optionally coloring and/or rowdata 
		or simply to a ``.npy`` binary file containing the data but no 
		coloring or rowdata. 
		
		Method wraps:: 
		
			tabular.io.savebinary(fname, self, savecoloring, saverowdata)
		
		"""
		io.savebinary(fname=fname, X=self, savecoloring=savecoloring)
	savebinary.func_doc = modifydocs(savebinary, io.savebinary, ":func:`tabular.io.savebinary`")

	def saveHSV(self, fname, printheaderfile=True):
		"""
		Save the tabarray to a ``.hsv`` directory.  Each column is 
		saved as a separate comma-separated variable file (``.csv``), 
		whose name includes the column name and data type of the 
		column (e.g. ``name.int.csv``, ``name.float.csv``, 
		``name.str.csv``). 
		
		Hierarchical structure on the columns, i.e. :attr:`coloring`, is 
		preserved by the file directory structure, with subdirectories 
		named ``color.hsv`` and containing ``.csv`` files 
		corrseponding to columns of data grouped by that color. 
		
		Finally, :attr:`rowdata` is stored as a dump of a pickled 
		object in the top level directory *fname*.  
		
		The ``.hsv`` can later be loaded back by passing the file path 
		*fname* to the *HSV* argument of the :class:`tabarray` 
		constructor.
		
		Method wraps::
		
			tabular.io.saveHSV(fname, self, printheaderfile)
		
		"""
		io.saveHSV(fname=fname, X=self, printheaderfile=printheaderfile)
	saveHSV.func_doc = modifydocs(saveHSV, io.saveHSV, ":func:`tabular.io.saveHSV`")
	
	def savecolumns(self, fname):
		"""
		Save the tabarray to a set of flat ``.csv`` files in ``.hsv`` 
		format (e.g. ``.int.csv``, ``.float.csv``, ``.str.csv``). Note that 
		data in the attributes *coloring* and *rowdata* are lost.
		
		Method wraps:: 
		
			tabular.io.savecolumns(fname, self)
		
		"""
		io.savecolumns(fname=fname, X=self)
	savecolumns.func_doc = modifydocs(savecolumns, io.savecolumns, ":func:`tabular.io.savecolumns`")
		
	def appendHSV(self, fname, order=None):
		"""
		Like :func:`saveHSV` but for appending instead of writing 
		from scratch.  
		
		Method wraps::
			
			tabular.io.appendHSV(fname, self, order)
		
		"""
		io.appendHSV(fname=fname, RecObj=self, order=order)
	appendHSV.func_doc = modifydocs(appendHSV, io.appendHSV, ":func:`tabular.io.appendHSV`")
	
	def appendcolumns(self, fname, order=None):
		"""
		Like :func:`savecolumns` but for appending instead of writing 
		from scratch.  
		
		Method wraps:: 
		
			tabular.io.appendcolumns(fname, self, order)
		
		"""
		io.appendcolumns(fname=fname, RecObj=self, order=order)
	appendcolumns.func_doc = modifydocs(appendcolumns, io.appendcolumns, ":func:`tabular.io.appendcolumns`")

	def colstack(self, new, mode='abort'):
		"""
		Horizontal stacking for tabarrays.
		
		Stack tabarray(s) in `new` to the right of `self`.
		
		**See also**
			
			:func:`tabular.tabarray.tab_colstack`, :func:`tabular.spreadsheet.colstack`
		
		"""
		if isinstance(new,list):
			return tab_colstack([self] + new,mode)
		else:
			return tab_colstack([self,new],mode)
			
	colstack.func_doc = modifydocs(colstack, spreadsheet.colstack, ":func:`tabular.spreadsheet.colstack`")
	
	def rowstack(self, new, mode='nulls'):
		"""		
		Vertical stacking for tabarrays.
		
		Stack tabarray(s) in `new` below `self`.
		
		**See also**
			
			:func:`tabular.tabarray.tab_rowstack`, :func:`tabular.spreadsheet.rowstack`
		
		"""
		if isinstance(new,list):
			return tab_rowstack([self] + new,mode)
		else:
			return tab_rowstack([self, new],mode)
		
	rowstack.func_doc = modifydocs(rowstack, spreadsheet.rowstack, ":func:`tabular.spreadsheet.rowstack`")
		
	def aggregate(self, On=None, AggFuncDict=None, AggFunc=None, returnsort=False):
		"""
		Aggregate a tabarray on columns for given functions. 
		
		Method wraps::
		
			tabular.spreadsheet.aggregate(self, On, AggFuncDict, AggFunc, returnsort)
		
		"""
		if returnsort:
			[data,s] = spreadsheet.aggregate(X=self, On=On, AggFuncDict=AggFuncDict, AggFunc=AggFunc, returnsort=returnsort)	
		else:
			data = spreadsheet.aggregate(X=self, On=On, AggFuncDict=AggFuncDict, AggFunc=AggFunc,returnsort=returnsort)
		data = data.view(tabarray)
		data.coloring = self.coloring
		if returnsort:
			return [data,s]
		else:	
			return data		
	aggregate.func_doc = modifydocs(aggregate, spreadsheet.aggregate, ":func:`tabular.spreadsheet.aggregate`")
	
	def aggregate_in(self, On=None, AggFuncDict=None, AggFunc=None, interspersed=True):
		"""
		Aggregate a tabarray and include original data in the result.
		
		See the :func:`aggregate` method.
		
		Method wraps:: 
		
			tabular.summarize.aggregate_in(self, On, AggFuncDict, AggFunc, interspersed)
		
		"""
		data = spreadsheet.aggregate_in(Data=self, On=On, AggFuncDict=AggFuncDict, AggFunc=AggFunc, interspersed=interspersed)
		data = data.view(tabarray)
		data.view = self.coloring
		return data
		
	aggregate_in.func_doc = modifydocs(aggregate_in, spreadsheet.aggregate_in, ":func:`tabular.spreadsheet.aggregate_in`")

	def pivot(self, a, b, Keep=None, NullVals = None, prefix = '_'):
		"""
		Pivot with `a` as the row axis and `b` values as the column axis. 	
		
		Method wraps::
		
			tabular.spreadsheet.pivot(X, a, b, Keep)
		
		"""
		[data,coloring] = spreadsheet.pivot(X=self, a=a, b=b, Keep=Keep, NullVals=NullVals, prefix=prefix)
		data = data.view(tabarray)
		data.coloring = coloring
		return data
		
	pivot.func_doc = modifydocs(pivot, spreadsheet.pivot, ":func:`tabular.spreadsheet.pivot`")
	
	def replace(self, old, new, strict=True, cols=None, rows=None):
		spreadsheet.replace(self,old,new,strict,cols,rows)
	
	def join(self,ToMerge,keycols = None,nullvals = None,renamer = None,returnrenaming=False,selfname = None, Names = None):
		"""
		Wrapper for spread.join, but handles coloring attributes.   
		
		"selfname" argument allows naming of self to be used if ToMerge is a dictionary.
		
		Method wraps::
			
			tabular.spreadsheet.join
		"""
	
		if isinstance(ToMerge,numpy.ndarray):
			ToMerge = [ToMerge]
				
		if isinstance(ToMerge,dict):
			assert selfname not in ToMerge.keys(), 'Can\'t use name "' + selfname + '" for name of one of things to merge, since its the same name as the self object.'	
			if selfname == None:
				try:
					selfname = self.name
				except AttributeError:
					selfname = 'self'		
			ToMerge.update({selfname:self})
		else:
			ToMerge = [self] + ToMerge

		return tab_join(ToMerge,keycols=keycols,nullvals=nullvals,renamer=renamer,returnrenaming=returnrenaming,Names = Names)
	
	def argsort(self, axis=-1, kind='quicksort', order=None):
		"""
		Returns the indices that would sort an array.

		.. note:: 

			This method wraps `numpy.argsort`.  This documentation is modified 
			from that of `numpy.argsort`.
		
		Perform an indirect sort along the given axis using the algorithm specified
		by the `kind` keyword. It returns an array of indices of the same shape as
		the original array that index data along the given axis in sorted order.
		
		**Parameters**
			
			**axis** : int or None, optional
			
				Axis along which to sort.  The default is -1 (the last axis). If None,
				the flattened array is used.
			
			**kind** : {'quicksort', 'mergesort', 'heapsort'}, optional
			
				Sorting algorithm.
			
			**order** : list, optional
			
				This argument specifies which fields to compare first, second, etc.  
				Not all fields need be specified.
		
		**Returns**
		
			**	index_array** : ndarray, int
			
				Array of indices that sort the tabarray along the specified axis.
				In other words, ``a[index_array]`` yields a sorted `a`.
			
			**See Also**

				sort : Describes sorting algorithms used.
				lexsort : Indirect stable sort with multiple keys.
				ndarray.sort : Inplace sort.
			
			**Notes**

				See `numpy.sort` for notes on the different sorting algorithms.
			
			**Examples**

				Sorting with keys:
				
				>>> x = tabarray([(1, 0), (0, 1)], dtype=[('x', '<i4'), ('y', '<i4')])
				>>> x
				tabarray([(1, 0), (0, 1)], 
				      dtype=[('x', '<i4'), ('y', '<i4')])

				>>> x.argsort(order=('x','y'))
				array([1, 0])

				>>> x.argsort(order=('y','x'))
				array([0, 1])
		
		"""
		index_array = numpy.core.fromnumeric._wrapit(self, 'argsort', axis, kind, order)
		index_array = index_array.view(numpy.ndarray)
		return index_array
	
def chkExists( path ):
    """If the given file or directory does not exist, raise an exception"""
    if not os.path.exists(path): raise IOError("Directory or file %s does not exist" % path)