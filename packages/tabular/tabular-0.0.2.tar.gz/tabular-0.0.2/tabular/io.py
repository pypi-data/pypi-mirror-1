"""
Functions for :class:`tabular.tabarray.tabarray` i/o methods, 
including to/from separated-value (e.g. ``.tsv``, ``.csv``) and other 
text files, binary files, hierarchical separated-value (HSV) format.
"""

__all__ = ['loadSV', 'saveSV', 'loadbinary', 'savebinary', 'loadHSV', 'saveHSV', 'savecolumns', 'loadHSVlist', 'appendHSV', 'appendcolumns', 'typeinfer', 'inferdelimiter']

import numpy, types, csv, cPickle, os, shutil
from numpy import int64
import tabular as tb
from tabular import utils as utils

def loadSV(fname, comments='#', delimiter='\t', delimiter_regex=None, linebreak='\n', skiprows=0, usecols=None, toload=None, metadatadict=None, namesinheader=True, headerlines=None, valuefixer=None, linefixer=None, returnasrecords=False):
	"""
	Load a separated value text file. 
	
	Takes a tabular text file with a specified delimeter and end-
	of-line character, and return data as a Python list of either
	numpy arrays corresponding to columns, each a uniform 
	Python type (int, float, str), or Python lists corresponding to
	records (rows).  If given in the text file, also returns column 
	names and hierarchical column-oriented structure (coloring).

	**Parameters**

		**fname** :  string or file object

			Path (or file object) corresponding to a separated variable 
			(SV) text file. 
		
		**comments** :  string, optional
			
			The string denoting the start of a comment, e.g. '#'.  Note 
			that the default is '#'.  Lines at the top of the file 
			beginning with `comments` are assumed to be the header
			of the file where metadata can be found (e.g. column 
			names).  
		
		**delimiter** :  string, optional
		
			The string that separates values in each line of text, e.g. 
			'\\t'.  By default, this is inferred from the file extension:
			
				*	if the file ends in `.tsv`, the delimiter is '\\t'
				*	if the file ends in `.csv`, the delimiter is ','
		
			If the delimiter cannot be inferred and is not given, it is
			assumed to be '\\t'.  Note that this is different from the 
			default for `numpy.loadtxt <http://docs.scipy.org/doc/numpy/reference/generated/numpy.loadtxt.html>`_, 
			which is any whitespace. 
			
			**See Also:**  :func:`tabular.io.inferdelimiter`

		**delimiter_regex** :  reguiar expression, optional
		
			Regular expression decribing the delimiter.
		
		**linebreak** :  string, optional
		
			The string separating lines of text, e.g. '\\n'.  By default, 
			this is assumed to be '\\n'. Note that the file is opened 
			using the "read universal" option::
			
				file(fname, 'rU')
		
		**skiprows** :  non-negative integer, optional
		
			The first `skiprows` lines are ignored. 
		
		**usecols** :  sequence of non-negative integers, optional
		
			If `usecols` is not `None`, only the columns it lists are
			loaded, with 0 being the first column.

		**toload** :  list of strings, optional
		
			List of strings corresponding to a subset of column 
			names; only these columns are loaded. 	

		**metadatadict**:  dictionary, optional
		
			Dictionary mapping one or more special keys in 
			['names', 'formats', 'types', 'coloring'] each to a line 
			number corresponding to a row in the header (Python
			style, starting with 0 rather than 1).  The line number 
			is equal to the actual line number in the file (starting 
			at 0) minus `skiprows`.  Negative line numbers 
			allowed, and are counted from the end of the header.
		
			If `None`, look for a string representation of 
			`metadatadict` in the header, this is a line beginning 
			with "metadatadict=".  The default settings of 
			:func:`tabular.io.saveSV` result in writing out this line 
			in the 
			
		**namesinheader**:  Boolean, optional
		
			If `namesinheader == True` and `metadatadict == None`, 
			then assume metadatadict = {'names': headerlines-1}, 
			e.g. the column names are in the last header line.  
			
		**headerlines** :  integer, optional
		
			The number of lines at the top of the file (after the
			first `skiprows` lines) corresponding to the header
			of the file, where metadata can be found (e.g. 
			column names).  
		
			If `comments == ''` and there are header lines in the 
			file, then it might not necessarily be possible to 
			automatically parse the header from the data. 
			
			If `comments == ''` and `headerlines == None`
			and `metadatadict != None`, then::
			
				headerlines = max(metadatadict.values())
				
			For this to be well-defined, we must have::
			
				all(metadatadict.values() > 0)
				
			If `comments == ''` and `headerlines == None`
			and `metadatadict == None` and 
			`namesinheader == True` then it is assumed that
			the column names are in the first line of the file
			after the first `skiprows` lines.  This is equivalent
			to setting `comments = None`, `headerlines = 1`,
			`metadatadict = {'names': 0}`. 
	
		**valuefixer** :  lambda function 
		
			Lambda function to apply to all values in the SV.
	
		**linefixer** :  lambda function
		
			Lambda function to apply to every line in the SV.
			
		**returnasrecords** :  boolean, optional
		
			If `True`, return a list of parsed records.  Otherwise,
			return a list of parsed columns.  Default is `False`.

	**Returns**	
		
		**columns** :  list of one-dimensional numpy arrays 
		
			List of typed numpy arrays corresponding to columns 
			of data, each a uniform NumPy data type.
			
			Returned if `returnasrecords = False` (default).

		**records** :  list of lists
		
			List of lists corresponding to records (rows) of data.
			Only returned if `returnasrecords = True`.
			
		**names** :  list of strings, or `None`
			
			List of column names given in the header of the file 
			(optional). 
			
		**coloring** :  dictionary, or `None`
		
			Hierarchical column-oriented structure. Each key is a 
			string naming a color whose corresponding value is a 
			list of column names (strings) in that color.
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about `coloring`.
	
	**See Also:**  
	
		:func:`tabular.io.saveSV`, :func:`tabular.io.typeinfer`

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
	
	if headerlines is None:	
		if comments != '':		# file header = lines at the top beginning with comments
			headerlines = 0
			for ind in range(len(F)):			
				line = F[ind]
				line = delimiter.join(list(csv.reader([line], delimiter=delimiter))[0])
				F[ind] = line
				
				if line[:len(comments)] == comments:
					headerlines += 1
				else:
					break
		else:
			if F[0].startswith(comments + 'metadatadict='):
				metadatadict = eval(F[0].split(comments + 'metadatadict=')[-1])
				if len(metadatadict.keys()) > 0:
					headerlines = max(metadatadict.values())				
			else:
				if namesinheader is True:	# if there is no comments character and there are column names in the header
					headerlines = 1				# assume there is one header line containing the column names
				else:
					headerlines = 0					
	
	# headerdata = file header, may contain structured metadata, chop off comments character(s)
	headerdata = [line[len(comments):] for line in F[:headerlines]]
	F = F[headerlines:]
	
	if metadatadict is None:
		metadatadict = [eval(line.split('metadatadict=')[-1]) for line in headerdata if line.startswith('metadatadict=')]
		if len(metadatadict) == 1:
			metadatadict = metadatadict[0]
		else:
			if namesinheader is True:
				metadatadict = {'names': headerlines-1}
			else:
				metadatadict = {}

	metadata = {}
	for key in metadatadict.keys():
		line = headerdata[metadatadict[key]]
		if key == 'coloring':
			metadata[key] = line
		elif key in ['names', 'formats', 'types']:
			metadata[key] = list(csv.reader([line], delimiter=delimiter))[0]

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
	
	# Restrict the columns to the subset requested by the user
	if not toload is None:		
		usecols = list(set(utils.ListUnion([[names.index(TL)] if TL in names else [names.index(c) for c in coloring[TL]] for TL in toload])))
		usecols.sort()

	# parse data F on the delimiter
	F = list(csv.reader(F, delimiter=delimiter))

	if usecols is None:
	 	if not toload is None:
		 	usecols = [names.index(TL) for TL in toload]
		 	usecols.sort()
		elif not names is None:
			usecols = range(len(names))
		else:
			usecols = range(len(F[0]))

	if not names is None:
		names = [names[i] for i in usecols]
	if not coloring is None:
		coloring = thresholdcoloring(coloring, names)	

	if returnasrecords:
		F = [[record[column] for column in usecols] for record in F]
		return [F, names, coloring]

	if not names is None:
		for r in F:
			assert len( r ) >= len( names )
	
	# Type the columns and save to a list of (attribute) columns, each a numpy array
	if valuefixer is None:
		if not formats is None:
			columns = [numpy.array([record[column] for record in F], formats[column]) for column in usecols]
		else:
			columns = [typeinfer([record[column] for record in F]) for column in usecols]
	else:
		if not formats is None:
			columns = [numpy.array([valuefixer( record[column] ) for record in F], formats[column]) for column in usecols]
		else:
			columns = [typeinfer([valuefixer( record[column] ) for record in F]) for column in usecols]
	
	return [columns, names, coloring]


def saveSV(fname, X, comments='#', delimiter=None, linebreak=None, metadatakeys=['coloring','types','names'], printmetadatadict=True, strongmetadata=False):
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
	
		**metadatakeys** :  list of strings, optional
		
			Allowed header keys are strings in ['names', 'formats', 
			'types', 'coloring']. These keys indicate what special
			metadata is printed in the header.
			
			Default value is ['coloring', 'types', 'names']. 
			
		**printmetadatadict** :  Boolean, optional
		
			Whether or not to print a string representation of the
			`metadatadict` in the first line of the header. 
			
			See the :func:`tabular.io.loadSV` for more information 
			about `metadatadict`.
			
		**strongmetadata** :  Boolean, optional
		
			Whether or not to drop "blank" metadata, e.g. if
			`strongmetadata` is False and `X.coloring == {}`
			then do not print metadata in the header for the
			coloring.  This is also reflected in the the
			`metadatadict` if `printmetadatadict == True`. 
			
	**See Also:**  
	
		:func:`tabular.io.loadSV`
		
	"""

	if delimiter is None:
		delimiter = inferdelimiter(fname)

	if linebreak is None:
		linebreak = '\n'

	metadata = {}
	if 'names' in metadatakeys:	
		metadata['names'] = X.dtype.names
	if 'coloring' in metadatakeys:
		if strongmetadata is False and X.coloring == {}:
			metadatakeys = [key for key in metadatakeys if key != 'coloring']
		else:
			metadata['coloring'] = str(X.coloring)	
	if 'types' in metadatakeys:
		metadata['types'] = parsetypes(X.dtype)
	if 'formats' in metadatakeys:
		metadata['formats'] = parseformats(X.dtype)
	
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
	
	if printmetadatadict is True:
		metadatadict = dict( zip( metadatakeys, range(1, 1+len(metadata.keys())) ) )
		line = "metadatadict=" + metadatadict.__repr__()
		if delimiter in line:
			csv.writer(F, delimiter=delimiter, lineterminator=linebreak).writerow([comments + line])
		else:
			F.write(comments + line + linebreak)

	for key in metadatakeys:
		if key == 'coloring':
			if delimiter in metadata['coloring']:
				csv.writer(F, delimiter=delimiter, lineterminator=linebreak).writerow([comments + metadata['coloring']])
			else:
				F.write(comments + metadata['coloring'] + linebreak)
		else:
			F.write(comments + delimiter.join(metadata[key]) + linebreak)

	if UseComplex is True:
		csv.writer(F, delimiter=delimiter, lineterminator=linebreak).writerows(X)
	else:
		F.write(linebreak.join([delimiter.join([col[i] for col in ColStr]) for i in range(len(ColStr[0]))]))
	F.close()

