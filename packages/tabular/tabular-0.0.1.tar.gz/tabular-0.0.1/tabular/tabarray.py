'''
Class and functions pertaining to the :class:`tabarray` class, a 
column-oriented hierarchical data object and subclass of 
`numpy.recarray <http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html?highlight=recarray#numpy.recarray>`_. 

'''

__all__ = ['tabarray', 'nullvalue']

import numpy, os
import tabular.io as io
import tabular.shape_base as sb
import tabular.summarize as summarize
import tabular.utils as utils

def modifydocs(a, b, desc=''):
	"""
	Convenience function for writing documentation. For a class
	method *a* that is essentially a wrapper for an outside 
	function *b*, rope in the docstring from *b* and append to that 
	of *a*.  Also modify the docstring of *a* to get indentation 
	right. 
	
	"""
	newdoc = a.func_doc.replace('\t\t', '\t')
	newdoc += "Documentation from " + desc + ":\n" + b.func_doc
	return newdoc

class tabarray(numpy.core.records.recarray):
	"""
	tabarray is a column-oriented data object based on the numpy 
	recarray (a tabular data object with named columns, each a 
	uniform Python type), with added functionality and ability to 
	define named groups of columns.
	
	tabarray supports several i/o methods to/from a number of file 
	formats, including (separated variable) text (e.g. ``.txt``, 
	``.tsv``, ``.csv``), numpy binary (``.npz``) and hierarchical separated variable (``.hsv``). 
	
	Added functionality includes spreadsheet style operations 
	such as "pivot" and "aggregate".

	**Invariants**

		The names of all columns are distinct (unique) within one 
		:mod:`tabarray`.
	
	**QuickStart**
	
		Try the following in an interactive Python session. Start by typing:
		
		>>> from tabular.tabarray import tabarray
	
		**Get data into a tabarray and do stuff (Part 1)**
		
		Create a tabarray from records (rows) of mixed data types. 
		Notice that data types are inferred (str, int, float).

		>>> x = tabarray(records=[('bork', 1, 3.5), ('stork', 2, -4.0)])
		>>> x
		tabarray([('bork', 1, 3.5), ('stork', 2, -4.0)], 
		      dtype=[('f0', '|S5'), ('f1', '<i4'), ('f2', '<f8')])
		
		Basic properties

		>>> len(x)					# number of records
		2
		>>> len(x.dtype)				# number of columns
		3
		>>> x.dtype.names				# default column names
		('f0', 'f1', 'f2')

		Indexing and slicing
		
		>>> x['f1']					# index on a column (returns a numpy array)
		array([1, 2])
		>>> x[['f0','f2']]				# index on a list of columns (returns a tabarray)
		tabarray([('bork', 3.5), ('stork', -4.0)], 
		      dtype=[('f0', '|S5'), ('f2', '<f8')])
		>>> x[0]					# index on a row (returns a numpy record)
		('bork', 1, 3.5)
		>>> x[1:]					# get a slice (returns a tabarray)
		tabarray([('stork', 2, -4.0)], 
		      dtype=[('f0', '|S5'), ('f1', '<i4'), ('f2', '<f8')])
		
		**Get data into a tabarray and do stuff (Part 2)**
		
		Create a tabarray from columns of data, each a specific type, and name the columns.
		
		>>> x = tabarray(columns=[['bork', 'stork'], [1, 2], [3.5, -4.0]], names=['a','b','c'])	
		>>> x
		tabarray([('bork', 1, 3.5), ('stork', 2, -4.0)], 
		      dtype=[('a', '|S5'), ('b', '<i4'), ('c', '<f8')])

		Coloring:  tabarray attribute describing hierarchical structure on the columns

		>>> x.coloring = {'data': ['b','c']}		# add hierarchical structure to the columns
		>>> x['data']					# index on a coloring key
		tabarray([(1, 3.5), (2, -4.0)],	
		      dtype=[('b', '<i4'), ('c', '<f8')])

		Getting data into numpy to do math

		>>> y = x['data'].extract()			# extract data to a numpy array
		>>> y
		array([[ 1. ,  3.5],
		       [ 2. , -4. ]])
		>>> y * 2					# now you can do math, etc.
		array([[ 2.,  7.],
		       [ 4., -8.]])

		Filtering plus indexing

		>>> x['b']==2					# x['b'] is a numpy array
		array([False,  True], dtype=bool)
		>>> x[x['b']==2]				# index on a boolean array
		tabarray([('stork', 2, -4.0)], 
		      dtype=[('a', '|S5'), ('b', '<i4'), ('c', '<f8')])
		>>> x[x['b']==2]['c']				# combine filtering and indexing
		array([-4.])
		
	"""

	def __new__(subtype, array=None, records=None, columns=None, SV=None, binary=None, HSV=None, HSVlist=None, shape=None, dtype=None, formats=None, names=None, titles=None, aligned=False, byteorder=None, comments='#', delimiter=None, delimiter_regex=None, linebreak=None, skiprows=0, usecols=None, toload=None, structuredheader=True, namesinheader=True, valuefixer=None, linefixer=None, coloring=None, rowdata=None, wrap=None):
		"""		   	
		**Unified constructor for tabarrays.** 
		
		**Specifying the data** 
		
			Data can be passed to the constructor, or loaded from 
			several different file formats. The constructor first 
			creates a :class:`numpy.rec.recarray`. If provided, the 
			constructor adds two attributes:
				
				:attr:`coloring` : column-oriented hierarchical structure
				
				:attr:`rowdata` : per-row structured data
		
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
			
			**SV** :  string 
			
				File path to a separated variable (SV) text file.  Load 
				data from a SV by calling::
				
					tabular.io.loadSV(SV, comments, delimiter, delimiter_regex,
								linebreak, skiprows, usecols, toload, structuredheader,
								namesinheader, valuefixer, linefixer)	
				
				**See also:**  :func:`saveSV`, :func:`tabular.io.loadSV`

		
			**binary** :  string 
			
				File path to a binary file. Load a ``.npz`` binary file created by the 
				:func:`savebinary` by calling::
				
					tabular.io.loadbinary(binary)
				
				which uses :func:`numpy.load`.
								
				**See also:** :func:`savebinary`, :func:`tabular.io.loadbinary`
		
			**HSV** :  string 
			
				File path to a hierarchical separated variable (``.hsv``) 
				directory, or a separated variable (SV) text file inside of 
				a HSV directory corresponding to a single column of 
				data.  Load a structured directory or single file defined 
				by the :func:`saveHSV` method by calling::
				
					tabular.io.loadHSV(HSV, toload)
				
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

			**coloring**:  hierarchical column-oriented structure

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
			
			**rowdata**:  per-row structured data
				
				The *rowdata* argument must either be *None* (no  
				rowdata) or a :class:`numpy.rec.recarray` record array 
				the same length as the data set.  This rowdata is 
				meant to represent "row-by-row" metadata.   These are 
				columns that you don't really want to appear in 
				displays of the data set, but which are meant to "travel 
				with" the data no matter what subsetting you do on the 
				"real data" columns, so that the rowdata columns will 
				still be there without your explicitly having to 
				remember them.   
			
				One use of :attr:`rowdata` columns is for formatting and 
				communicating "side" information to other 
				:class:`tabarray` methods. For instance, various 
				specially designated columns in the :attr:`rowdata` 
				information can be used to tell other applications that 
				use :class:`tabarray` objects how to interpret the rows 
				in a way that would be tedious for the user to have to 
				remember to supply. Two instances of this are:
					
				*	A '__color__' column present in the :attr:`rowdata` is 
					specially interpreted by the browser's tabular-to- 
					html representation. It is expected in each row to 
					contain a web-safe hex triplet color specification, 
					e.g. a string of the form '#XXXXXX' (see 
					http://en.wikipedia.org/wiki/Web_colors).  
				
				*	The 'Aggregates' column is used to disambiguate 	
					rows that are aggregates of data in other sets of 
					rows for the :func:`aggregate_in` method (see 
					comments on that below). 
				
				Rowdata information can also be used to specify 
				arbitrary higher-level groups of rows, in analogy to how 
				the *coloring* attribute specifies groupings of columns.   
				This would work either by: 
			
				*	storing in a .rowdata column whose name specifies 
					group name, a boolean in each row as to whether the 
					row belongs to that group, or
					
				*	for a "type" of grouping consisting of several 
					nonintersecting row groups, a single column 
					specifying by some string or integer code which 
					group the row belongs to.  (An example of this is the 
					"Aggregates" column used by the .aggregate_in 
					method, see below for info about this.) 
					
			**wrap**:  string 
				
				Adds a color with name 	*wrap* listing all column 
				names. (When this  :class:`tabarray` is saved to a 
				``.hsv`` directory, all columns will be nested in an 
				additional directory, ``wrap.hsv``.)					
	
			**subtype**:  class
			
				The class object for the actual type of the newly 
				created type(:class:`tabarray`) object; this will be 
				either type(:class:`tabarray`) or the type of a subclass).

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
		elif not SV is None:
			chkExists(SV)
			# Returned DataObj is a list of numpy arrays
			[DataObj, givennames, givencoloring] = io.loadSV(fname=SV, comments=comments, delimiter=delimiter, delimiter_regex=delimiter_regex, skiprows=skiprows, usecols=usecols, toload=toload, structuredheader=structuredheader, namesinheader=namesinheader, valuefixer=valuefixer, linefixer=linefixer)		
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
			[DataObj, givendtype, givencoloring, givenrowdata] = io.loadbinary(fname=binary)
			if (dtype is None) and (not givendtype is None):
				dtype = givendtype
			if (coloring is None) and (not givencoloring is None):
				coloring = givencoloring
			if (rowdata is None) and (not givenrowdata is None):
				rowdata = givenrowdata
			DataObj = numpy.rec.fromrecords(DataObj, dtype=dtype, shape=shape, formats=formats, names=names, titles=titles, aligned=aligned, byteorder=byteorder)
		elif not HSV is None:
			chkExists(HSV)	
			# Returned DataObj is a list of numpy arrays
			[DataObj, givennames, givencoloring, givenrowdata] = io.loadHSV(path=HSV, toload=toload)
			if (names is None) and (not givennames is None):
				names = givennames
			if (coloring is None) and (not givencoloring is None):
				coloring = givencoloring
			if (rowdata is None) and (not givenrowdata is None):
				rowdata = givenrowdata
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
			
		self.rowdata = rowdata

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
		Used to set default attributes (e.g. *coloring*, *rowdata*) if 
		*obj* does not have them.  
		
		Note:  this is called when you view a :class:`numpy.ndarray` 
		as a :class:`tabarray`.
		
		"""
		self.coloring = getattr(obj, 'coloring', {})
		self.rowdata = getattr(obj, 'rowdata', None)

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
		*type(ind)*. Also, whether the returned object represents 
		a new independent copy of the subrectangle, or a "view" 
		into this self object, depends on *type(ind)*.

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
				*len(self)*, 	the rectangle contains copies of the rows 
				for which the corresponding entry is *True*. 
				
			*	if you pass a list of row numbers, you get a *tabarray* 
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
				D.coloring = dict([(k,self.coloring[k]) for k in self.coloring.keys() if set(self.coloring[k]) < set(D.dtype.names)])		
				if not self.rowdata is None:
					if isinstance(ind,list) and all([a in self.dtype.names or a in self.coloring.keys() for a in ind]):
						D.rowdata = self.rowdata
					else:
						D.rowdata = self.rowdata[ind]
			return D	
			
	def __getslice__(self,ind1,ind2):
		"""
		Returns a slice into the array: a contiguous range of its 
		rows.  This is not a copy but a mutable reference into the 
		array.
		
		"""
		D = numpy.core.records.recarray.__getslice__(self,ind1,ind2)
		if not self.rowdata is None:
			D.rowdata = self.rowdata[ind1:ind2]
		return D	

	def addrecords(self,new):
		"""
		Append one or more records to the end of the array. Can 
		take a single record, void or tuple, or a list of records, 
		voids or tuples.
		
		"""
		if isinstance(new,numpy.record) or isinstance(new,numpy.void) or isinstance(new,tuple):
			new = [new]		
		if not self.rowdata is None:
			newrowdata = numpy.rec.fromarrays([[nullvalue(self.rowdata[l][0])]*len(new) for l in self.rowdata.dtype.names], names=self.rowdata.dtype.names)
			rowdata = utils.SimpleStack1([self.rowdata,newrowdata])
		else:
			rowdata = None		
		return tabarray(array = numpy.append(self, numpy.rec.fromrecords(new, dtype=self.dtype), axis=0), dtype=self.dtype, coloring=self.coloring, rowdata=rowdata)
		
	def deletecols(self,cols):
		"""
		Delete columns.  Can take a string giving a column or
		coloring name, or a list of such strings. 
		
		"""	
		if isinstance(cols, str):
			cols = [cols]
		deletenames = utils.uniqify(utils.ListUnion([[c] if c in self.dtype.names else self.coloring[c] for c in cols]))
		return self[[n for n in self.dtype.names if n not in deletenames]]
		
	def renamecol(self,old,new):
		"""
		Rename column or color. Takes the old name and the
		new name.
		
		"""
		if old in self.dtype.names:
			if old not in self.coloring.values():
				coloring = self.coloring
			else:
				coloring = {}
				for key in self.coloring.keys():
					coloring[key] = [v if v != old else new for v in self.coloring[key]]
			return tabarray(records=self, formats=[self.dtype[i].str for i in range(len(self.dtype))], names=[n if n != old else new for n in self.dtype.names], coloring=coloring)
		else:
			coloring = {}
			for key in self.coloring.keys():
				if key != old:
					coloring[key] = self.coloring[key]
				else:
					coloring[new] = self.coloring[key]
			return tabarray(records=self, dtype=self.dtype, coloring=coloring)

	def saveSV(self, fname, comments='#', delimiter=None, linebreak=None, headerkeys=['coloring','types','names']):
		"""
		Save the tabarray to a single flat file.  Column headers are 
		kept, but colorings are lost.
		
		Method calls:: 	
		
			tabular.io.saveSV(fname, self, comments, delimiter, linebreak, headerkeys)
		
		"""
		io.saveSV(fname=fname, X=self, comments=comments, delimiter=delimiter, linebreak=linebreak, headerkeys=headerkeys)
	saveSV.func_doc = modifydocs(saveSV, io.saveSV, ":func:`tabular.io.saveSV`")
		
	def savebinary(self, fname, savecoloring=True, saverowdata=True):
		"""
		Save the tabarray to a ``.npz`` zipped file containing ``.npy`` 
		binary files for data, plus optionally coloring and/or rowdata 
		or simply to a ``.npy`` binary file containing the data but no 
		coloring or rowdata. 
		
		Method calls:: 
		
			tabular.io.savebinary(fname, self, savecoloring, saverowdata)
		
		"""
		io.savebinary(fname=fname, X=self, savecoloring=savecoloring, saverowdata=saverowdata)
		io.savebinary(fname=fname, X=self)
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
		
		Method calls::
		
			tabular.io.saveHSV(fname, self, printheaderfile)
		
		"""
		io.saveHSV(fname=fname, X=self, printheaderfile=printheaderfile)
	saveHSV.func_doc = modifydocs(saveHSV, io.saveHSV, ":func:`tabular.io.saveHSV`")
	
	def savecolumns(self, fname):
		"""
		Save the tabarray to a set of flat ``.csv`` files in ``.hsv`` 
		format (e.g. ``.int.csv``, ``.float.csv``, ``.str.csv``). Note that 
		data in the attributes *coloring* and *rowdata* are lost.
		
		Method calls:: 
		
			tabular.io.savecolumns(fname, self)
		
		"""
		io.savecolumns(fname=fname, X=self)
	savecolumns.func_doc = modifydocs(savecolumns, io.savecolumns, ":func:`tabular.io.savecolumns`")
		
	def appendHSV(self, fname, order=None):
		"""
		Like :func:`saveHSV` but for appending instead of writing 
		from scratch.  
		
		Method calls::
			
			tabular.io.appendHSV(fname, self, order)
		
		"""
		io.appendHSV(fname=fname, RecObj=self, order=order)
	appendHSV.func_doc = modifydocs(appendHSV, io.appendHSV, ":func:`tabular.io.appendHSV`")
	
	def appendcolumns(self, fname, order=None):
		"""
		Like :func:`savecolumns` but for appending instead of writing 
		from scratch.  
		
		Method calls:: 
		
			tabular.io.appendcolumns(fname, self, order)
		
		"""
		io.appendcolumns(fname=fname, RecObj=self, order=order)
	appendcolumns.func_doc = modifydocs(appendcolumns, io.appendcolumns, ":func:`tabular.io.appendcolumns`")

	def hstack(self, new):
		"""
		Create a new tabarray that has columns of *self* followed 
		by columns of *new*, with the names and colorings 
		correctly merged.  :attr:`rowdata` is merged using 
		:func:`tabular.summarize.SafeColumnStack`.  Note that if there are 
		repeated column names from different arrays, no exception 
		is raised and the data from the first array that has that 
		rowdata is taken.
		
		Method calls::
			
			tabular.shape_base.datahstack([self, new])
		
		"""
		return sb.datahstack([self, new])
	hstack.func_doc = modifydocs(hstack, sb.datahstack, ":func:`tabular.shape_base.datahstack`")
	
	def vstack(self, new):
		"""		
		Create a new tabarray that has rows of *self* followed by 
		rows of *new*, with the names, colorings and rowdata 
		correctly merged.
		
		Method calls:: 
		
			tabular.shape_base.datavstack([self, new])
		
		"""
		return sb.datavstack([self, new])
	vstack.func_doc = modifydocs(vstack, sb.datavstack, ":func:`tabular.shape_base.datavstack`")
		
	def aggregate(self, On=None, AggFuncDict=None, AggFunc=None, returnsort=False):
		"""
		Create a new tabarray by aggregating on a set of specified 
		factors, using specified aggregation functions. 
		
		Method calls::
		
			tabular.summarize.aggregate(self, On, AggFuncDict, AggFunc, returnsort)
		
		"""
		return summarize.aggregate(X=self, On=On, AggFuncDict=AggFuncDict, AggFunc=AggFunc, returnsort=returnsort)
	aggregate.func_doc = modifydocs(aggregate, summarize.aggregate, ":func:`tabular.summarize.aggregate`")
	
	def aggregate_in(self, On=None, AggFuncDict=None, AggFunc=None, interspersed=True):
		"""
		Create a new tabarray by taking an aggregate of tabarray on 
		specified columns, then adding the resulting rows back into 
		data set to make a composite object containing both 
		original non-aggregate data rows as well as the aggregate 
		rows.  
		
		See the :func:`aggregate` method.
		
		Method calls:: 
		
			tabular.summarize.aggregate_in(self, On, AggFuncDict, AggFunc, interspersed)
		
		"""
		return summarize.aggregate_in(Data=self, On=On, AggFuncDict=AggFuncDict, AggFunc=AggFunc, interspersed=interspersed)
	aggregate_in.func_doc = modifydocs(aggregate_in, summarize.aggregate_in, ":func:`tabular.summarize.aggregate_in`")

	def pivot(self, a, b, Keep=None):
		"""
		Pivot with *a* as the row axis and *b* values as the column axis. 	
		
		Method calls::
		
			tabular.summarize.pivot(X, a, b, Keep)
		
		"""
		return summarize.pivot(X=self, a=a, b=b, Keep=Keep)
	pivot.func_doc = modifydocs(pivot, summarize.pivot, ":func:`tabular.summarize.pivot`")
	
	def replace(self, old, new, strict=True, cols=None, rows=None):
		"""
		Replace value *old* with *new* everywhere it appears. 

		**Parameters**
		
			**old** : string
			
			**new** : string
		
			**strict** :  boolean, optional
		
			*	If *strict* = *True*, replace only exact occurences of 
				*old*.
		
			*	if *strict* = *False*, assume *old* and *new* are 
				strings and  replace all occurences of substrings (e.g. 
				like :func:`str.replace`)
			
			**cols** :  list of strings, optional
			
				Names of columns to make replacements in; if *None*, 
				make replacements everywhere. 
				
			**rows** : list of booleans or integers, optional
			
				Rows to make replacements in; if *None*, make 
				replacements everywhere.
		
		Note:  This function does in-place replacements.  Thus 
		there are issues handling data types here when replacement 
		dtype is larger than original dtype.  This can be resolved 
		later by making a new array when necessary ... 
		
		"""
		
		if cols is None:
			cols = self.dtype.names
			
		if rows is None:
			rows = numpy.ones((len(self),), bool)
			
		if strict:
			new = numpy.array(new)
			for a in cols:
				if self.dtype[a] < new.dtype:
					print 'WARNING: dtype of column', a, 'is inferior to dtype of ', new, 'which may cause problems.'
				self[a][(self[a] == old)[rows]] = new
		else:
			for a in cols:
				QuickRep = True
				if not rows is None:
					colstr = ''.join(self[a][rows])
				else:
					colstr = ''.join(self[a])		
				avoid = [ord(o) for o in utils.uniqify(old + new + colstr)]
				ok = set(range(256)).difference(avoid)
				if len(ok) > 0:
					sep = chr(list(ok)[0])
				else:
					ok = set(range(65536)).difference(avoid)
					if len(ok) > 0:
						sep = unichr(list(ok)[0])
					else:
						print 'All unicode characters represented in column', a ,', can\t replace quickly.'
						QuickRep = False
						
				if QuickRep:
					newrows = numpy.array(sep.join(self[a][rows]).replace(old,new).split(sep))			
				else:
					newrows = numpy.array([aa.replace(old,new) for aa in self[a][rows]])
				self[a][rows] = numpy.cast[self.dtype[a]](newrows)
					
				if newrows.dtype > self.dtype[a]:
						print 'WARNING: dtype of column', a, 'is inferior to dtype of its replacement which may cause problems.'
	
def nullvalue(test):
	"""
	Returns a null value for each of various kinds of test values:
	
		*	if *test* is a *bool*, return *False*
		*	else if *test* is an *int*, return *0*
		*	else if *test* is a *float*, return *0.0*
		*	else *test* is a *str*, return *''*
	"""
	return False if isinstance(test,bool) else 0 if isinstance(test,int) else 0.0 if isinstance(test,float) else ''
	
def chkExists( path ):
    """If the given file or directory does not exist, raise an exception"""
    if not os.path.exists(path): raise IOError("Directory or file %s does not exist" % path)