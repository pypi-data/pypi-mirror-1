"""
Functions for :class:`tabular.tabarray.tabarray` i/o methods, 
including to/from separated-value and other text files, binary 
files, hierarchical tabular format.
"""

__all__ = ['loadSV', 'saveSV', 'loadbinary', 'savebinary', 'loadHSV', 'saveHSV', 'savecolumns', 'loadHSVlist', 'appendHSV', 'appendcolumns', 'loadrowdata', 'typeinfer', 'infercoloring', 'inferdelimiter']

import numpy, types, csv, cPickle, os, shutil
from numpy import int64
import tabular as tb
from tabular import utils as utils
	
def loadSV(fname, comments='#', delimiter='\t', delimiter_regex=None, linebreak='\n', skiprows=0, usecols=None, toload=None, structuredheader=True, namesinheader=True, valuefixer=None, linefixer=None, returnasrecords=False):
	"""
	Takes a tabular text file with the specified delimeter and end-
	of-line character, and return [columns, names], where:

		**columns** :  list of one-dimensional numpy arrays 
		
			List of typed numpy arrays corresponding to columns of 
			data, each a uniform NumPy data type.
			
		**names** :  list of strings, or None
			
			List of column names given in the header of the file 
			(optional). 

	unless *returnasrecords* is *True*. 

	**Parameters**

		**fname** :  string or file object

			Path (or file object) corresponding to a separated variable 
			(SV) text file. 
		
		**comments** :  string, optional
			
			The string denoting the start of a comment, e.g. '#'.  Note 
			that the default is '#'.
		
		**delimiter** :  string, optional
		
			The string that separates values in each line of text, e.g. 
			'\\t'.  By default, this is inferred from the file extension:
			
				*	if the file ends in `.tsv`, the delimiter is '\\t'
				*	if the file ends in `.csv`, the delimiter is ','
		
			If the delimiter cannot be inferred and is not given, it is
			assumed to be '\\t'.  Note that this is different from the 
			default for :func:`numpy.loadtxt`, which is any 
			whitespace. 
			
			**See also:**  :func:`tabular.io.inferdelimiter`

		**delimiter_regex** : reguiar expression, optional
		
			Regular expression decribing the delimiter.
		
		**linebreak** :  string, optional
		
			The string separating lines of text, e.g. '\\n'.  By default, 
			this is assumed to be '\\n'. Note that the file is opened 
			using the "read universal" option::
			
				file(fname, 'rU')
		
		**skiprows** :  non-negative integer, optional
		
			The first *skiprows* lines are ignored. 
		
		**usecols** :  sequence of non-negative integers, optional
		
			If *usecols* is not *None*, only the columns it lists are
			loaded, with 0 being the first column.

		**toload** :  list of strings, optional
		
			List of strings corresponding to a subset of column 
			names; only these columns are loaded. 	
	
		**structuredheader** :  boolean, optional
		
			Denotes whether or not meta-metadata is in the header, 
			referring to the format used by :func:`tabular.io.saveSV`, 
			described below.  Up to four pieces of special metadata 
			may exist in the header: coloring, types, formats, names.
			(Note that types and formats are more or less redundant.)
			Each of these is represented by a line in the header (e.g.
			a line at the top beginning withe *comments*), followed 
			by a string describing the metadata and then an equals 
			sign, e.g. '#coloring=' for *comments='#'*. 
			
			Structured metadata is defined as follows:
			
				coloring:  string representation of coloring dictionary
				
				types:  delimiter-separated list of column types
				(e.g. 'int', 'str', 'float')
				
				formats:  delimiter-separated list of column formats
				
				names:  delimiter-separated list of column names
	
			If neither 'types' nor 'formats' is in the structured metadata,
			then the data type of each column is inferred. 

		**namesinheader** :  boolean, optional
			
			If *structuredheader == False* and *namesinheader == True*,
			then it is assumed that the column names are in the last line 
			beginning with *comments* (if *comments* != ''), or the first 
			line after the first *skiprows* lines (otherwise). 
					
		**returnasrecords** :  boolean, optional
		
			If *True*, return a list of parsed records. 
	
		**valuefixer** : lambda function 
		
			Lambda function to apply to all values in the SV.
	
		**linefixer** : lambda function
		
			Lambda function to apply to every line in the SV.
	
	**See also:**  :func:`tabular.io.loadSV`, :func:`tabular.io.saveSV`,
	:func:`tabular.io.typeinfer`
	
	"""

	names = None
	formats = None
	coloring = None

	if delimiter is None:
		delimiter = inferdelimiter(fname)

	if is_string_like(fname):
		fh = file(fname, 'rU')
	elif hasattr(fname, 'readline'):
		fh = fname
	else:
		raise ValueError('fname must be a string or file handle')	

	F = fh.read().strip(linebreak).split(linebreak)[skiprows:]
	fh.close()

	if linefixer: F = map( linefixer, F )
	if delimiter_regex:
		if isinstance( delimiter_regex, types.StringType ):
			import re
			delimiter_regex = re.compile( delimiter_regex )
		F = map( lambda line: delimiter_regex.sub( delimiter, line ), F )

	headerlines = 0
	if comments != '':
		for line in F:
			if line[:len(comments)] == comments:
				headerlines += 1
			else:
				break

	metadata = {}
	
	if structuredheader is True:
		headerdata = F[:headerlines]
		F = F[headerlines:]	
		for line in headerdata:
			line = line[len(comments):]
			if line.split('=')[0] in ['names', 'formats', 'types', 'coloring']:
				if len(line.split('='))==2:
					if line.split('=')[0] == 'coloring':
						metadata['coloring'] = line.split('=')[1]
					else:
						metadata[line.split('=')[0]] = list(csv.reader([line.split('=')[1]], delimiter=delimiter))[0]	
	else:
		if namesinheader is True:
			if comments != '':
				print "Assuming that the last line in ", fname, " beginning with '", comments, "' has attribute names."
				headerdata = F[:headerlines]
				F = F[headerlines:]					
				namesline = headerdata[-1][len(comments):]
			else:
				print "Assuming that the first line in ", fname, " after the first ", skiprows, " lines has attribute names."
				headerdata = F[0]
				F = F[1:]
				namesline = headerdata
			metadata['names'] = list(csv.reader([namesline], delimiter=delimiter))[0]
				

	if 'names' in metadata.keys():
		names = metadata['names']
	else:
		names = ['f'+str(i) for i in range(headerlines)]
	if 'formats' in metadata.keys():
		formats = metadata['formats']
	elif 'types' in metadata.keys():
		formats = metadata['types']
	else:
		formats = None		# need to infer types in this case
	if 'coloring' in metadata.keys():
		coloring = eval(metadata['coloring'])
		if '' in coloring.keys():
			coloring.pop('')
	else:
		coloring = {}

	records = F
	
	# Restrict the columns to the subset requested by the user
	if not toload is None:		
		usecols = list(set(utils.ListUnion([[names.index(TL)] if TL in names else [names.index(c) for c in coloring[TL]] for TL in toload])))
		usecols.sort()

	# parse data records on the delimiter
	records = list(csv.reader(records, delimiter=delimiter))

	if usecols is None:
	 	if not toload is None:
		 	usecols = [names.index(TL) for TL in toload]
		 	usecols.sort()
		elif not names is None:
			usecols = range(len(names))
		else:
			usecols = range(len(records[0]))

	if not names is None:
		names = [names[i] for i in usecols]
	if not coloring is None:
		coloring = thresholdcoloring(coloring, names)	

	if returnasrecords:
		records = [[record[column] for column in usecols] for record in records]
		return [records, names, coloring]

	if not names is None:
		for r in records:
			assert len( r ) >= len( names )
	
	# Type the columns and save to a list of (attribute) columns, each a numpy array
	if valuefixer is None:
		if not formats is None:
			columns = [numpy.array([record[column] for record in records], formats[column]) for column in usecols]
		else:
			columns = [typeinfer([record[column] for record in records]) for column in usecols]
	else:
		if not formats is None:
			columns = [numpy.array([valuefixer( record[column] ) for record in records], formats[column]) for column in usecols]
		else:
			columns = [typeinfer([valuefixer( record[column] ) for record in records]) for column in usecols]
	
	return [columns, names, coloring]
	