def loadbinary(fname):
	"""
	Load a numpy binary file (``.npy``) or archive (``.npz``) created by :func:`tabular.io.savebinary`. 
	
	The data and associated data type (e.g. `dtype`, including if 
	given, column names) are loaded and reconstituted.  
	
	If `fname` is a numpy archive, it may contain additional data 
	giving hierarchical column-oriented structure (e.g. `coloring`). 
	See :func:`tabular.tabarray.tabarray.__new__` for more information about coloring.
	
	The ``.npz`` file is a zipped archive created using
	:func:`numpy.savez` and containing one or more ``.npy`` files, 
	which are NumPy binary files created by :func:`numpy.save`. 
	
	**Parameters**
	
		**fname** :  string or file-like object
		
			FIle name or open file to a numpy binary file (``.npy``) or 
			archive (``.npz``) created by :func:`tabular.io.savebinary`.
		
			*	When `fname` is a ``.npy`` binary file, it is reconstituted 
				as a flat ndarray of data, with structured dtype.
		
			*	When `fname` is a ``.npz`` archive, it contains at least 
				one ``.npy`` binary file and optionally another:
			
				*	``data.npy`` must be in the archive, and is 
					reconstituted as `X`, a flat ndarray of data, with 
					structured dtype, `dtype`.
				
				*	``coloring.npy``, if present is reconstitued as 
					`coloring`, a dictionary.

	**Returns**
	
		**X** :  numpy ndarray with structured dtype
		
			The data, where each column is named and is of a 
			uniform NumPy data type.
		
		**dtype** :  numpy dtype object
		
			The data type of `X`, e.g. `X.dtype`.
				
		**coloring** :  dictionary, or None
		
			Hierarchical structure on the columns given in the 
			header of the file; an attribute of tabarrays.
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
	
	**See Also:**  
	
		:func:`tabular.io.savebinary`, :func:`numpy.load`, :func:`numpy.save`, :func:`numpy.savez`
	
	"""
	
	X = numpy.load(fname)
	if isinstance(X, numpy.lib.io.NpzFile):
		if 'coloring' in X.files:
			coloring = X['coloring'].tolist()
		else:
			coloring = None
		if 'data' in X.files:
			return [X['data'], X['data'].dtype, coloring]
		else:
			return [None, None, coloring]
	else:
		return [X, X.dtype, None]

def savebinary(fname, X, savecoloring=True):
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
			
			*	if `fname` is a ``.npy`` file, then this is the same as::
				
					numpy.savez(fname, data=X)
					
			*	otherwise, if `fname` is a ``.npz`` file, then `X` is zipped 
				inside of `fname` as ``data.npy``

		**savecoloring** : boolean
		
			Whether or not to save the `coloring` attribute of `X`. 
			If `savecoloring` is `True`, then `fname` must be a 
			``.npz`` archive and `X.coloring` is zipped inside of 
			`fname` as ``coloring.npy``
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
	
	**See Also:**  
	
		:func:`tabular.io.loadbinary`, :func:`numpy.load`, :func:`numpy.save`, :func:`numpy.savez`
	
	"""
	
	if fname[-4:] == '.npy':
		numpy.save(fname, X)
	else:
		if savecoloring is True:
			numpy.savez(fname, data=X, coloring=X.coloring)
		else:
			numpy.savez(fname, data=X)

def loadHSV(path, X=None, names=None, rootpath=None, rootheader=None, coloring=None, toload=None, Nrecs=None):
	"""
	Load a list of numpy arrays, corresponding to columns of data,  
	from a hierarchical separated variable (HSV) directory 
	(``.hsv``) created by :func:`tabular.io.saveHSV`.  
	
	This function is used by the tabarray constructor 
	:func:`tabular.tabarray.tabarray.__new__` when passed the 
	`HSV` argument.
	
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

	**Parameters**
	
		**path** :  string 

			Path to a ``.hsv`` directory or individual ``.csv`` text files, 
			corresponding to individual columns of data inside of a 
			``.hsv`` directory.
			
		**X** :  list of numpy arrays, optional
		
			List of numpy arrays, corresponding to columns of data.  
			Typically, the `X` argument is only passed when  
			:func:`tabular.io.loadHSV` calls itself recursively, in which 
			case each element is a column of data that has already 
			been loaded.
			
		**names** :  list of strings, optional
		
			List of strings giving column names. Typically, the 
			`names` is only passed when :func:`tabular.io.loadHSV` 
			calls itself recursively, in which case each element gives 
			the name of the corresponding array in `X`.
			
		**rootpath** :  string, optional
		
			Path to the top-level file (directory), i.e. the value of 
			`path` the first time :func:`tabular.io.loadHSV` is called. 
			Typically, the `rootpath` argument is only passed when  
			:func:`tabular.io.loadHSV` calls itself recursively.
			
		**rootheader** :  list of strings, optional
			
			Ordered list of column names. Typically, the `rootheader` 
			argument is only passed when :func:`tabular.io.loadHSV` 
			calls itself recursively, in which case `rootheader` is 
			filled by parsing the (optional) ``header.txt`` file in 
			`rootpath`, if it exists.

		**coloring** :  dictionary, optional
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			Typically, the `coloring` argument is only passed when 
			:func:`tabular.io.loadHSV` calls itself recursively, in which 
			case it contains coloring, i.e. hierarchical structure 
			information, on the arrays in `X`. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
			
			**See Also:** :func:`tabular.io.infercoloring`
			
		**toload** :  list of strings, optional
		
			List of strings corresponding to a subset of column names 
			and/or color names; only these columns are loaded. 
		
			**See Also:**  :func:`tabular.io.thresholdcoloring`
		
		**Nrecs** :  non-negative integer
		
			The number of records in `X`. Typically, the `Nrecs` 
			argument is only passed when :func:`tabular.io.loadHSV` 
			calls itself recursively, in which case it is set by the first 
			``.csv`` file loaded.  Subsequent columns must have the 
			same number of records; when any subsequent column 
			disagrees, it is not loaded and a warning is issued.
		
	**Returns**

		**X** :  list of numpy arrays
		
			List of numpy arrays, corresponding to columns of data, 
			each loaded from one ``.csv`` file. 
			
		**names** :  list of strings
		
			List of strings giving column names. 	
			
		**coloring** :  dictionary
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
	
	**See Also:**  
	
		:func:`tabular.tabarray.tabarray.__new__`, :func:`tabular.io.saveHSV`
	
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
				[X, names, coloring] = loadHSV(path + l, X=X, names=names, rootpath=rootpath, rootheader=rootheader, coloring=coloring, toload=toload, Nrecs=Nrecs)
			elif colorname in toload:
				[X, names, coloring] = loadHSV(path + l, X=X, names=names, rootpath=rootpath, rootheader=rootheader, coloring=coloring, toload=None, Nrecs=Nrecs)
		
	if (path == rootpath) & path.endswith('.hsv/'):
		coloring = infercoloring(path)
		if not toload is None:
			coloring = thresholdcoloring(coloring, names)

	return [X, names, coloring]

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
			
	**See Also:**  
	
		:func:`tabular.tabarray.tabarray.__new__`, :func:`tabular.io.loadHSV`, :func:`tabular.io.savecolumns`
	
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
		