def saveSV(fname, X, comments='#', delimiter=None, linebreak=None, headerkeys=['coloring','types','names']):
	"""
	Save a tabarray to a separated-variable (tabular) file.

	**Parameters**
	
		**fname** :  string 

			Path to a separated variable (SV) text file. 

		**X** :  tabarray
		
			The actual data in a :class:`tabular.tabarray.tabarray`.
		
		**comments** :  string, optional
			
			The string denoting the start of a comment, e.g. '#'.  Note 
			that the default is '#'.
		
		**delimiter** :  string, optional
		
			The string that separates values in each line of text, e.g. 
			'\\t'.  By default, this is inferred from the file extension:
			
				*	if the file ends in `.tsv`, the delimiter is '\\t'
				*	if the file ends in `.csv`, the delimiter is ','
		
			If the delimiter cannot be inferred and is not given, it is
			assumed to be '\\t'.  Note that this is different from the 
			default for :func:`numpy.loadtxt`, which is any 
			whitespace. 
			
		**linebreak** :  string, optional
		
			The string separating lines of text, e.g. '\\n'.  By default, 
			this is assumed to be '\\n'.
	
		**headerkeys** :  list of strings, optional
		
			Allowed header keys are strings in ['names', 'formats', 
			'types', 'coloring']. These keys indicate what special
			metadata is printed in the header.
			
	**See also:**  :func:`tabular.io.loadSV`, :func:`tabular.io.loadSVsafe`
	
	"""

	if delimiter is None:
		delimiter = inferdelimiter(fname)

	if linebreak is None:
		linebreak = '\n'

	headerdict = {}
	if 'names' in headerkeys:	
		headerdict['names'] = X.dtype.names
	if 'coloring' in headerkeys:
		headerdict['coloring'] = str(X.coloring)	#parsecoloring(X.coloring, X.dtype.names)
	if 'types' in headerkeys:
		headerdict['types'] = parsetypes(X.dtype)
	if 'formats' in headerkeys:
		headerdict['formats'] = parseformats(X.dtype)
	
	typevec = []
	ColStr = []
	UseComplex = False
	for name in X.dtype.names:
		typevec.append(X.dtype[name].name.strip('0123456789').rstrip('ing'))
		D = X[name]
		if D.ndim > 1:
			D = D.flatten()	
		if typevec[-1] == 'str':
			if sum([delimiter in d for d in D]) > 0:
				print "\nWARNING: An entry in the '" + name + "' column contains at least one instance of the delimiter '" + delimiter + "', and therefore will use Python csv module quoting convention (see online documentation for Python's csv module).  You may want to choose another delimiter not appearing in records, for performance reasons.\n"
				UseComplex = True
				break
			else:
				ColStr.append(D)
		else:
			ColStr.append(str(D.tolist()).strip('[]').split(', '))

	F = open(fname,'wb')

	for key in headerkeys:
		if key == 'coloring':
			F.write(comments + key + '=' + headerdict['coloring'] + linebreak)
		else:
			F.write(comments + key + '=' + delimiter.join(headerdict[key]) + linebreak)

	if UseComplex is True:
		csv.writer(F, delimiter=delimiter, lineterminator=linebreak).writerows(X)
	else:
		F.write(linebreak.join([delimiter.join([col[i] for col in ColStr]) for i in range(len(ColStr[0]))]))
	F.close()