def savecolumns(fname, X):
	"""
	Save columns of a tabarray to an existing HSV directory.
	
	Save columns of tabarray `X` to an existing HSV directory
	`fname` (e.g. a ``.hsv`` directory created by :func:`tabular.io.saveHSV`).
	
	Each column of data in the tabarray is stored inside of the 
	``.hsv`` directory to a separate comma-separated variable text 
	file (``.csv``), whose name includes the column name and data 
	type of the column (e.g. ``name.int.csv``, ``name.float.csv``, 
	``name.str.csv``). 
	
	Coloring is lost. 
	
	This function is used by the tabarray method
	:func:`tabular.tabarray.tabarray.savecolumns`.
	
	**Parameters**
	
		**fname** :  string 

			Path to a hierarchical separated variable (HSV) directory
			(``.hsv``).
			
		**X** :  tabarray
		
			The actual data in a :class:`tabular.tabarray.tabarray`.		

	**See Also:**  
	
		:func:`tabular.io.saveHSV`, :func:`tabular.io.loadHSVlist`
	
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
	
	**See Also:**  
	
		:func:`tabular.io.loadHSV`, :func:`tabular.io.savecolumns`
	
	"""
	
	X = tb.tabarray(HSVfile = flist[0])	
	for fname in flist[1:]:
		Y = tb.tabarray(HSVfile = fname)
		X = X.colstack(Y)
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
	
		**fname** :  string 
			
			Path of hierarchical separated variable (``.hsv``) file to 
			which to append records in `RecObj`.
	
		**RecObj** :  array or dictionary  
		
		*	Either an array with complex dtype (e.g. tabarray, 
			recarray or ndarray), or 
		
		*	a dictionary (ndarray with structured dtype, e.g. a tabarray) where 
		
			*	keys are names of columns to append to, and
			*	the value on a column is a list of values to be 
				appended to that column.
	
		**order** :  list of strings 
		
			List of column names specifying order in which the 
			columns should be written; only used when the HSV does 
			not exist and the header specifying order needs to be 
			written.
			
	**See Also:** 
	
		:func:`tabular.io.appendcolumns` 
	
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
	
	
def appendcolumns(fname, RecObj, order=None):
	"""
	Function for appending records to a flat on-disk tabarray, 
	(e.g. no colors), used when one wants to write a large 
	tabarray that is not going to be kept in memory at once. 
	
	If the tabarray is not there already, the function intializes 
	the tabarray using the tabarray __new__ method, and saves 
	it out. 
	
	See :func:`tabular.io.appendHSV` for a more general method.
	
	**Parameters**
	
		**fname** :  string 
			
			Path of hierarchical separated variable (.hsv) file of which 
			to append.
	
		**RecObj** :  array or dictionary  
		
		*	Either an array with complex dtype (e.g. tabarray, 
			recarray or ndarray), or 
		
		*	a dictionary (ndarray with structured dtype, e.g. a tabarray) where 
		
			*	keys are names of columns to append to, and
			*	the value on a column is a list of values to be 
				appended to that column.
	
		**order** :  list of strings 
		
			List of column names specifying order in which the 
			columns should be written; only used when the HSV does 
			not exist and the header specifying order needs to be 
			written.

	**See Also:**
	
		:func:`tabular.io.appendHSV`
	
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

def is_string_like(obj):
    """
    Check whether input object behaves like a string.
    
    From:  _is_string_like in numpy.lib._iotools
    
    **Parameters**
    
    	**obj** :  string or file object
    	
    		Input object to check.
    	
    **Returns**
    
    	**out** :  bool
    	
    		Whether or not `obj` behaves like a string.
    
    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True