def loadbinary(fname):
	"""
	Load a numpy binary file (``.npy``) or archive (``.npz``) created 
	by :func:`tabular.io.savebinary`. 
	
	The tabarray and, if present, rowdata and/or coloring, are all 
	loaded as numpy ndarrays and reconstituted properly, and 
	returned as [X, dtype, coloring, rowdata], where:
	
		**X** :  numpy ndarray with structured dtype
		
			The data, where each column is named and is of a uniform 
			NumPy data type.
		
		**dtype** : numpy dtype object
		
			The data type of *X*, e.g.::
			
				dtype = X.dtype
				
		**coloring** : dictionary, or None
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays.
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
			
		**rowdata** : numpy recarray, or None
		
			Structured per-row data; an attribute of tabarrays.
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about rowdata.
	
	The ``.npz`` file is a zipped archive created using
	:func:`numpy.savez` and containing one or more ``.npy`` files, 
	which are NumPy binary files created by :func:`numpy.save`. 
	
	**Parameters**
	
		**fname** :  string or file-like object
		
			FIle name or open file to a numpy binary file (``.npy``) or 
			archive (``.npz``) created by :func:`tabular.io.savebinary`.
		
			*	When *fname* is a ``.npy`` binary file, it is reconstituted 
				as a flat ndarray of data, with structured dtype.
		
			*	When *fname* is a ``.npz`` archive, it contains at least 
				one ``.npy`` binary file and optionally others:
			
				*	``data.npy`` must be in the archive, and is 
					reconstituted as a flat ndarray of data, with 
					structured dtype.
				
				*	``coloring.npy`` is reconstitued as a dictionary.
			
				*	``rowdata.npy`` is reconstituted as a numpy recarray 
					with structrued dtype. 
	
	**See also:**  :func:`tabular.io.savebinary`, :func:`numpy.load`, :func:`numpy.save`, :func:`numpy.savez`
	
	"""
	
	X = numpy.load(fname)
	if isinstance(X, numpy.lib.io.NpzFile):
		if 'coloring' in X.files:
			coloring = X['coloring'].tolist()
		else:
			coloring = None
		if 'rowdata' in X.files:
			rowdata = X['rowdata'].tolist()
			if not rowdata is None:
				rowdata = numpy.rec.fromrecords(rowdata, dtype=X['rowdata'].dtype)
		else:
			rowdata = None
		if 'data' in X.files:
			return [X['data'], X['data'].dtype, coloring, rowdata]
		else:
			return [None, None, coloring, rowdata]
	else:
		return [X, X.dtype, None, None]

def savebinary(fname, X, savecoloring=True, saverowdata=True):
	"""
	Save a tabarray to a numpy binary file (``.npy``) or archive 
	(``.npz``) that can be loaded by :func:`tabular.io.savebinary`. 

	The ``.npz`` file is a zipped archive created using
	:func:`numpy.savez` and containing one or more ``.npy`` files, 
	which are NumPy binary files created by :func:`numpy.save`. 
	
	**Parameters**
	
		**fname** :  string or file-like object
		
			FIle name or open file to a numpy binary file (``.npy``) or 
			archive (``.npz``) created by :func:`tabular.io.savebinary`.

		**X** :  tabarray
		
			The actual data in a :class:`tabular.tabarray.tabarray`:
			
			*	if *fname* is a ``.npy`` file, then this is the same as::
				
					numpy.savez(fname, data=X)
					
			*	otherwise, if *fname* is a ``.npz`` file, then *X* is zipped 
				inside of *fname* as ``data.npy``

		**savecoloring** : boolean
		
			Whether or not to save the :attr:`coloring` attribute of *X*. 
			If *savecoloring* is *True*, then *fname* must be a 
			``.npz`` archive and *X.coloring* is zipped inside of 
			*fname* as ``coloring.npy``
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
			
		**saverowdata** : boolean
		
			Whether or not to save the :attr:`rowdata` attribute of *X*. 
			If *saverowdata* is *True*, then *fname* must be a 
			``.npz`` archive and *X.rowdata* is zipped inside of 
			*fname* as ``rowdata.npy``
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about rowdata.
	
	**See also:**  :func:`tabular.io.loadbinary`, :func:`numpy.load`, :func:`numpy.save`, :func:`numpy.savez`
	
	"""
	
	if fname[-4:] == '.npy':
		numpy.save(fname, X)
	else:
		if (savecoloring is True) and (saverowdata is True):
			numpy.savez(fname, data=X, coloring=X.coloring, rowdata=X.rowdata)
		elif savecoloring is True:
			numpy.savez(fname, data=X, coloring=X.coloring)
		elif saverowdata is True:
			numpy.savez(fname, data=X, rowdata=X.rowdata)
		else:
			numpy.savez(fname, data=X)