def typeinfer(column):
	"""
	Infer the data type (int, float, str) of a list of strings.
	
	Take a list of strings, and attempts to infer a numeric 
	data type that fits them all.  
	
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
	
		**column** :  list of strings
		
			List of strings corresponding to a column of data.
			
	**Returns**
	
		**out** :  numpy array
		
			Numpy array of data from `column`, with data type
			int, float or str.
				
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
	Infer the coloring from the file structure of a HSV directory. 
	
	Infer the coloring of a tabarray saved as a hierarchical 
	separated variable ('.hsv') directory by looking at file directory 
	substructure.  Note that when the file structure is not flat, 
	:func:`tabular.io.infercoloring` calls itself recursively.
	
	Used by loadHSV() because when 'toload' is not None, the 
	complete coloring must be known to threshold it properly. 
	
	**Parameters**
	
		**path** :  string 

			Path to a ``.hsv`` directory or individual ``.csv`` text files, 
			corresponding to individual columns of data inside of a 
			``.hsv`` directory.

		**rootpath** :  string, optional
		
			Path to the top-level file (directory), i.e. the value of 
			`path` the first time :func:`tabular.io.loadHSV` is called. 
			Typically, the `rootpath` argument is only passed when  
			:func:`tabular.io.infercoloring` calls itself recursively.

		**coloring** :  dictionary, optional
		
			Hierarchical structure on the columns.  See below.
	
	**Returns**
	
		**coloring** :  dictionary
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			Typically, the `coloring` argument is only passed when 
			:func:`tabular.io.loadHSV` calls itself recursively, in which 
			case it contains coloring, i.e. hierarchical structure 
			information, on the arrays in `X`. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
			
	**See Also:** 
	
		:func:`tabular.io.loadHSV`
	
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
				coloring[key] = utils.uniqify(coloring[key] + names)
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
	
		**fname** :  string
		
			File path assumed to be for a separated-variable file.
			
	**Returns**
	
		**delimiter** :  string
		
			String in ['\\t', ','], the inferred delimiter. 
	
	"""
	if fname.endswith('.tsv'):
		return '\t'
	elif fname.endswith('.csv'):
		return ','
	else:
		return '\t'

def parseformats(dtype):
	""" 
	Parse the formats from a structured numpy dtype object.
	
	Return list of string representations of numpy formats 
	from a structured numpy dtype object. 
	
	Used by :func:`tabular.io.saveSV` to write out format
	information in the header. 
	
	**Parameters**
	
		**dtype** :  numpy dtype object
		
			Structured numpy dtype object to parse. 

	**Returns**
	
		**out** :  list of strings
		
			List of strings corresponding to numpy formats::
			
				[dtype[i].descr[0][1] for i in range(len(dtype))]
	
	"""
	return [dtype[i].descr[0][1] for i in range(len(dtype))]

def parsetypes(dtype):
	""" 
	Parse the types from a structured numpy dtype object.
	
	Return list of string representations of types from a 
	structured numpy dtype object, e.g. ['int', 'float', 'str']. 
	
	Used by :func:`tabular.io.saveSV` to write out type
	information in the header. 
	
	**Parameters**
	
		**dtype** :  numpy dtype object
		
			Structured numpy dtype object to parse. 

	**Returns**
	
		**out** :  list of strings
		
			List of strings corresponding to numpy types::
			
				[dtype[i].name.strip('1234567890').rstrip('ing') for i in range(len(dtype))]
	
	"""
	return [dtype[i].name.strip('1234567890').rstrip('ing') for i in range(len(dtype))]
	