def loadHSV(path, X=None, names=None, rootpath=None, rootheader=None, coloring=None, toload=None, Nrecs=None):
	"""
	Load a list of numpy arrays, corresponding to columns of data,  
	from a hierarchical separated variable (HSV) directory 
	(``.hsv``) created by :func:`tabular.io.saveHSV`.  
	
	This function is used by the tabarray constructor 
	:func:`tabular.tabarray.tabarray.__new__` when passed the 
	*HSV* argument.
	
	Each column of data inside of the ``.hsv`` directory is a 
	separate comma-separated variable text file (``.csv``), whose 
	name includes the column name and data type of the column 
	(e.g. ``name.int.csv``, ``name.float.csv``, ``name.str.csv``). An 
	ordered list of columns, if provided, is stored in a separate file, 
	``header.txt``.
	
	A ``.hsv`` directory can contain ``.hsv`` subdirectories. This 
	allows for hierarchical structure on the columns, which is 
	mapped to a coloring dictionary. For example, a subdirectory
	named ``color.hsv`` contains ``.csv`` files corrseponding to 
	columns of data grouped by that color.  Note that when the file 
	structure is not flat, :func:`tabular.io.loadHSV` calls itself 
	recursively.
	
	There may optionally also be rowdata stored in a file 
	'__rowdata__.pickle' in the top level directory. 
	
	Returns  [X, names, coloring, rowdata], where:
	
		**X** : list of numpy arrays, optional
		
			List of numpy arrays, corresponding to columns of data, 
			each loaded from one ``.csv`` file. 
			
		**names** :  list of strings, optional
		
			List of strings giving column names. 	
			
		**coloring** : dictionary, optional
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.

		**rowdata** : numpy recarray or None
		
			Structured per-row data; an attribute of tabarrays. If it 
			exists, the rowdata is reconstituted from a file called 
			'__rowdata__.pickle', which is the dump of a pickled 
			object in the top-level directory in *path* (which must be 
			a ``.hsv`` directory)
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about rowdata.
			
			**See also:**  :func:`tabular.io.loadrowdata`

	**Parameters**
	
		**path** :  string 

			Path to a ``.hsv`` directory or individual ``.csv`` text files, 
			corresponding to individual columns of data inside of a 
			``.hsv`` directory.
			
		**X** : list of numpy arrays, optional
		
			List of numpy arrays, corresponding to columns of data.  
			Typically, the *X* argument is only passed when  
			:func:`tabular.io.loadHSV` calls itself recursively, in which 
			case each element is a column of data that has already 
			been loaded.
			
		**names** :  list of strings, optional
		
			List of strings giving column names. Typically, the 
			*names* is only passed when :func:`tabular.io.loadHSV` 
			calls itself recursively, in which case each element gives 
			the name of the corresponding array in *X*.
			
		**rootpath** : string, optional
		
			Path to the top-level file (directory), i.e. the value of 
			*path* the first time :func:`tabular.io.loadHSV` is called. 
			Typically, the *rootpath* argument is only passed when  
			:func:`tabular.io.loadHSV` calls itself recursively.
			
		**rootheader** : list of strings, optional
			
			Ordered list of column names. Typically, the *rootheader* 
			argument is only passed when :func:`tabular.io.loadHSV` 
			calls itself recursively, in which case *rootheader* is 
			filled by parsing the (optional) ``header.txt`` file in 
			*rootpath*, if it exists.

		**coloring** : dictionary, optional
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. Typically, the 
			*coloring* argument is only passed when 
			:func:`tabular.io.loadHSV` calls itself recursively, in which 
			case it contains coloring, i.e. hierarchical structure 
			information, on the arrays in *X*. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
			
			**See also:** :func:`tabular.io.infercoloring`
			
		**toload** : list of strings, optional
		
			List of strings corresponding to a subset of column names 
			and/or color names; only these columns are loaded. 
		
			**See also:**  :func:`tabular.io.thresholdcoloring`
		
		**Nrecs** : non-negative integer
		
			The number of records in *X*. Typically, the *Nrecs* 
			argument is only passed when :func:`tabular.io.loadHSV` 
			calls itself recursively, in which case it is set by the first 
			``.csv`` file loaded.  Subsequent columns must have the 
			same number of records; when any subsequent column 
			disagrees, it is not loaded and a warning is issued.
			
	**See also:**  :func:`tabular.tabarray.tabarray.__new__`, :func:`tabular.io.saveHSV`
	
	"""
	
	if os.path.isdir(path):
		path = backslash(path)
	if X is None:
		X = []
	if names is None:
		names = []
	if rootpath is None:
		rootpath = path
	if rootheader is None:
		# If it exists, use the header.txt files to order attributes 
		# (this is not required) 
		rootheader = []
		if os.path.isdir(path):
			if 'header.txt' in os.listdir(path):
				rootheader =  open(path + 'header.txt', 'r').read().strip('\n').split('\n')
			else:
				H = [h for h in os.listdir(path) if h.endswith('header.txt')]
				if len(H)>0:
					rootheader =  open(path + H[0], 'r').read().strip('\n').split('\n')
	
	if os.path.isdir(path):
		L = [l for l in os.listdir(path) if l.endswith('.hsv') or l.endswith('.csv')]
		keys = path[len(rootpath):].split('.hsv/')[:-1]
	else:
		L = [path]
		keys = []
	
	CSVList = []
	
	for l in L:
		parsed_filename = l.split('.')
		name = '.'.join(parsed_filename[:-2]).split('/')[-1]
		if parsed_filename[-1] == 'csv' and (toload is None or name in toload):
			CSVList += [name]
			if name not in names:
				col = open(path + l if l != path else path, 'r').read().split('\n')	
				if Nrecs is None:
					Nrecs = len(col)
				if len(col) == Nrecs:
					try:
						type_data = eval(parsed_filename[-2])
						col = numpy.array([type_data(c) for c in col], parsed_filename[-2])
						if len(rootheader) > 0 and name in rootheader:
							indvec = [names.index(j) for j in rootheader[:rootheader.index(name)] if j in names]
							insert_ind = max(indvec) + 1 if len(indvec) > 0 else 0
							X.insert(insert_ind, col)
							names.insert(insert_ind, name)
						else:
							X += [col]
							names += [name]					
					except:
						print "Warning: the data in the .csv file ", path + l if l != path else path, " does not match the given data type, ", parsed_filename[-2], ", and was not loaded."
				else:
					print "Warning: the column" + path + (l if l != path else path) + " has " + str(len(col)) + " records, which does not agree with the number of records in first column loaded, '" + names[0] + "', which has " + str(Nrecs) + " records -- only the first column, as well as all the other columns which also have " + str(Nrecs) + " records, will be loaded."	
		elif parsed_filename[-1] == 'hsv' and os.path.isdir(path):
			colorname = '.'.join(parsed_filename[:-1]).split('/')[-1]
			if toload is None or not colorname in toload:
				[X, names, coloring, rowdata] = loadHSV(path + l, X=X, names=names, rootpath=rootpath, rootheader=rootheader, coloring=coloring, toload=toload, Nrecs=Nrecs)
			elif colorname in toload:
				[X, names, coloring, rowdata] = loadHSV(path + l, X=X, names=names, rootpath=rootpath, rootheader=rootheader, coloring=coloring, toload=None, Nrecs=Nrecs)
	
	rowdata = loadrowdata(path, len(X[0]))
	
	if (path == rootpath) & path.endswith('.hsv/'):
		coloring = infercoloring(path)
		if not toload is None:
			coloring = thresholdcoloring(coloring, names)

	return [X, names, coloring, rowdata]

def saveHSV(fname, X, printheaderfile=True):
	"""
	Save a tabarray to a hierarchical separated variable (HSV) 
	directory (``.hsv``).  The tabarray can later be loaded back 
	by passing *fname to the *HSV* argument of the tabarray 
	constructor :func:`tabular.tabarray.tabarray.__new__`.
	
	This function is used by the tabarray method
	:func:`tabular.tabarray.tabarray.saveHSV`.
	
	Each column of data in the tabarray is stored inside of the 
	``.hsv`` directory to a separate comma-separated variable text 
	file (``.csv``), whose name includes the column name and data 
	type of the column (e.g. ``name.int.csv``, ``name.float.csv``, 
	``name.str.csv``). 
	
	Coloring information, i.e.  hierarchical structure on the 
	columns, is stored in the file directory structure of the ``.hsv``, 
	where ``.hsv`` subdirectories correspond to colors in the 
	coloring dictionary::
	
		X.coloring.keys()
		
	e.g. a subdirectory named ``color.hsv`` contains ``.csv`` files 
	corrseponding to columns of data grouped by that color::
	
		X['color']
		
	See :func:`tabular.tabarray.tabarray.__new__` for more 
	information about coloring.
	
	Note that when the file structure is not flat, 
	:func:`tabular.io.loadHSV` calls itself recursively.
	
	There may optionally also be rowdata::
	
		X.rowdata != None
	
	which is stored in a file '__rowdata__.pickle' in the top level 
	directory.  See :func:`tabular.tabarray.tabarray.__new__` for 
	more information about rowdata.
	
	**Parameters**
	
		**fname** :  string 

			Path to a ``.hsv`` directory or individual ``.csv`` text files, 
			corresponding to individual columns of data inside of a 
			``.hsv`` directory.
			
		**X** :  tabarray
		
			The actual data in a :class:`tabular.tabarray.tabarray`.
			
		**printheaderfile** : boolean, optional
		
			Whether or not to print an ordered list of columns names 
			in an additional file ``header.txt`` in all ``.hsv`` directories.  
			The order is given by:: 
			
				X.dtype.names
		
			The ``header.txt`` file is used by :func:`tabular.io.loadHSV` 
			to load the columns of data in the proper order, but is not 
			required.
			
	**See also:**  :func:`tabular.tabarray.tabarray.__new__`, :func:`tabular.io.loadHSV`, :func:`tabular.io.savecolumns`
	
	"""	
	
	fname = backslash(fname)
	makedir(fname)

	keys = X.coloring.keys()
	pairwise = [[set(X.coloring[key1]) > set(X.coloring[key2]) for key1 in keys] for key2 in keys]
	names = list(X.dtype.names)
	
	for i in range(len(keys)):
		if sum(pairwise[i]) == 0:
			saveHSV(fname + keys[i] + '.hsv/', X[keys[i]], printheaderfile)
			names = [n for n in names if n not in X[keys[i]].dtype.names]

	savecolumns(fname, X[names])
			
	if (printheaderfile is True) and (X.dtype.names > 1):
		G = open(fname + 'header.txt', 'w')
		G.write('\n'.join(X.dtype.names))
		G.close()
		
	if not X.rowdata is None:
		G = open(fname + '__rowdata__.pickle','w')
		cPickle.dump(X.rowdata,G)
		G.close()