def thresholdcoloring(coloring, names):
	""" 
	Threshold a coloring dictionary for a given list of column names.
	
	Threshold `coloring` based on `names`, a list of strings in::
	
		coloring.values()	
	
	**Parameters**

		**coloring** :  dictionary
		
			Hierarchical structure on the columns given in the header 
			of the file; an attribute of tabarrays. 
			
			See :func:`tabular.tabarray.tabarray.__new__` for more 
			information about coloring.
	
		**names** :  list of strings
		
			List of strings giving column names. 
			
	**Returns**
	
		**newcoloring** :  dictionary
		
			The thresholded coloring dictionary.
	
	"""
	for key in coloring.keys():
		if len([k for k in coloring[key] if k in names]) == 0:
			coloring.pop(key)
		elif set(coloring[key]) == set(names):
			coloring.pop(key)
		else:
			coloring[key] = utils.uniqify([k for k in coloring[key] if k in names])
	return coloring
	
def backslash(dir):
	'''
	Add '/' to the end of a path if not already the last character. 
	
	Adds '/' to end of a path (meant to make formatting of 
	directory path `dir` consistently have the slash).
	
	**Parameters**
	
		**dir** :  string
		
			Path to a directory.

	**Returns**
	
		**out** :  string
		
			Same as `dir`, with '/' appended to the end if not 
			already there.
	
	'''

	if dir[-1] != '/':
		return dir + '/'
	else:
		return dir

def delete(ToDelete):
	'''
	Unified "strong" version of delete (remove) for files and directories.
	
	Unified "strong" version of delete that uses `os.remove` for a file 
	and `shutil.rmtree` for a directory tree.
	
	**Parameters**
	
		**ToDelete** :  string
		
			Path to a file or directory.

	**See Also:**
	
		`os <http://docs.python.org/library/os.html>`_, `shutil <http://docs.python.org/library/shutil.html>`_
	
	'''
	if os.path.isfile(ToDelete):
		os.remove(ToDelete)
	elif os.path.isdir(ToDelete):
		shutil.rmtree(ToDelete)		
		
def makedir(DirName):
	'''
	 "Strong" directory maker.
	
	"Strong" version of `os.mkdir`.  If `DirName` already exists, 
	this deletes it first. 
	
	**Parameters**
	
		**DirName** :  string
		
			Path to a file directory that may or may not already exist. 
	
	**See Also:**
	
		:func:`tabular.io.delete`, `os <http://docs.python.org/library/os.html>`_
	
	'''
	if os.path.exists(DirName):
			delete(DirName)
	os.mkdir(DirName)