def savecolumns(fname, X):
	"""
	Save columns in tabarray *X* to an existing directory 
	*fname* (e.g. ``.hsv``).  
	
	Each column of data in the tabarray is stored inside of the 
	``.hsv`` directory to a separate comma-separated variable text 
	file (``.csv``), whose name includes the column name and data 
	type of the column (e.g. ``name.int.csv``, ``name.float.csv``, 
	``name.str.csv``). 
	
	Colorings and rowdata are lost. 
	
	This function is used by the tabarray method
	:func:`tabular.tabarray.tabarray.savecolumns`.
	
	**Parameters**
	
		**fname** :  string 

			Path to a hierarchical separated variable (HSV) directory
			(``.hsv``).
			
		**X** :  tabarray
		
			The actual data in a :class:`tabular.tabarray.tabarray`.		

	**See also:**  :func:`tabular.io.saveHSV`, :func:`tabular.io.loadHSVlist`
	
	"""
	
	fname = backslash(fname)
	names = X.dtype.names
	for name in names:
		typestr = X.dtype[name].name.strip('0123456789').rstrip('ing')
		F = open(fname + name + '.' + typestr + '.csv', 'w')
		D = X[name]
		if D.ndim > 1:
			D = D.flatten()	
		if typestr == 'str':
			F.write('\n'.join(D))
		else:
			F.write(str(D.tolist()).strip('[]').replace(', ','\n'))
		F.close()

def loadHSVlist(flist):
	"""
	Loads tabarrays from a list of  hierarchical separated variable 
	(HSV) paths, assuming they have disjoint columns and 
	identical numbers of rows;  then stacks them horizontally, e.g. 
	adding columns side-by-side, aligning the rows.
	
	Colorings can be lost, row data is lost. 
	
	**Parameters**
	
		**flist** :  list of strings 

			List of paths to hierarchical separated variable (HSV) 
			directories (``.hsv``) and/or individual ``.csv`` text files, 
			corresponding to individual columns of data inside of a 
			``.hsv`` directory.
	
	**See also:**  :func:`tabular.io.loadHSV`, :func:`tabular.io.savecolumns`
	
	"""
	
	X = tb.tabarray(HSV = flist[0])	
	for fname in flist[1:]:
		X = tb.shape_base.datahstack([X, tb.tabarray(HSV = fname)])
	return X

def appendHSV(fname, RecObj, order=None):
	"""
	Function for appending records to an on-disk tabarray, used 
	when one wants to write a large tabarray that is not going 
	to be kept in memory at once. 
	
	If the tabarray is not there already, the function intializes 
	the tabarray using the tabarray __new__ method, and saves 
	it out. 
	
	**Parameters**
	
		**fname** : string 
			
			Path of hierarchical separated variable (.hsv) file of which 
			to append.
	
		**RecObj** : array or dictionary  
		
		*	Either an array with complex dtype (e.g. tabarray, 
			recarray or ndarray), or 
		
		*	a dictionary (ndarray with structured dtype, e.g. a tabarray) where 
		
			*	keys are names of columns to append to, and
			*	the value on a column is a list of values to be 
				appended to that column.
	
		**order** : list of strings 
		
			List of column names specifying order in which the 
			columns should be written; only used when the HSV does 
			not exist and the header specifying order needs to be 
			written.
			
	**See also:** :func:`tabular.io.appendcolumns` 
	
	"""
	
	if hasattr(RecObj, 'dtype'):
		names = RecObj.dtype.names
	elif hasattr(RecObj, 'keys'):
		names = RecObj.keys()

	if order is None:
			order = names

	if hasattr(RecObj, 'coloring'):
		keys = RecObj.coloring.keys()
		pairwise = [[set(RecObj.coloring[key1]) > set(RecObj.coloring[key2]) for key1 in keys] for key2 in keys]
		names = list(RecObj.dtype.names)		
		for i in range(len(keys)):
			if sum(pairwise[i]) == 0:
				appendHSV(fname + keys[i] + '.hsv/', RecObj[keys[i]], order)
				names = [n for n in names if n not in RecObj[keys[i]].dtype.names]
			
	appendcolumns(fname, RecObj[names])
	
	printrowdata = None
	rowdata = loadrowdata(fname)
	if not rowdata is None:
	# append given rowdata or null-valued rowdata
		if hasattr(RecObj, 'rowdata'):
			if not RecObj.rowdata is None:
				rowdata = utils.SimpleStack1([rowdata, RecObj.rowdata])
			else:	
				newrowdata = numpy.rec.fromarrays([[tb.nullvalue(rowdata[l][0])]*len(RecObj[names[0]]) for l in rowdata.dtype.names], names=rowdata.dtype.names)
				rowdata = utils.SimpleStack1([rowdata,newrowdata])
		G = open(fname + '__rowdata__.pickle','w')
		cPickle.dump(rowdata,G)
		G.close()

def appendcolumns(fname, RecObj, order=None):
	"""
	Function for appending records to a flat on-disk tabarray, 
	(e.g. no colors, no rowdata), used when one wants to write a 
	large tabarray that is not going to be kept in memory at 
	once. 
	
	If the tabarray is not there already, the function intializes 
	the tabarray using the tabarray __new__ method, and saves 
	it out. 
	
	**Parameters**
	
		**fname** : string 
			
			Path of hierarchical separated variable (.hsv) file of which 
			to append.
	
		**RecObj** : array or dictionary  
		
		*	Either an array with complex dtype (e.g. tabarray, 
			recarray or ndarray), or 
		
		*	a dictionary (ndarray with structured dtype, e.g. a tabarray) where 
		
			*	keys are names of columns to append to, and
			*	the value on a column is a list of values to be 
				appended to that column.
	
		**order** : list of strings 
		
			List of column names specifying order in which the 
			columns should be written; only used when the HSV does 
			not exist and the header specifying order needs to be 
			written.

	See :func:`tabular.io.appendHSV` for a more general method.
	
	"""
	
	if hasattr(RecObj, 'dtype'):
		names = RecObj.dtype.names
	elif hasattr(RecObj, 'keys'):
		names = RecObj.keys()

	if order is None:
			order = names
	
	Cols = [RecObj[o] for o in order]
	assert all([len(Cols[0]) == len(a) for a in Cols]), "In" + funcname() + ": There are differing numbers of elements in the columns, no records appended."

	if not os.path.exists(fname):
		assert set(names) == set(order), "The names and the order argument conflict."
		tb.tabarray.harray(Columns = Cols, names = order).save(fname)
	elif len(Cols[0]) > 0:
		headerfilename = [l for l in os.listdir(fname) if l.endswith('header.txt')][0]
		header = open(fname + headerfilename,'r').read().split('\n')
		#assert set(header) == set(names), "The header file and names conflict; either some names don't exist in the header or some headers don't exist in the name list."
		for h in header:
			name = [fname + l for l in os.listdir(fname) if l.startswith(h) and l.endswith('.csv')]
			if len(name) > 0:
				name = name[0]
				dtype = name.split('.')[-2]
				if dtype == 'str':
					F = open(name,'a')
					F.write('\n' + '\n'.join(RecObj[h]))
					F.close()
				else:
					F = open(name,'a')
					F.write('\n' + str(numpy.array(RecObj[h]).tolist()).strip('[]').replace(', ','\n'))
					F.close()				
	else: pass

def loadrowdata(fname, nrecords=None):
	"""
	Load pickled rowdata from *fname*, e.g. a hierarchical 
	separated variable (HSV) directory (``.hsv``) created by a 
	function like :func:`tabular.io.saveHSV`. 
	
	If there is no pickled rowdata, i.e. there is no file 
	'__rowdata.pickle' inside of *fname*, or the number of 
	records in the rowdata disagrees with that of the HSV, 
	*nrecords*.
	
	Returns rowdata, expected to be a numpy recarray or *None*. 
	
	This function is used by :func:`tabular.io.loadHSV` to load rowdata, which is later attached to the tabarray loaded from the HSV as the :attr:`rowdata` attribute. 
	
	**Parameters**
	
		**fname** :  string
		
			Path of HSV directory (``.hsv``)
		
		**nrecords** :  integer, optional
		
			Number of records (rows) in the HSV. 
		
	**See also:**  :func:`tabular.io.loadHSV`
	
	"""
	
	if os.path.isdir(fname):
		if '__rowdata__.pickle' in os.listdir(fname):
			try:
				rowdata = cPickle.load(open(backslash(fname) + '__rowdata__.pickle','r'))
				if not nrecords is None:
					if len(rowdata) != nrecords:
						rowdata = None
			except:
				rowdata = None
		else:
			rowdata = None
	else:
		rowdata = None
	return rowdata

def is_string_like(obj):
    """
    Check whether obj behaves like a string.
    From:  _is_string_like in numpy.lib._iotools
    
    **Parameters**
    
    	**obj** : string or file object
    
    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

def typeinfer(column):
	"""
	Take a list of strings, and attempts to infer a numeric datatype 
	that fits them all.  
	
	If the strings are all integers, returns a NumPy array of 
	integers.
	
	If the strings are all floats, returns a NumPy array of floats.
	
	Otherwise, returns a NumPy array of the original list of strings.

	Used to determine the datatype of a column read from a 
	separated-variable (SV) text file (e.g. ``.tsv``, ``.csv``) of data 
	where columns are expected to be of uniform Python type.
	
	This function is used by tabular load functions for SV files, e.g. 
	by :func`tabular.io.loadSV` when type information is not 
	provided in the header, and by :func:`tabular.io.loadSVsafe`.
	
	**Parameters**
	
		**column** : list of strings
		
			List of strings corresponding to a column of data.
	
	"""
	try:
		return numpy.array([int(x) for x in column], 'int')
	except:
		try:
			return numpy.array([float(x) if x != '' else numpy.nan for x in column], 'float')
		except:
			return numpy.array(column, 'str')
			
def infercoloring(path, rootpath = None, coloring = None):
	"""
	Infer the coloring of a tabarray saved as a hierarchical 
	separated variable ('.hsv') directory by looking at file directory 
	substructure. 
	
	Used by loadHSV() because when 'toload' is not None, the 
	complete coloring must be known to threshold it properly. 
	
	"""

	path = backslash(path)	
	if rootpath is None:
		rootpath = path
	if coloring is None:
		coloring = {}
	L = [l for l in os.listdir(path) if l.endswith('.hsv') or l.endswith('.csv')]
	
	tabarray = [L[i] for i in xrange(len(L)) if L[i].split('.')[-1] == 'hsv']
	for dd in tabarray:
		coloring = infercoloring(path+dd, rootpath, coloring)
	
	if path !=	rootpath:
		DotCSV = [L[i] for i in xrange(len(L)) if L[i].split('.')[-1] == 'csv']
		names = [DotCSV[i].split('.')[:-2][0] for i in xrange(len(DotCSV))]
		keysfrompath = path[len(rootpath):].strip('.hsv/').split('.hsv/')			
		for key in keysfrompath:
			if key in coloring.keys():
				coloring[key] = coloring[key] + names
			else:
				coloring[key] = names
				
	return coloring

def inferdelimiter(fname):
	""" 
	Infer delimiter from file extension.
	
		*	If *fname* ends with '.tsv', return '\\t'.
		
		*	If *fname* ends with '.csv', return ','.
		
		*	Otherwise, return '\\t'.
	
	**Parameters**
	
		**fname** : string
		
			File path assumed to be for a separated-variable file.
	
	"""
	if fname.endswith('.tsv'):
		return '\t'
	elif fname.endswith('.csv'):
		return ','
	else:
		return '\t'

def parseformats(dtype):
	""" 
	Return list of string representations of formats from a dtype 
	object. 
	
	Used by :func:`tabular.io.saveSV` to write out format
	information in the header. 
	
	**Parameters**
	
		**dtype** : NumPy dtype object
	
	"""
	return [dtype[i].descr[0][1] for i in range(len(dtype))]

def parsetypes(dtype):
	""" 
	Return list of string representations of types from a dtype 
	object, e.g. ['int', 'float', 'str']. 
	
	Used by :func:`tabular.io.saveSV` to write out type
	information in the header. 
	
	**Parameters**
	
		**dtype** : NumPy dtype object
	
	"""
	return [dtype[i].name.strip('1234567890').rstrip('ing') for i in range(len(dtype))]
	
def parsecoloring(coloring, names):
	""" 
	Return list of string representations of colors.
	
	Used by :func:`tabular.io.saveSV` to write out coloring 
	information in the header. 
	
	**Parameters**
	
		**coloring** : dictionary
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
	
		**names** :  list of strings
		
			List of strings giving column names. 
	
	"""
	d = utils.DictInvert1(coloring)
	return [','.join(d[n]) if n in d.keys() else '' for n in names]
	
def thresholdcoloring(coloring, names):
	""" 
	Threshold *coloring* based on *names*, a list of strings in::
	
		coloring.values()	
	
	**Parameters**

		**coloring** : dictionary
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
	
		**names** :  list of strings
		
			List of strings giving column names. 
	
	"""
	for key in coloring.keys():
		if coloring[key] != [k for k in coloring[key] if k in names]:
			coloring.pop(key)
		elif set(coloring[key]) == set(names):
			coloring.pop(key)
	return coloring
	
def backslash(Dir,Verbose=False):
	'''
	Adds '/' to end of a path (meant to make formatting of directory 
	Paths consistently have the slash)
	'''

	if Dir[-1] != '/':
		if Verbose:
			print "Warning: the directory name, ", Dir, ", was provided. The character '/' was appended to the end of the name."
		return Dir + '/'
	else:
		return Dir

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