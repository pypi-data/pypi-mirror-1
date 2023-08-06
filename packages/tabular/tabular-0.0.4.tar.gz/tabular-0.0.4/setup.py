"""
Setup script for the Tabular package.

"""

import ez_setup

long_desc = """
Tabular data can be easily represented in Python using the language's native objects -- e.g. by lists of tuples representing the records of the data set.    Though easy to create, these kind of representations typically do not enable important tabular data manipulations, like efficient column selection, matrix mathematics, or spreadsheet-style operations. 

**Tabular** is a package of Python modules for working with tabular data.     Its main object is the **tabarray** class, a data structure for holding and manipulating tabular data.  By putting data into a **tabarray** object, you'll get a representation of the data that is more flexible and powerful than a native Python representation.   More specifically, **tabarray** provides:
	
*	ultra-fast filtering, selection, and numerical analysis methods, using convenient Matlab-style matrix operation syntax
*  spreadsheet-style operations, including row & column operations, 'sort', 'replace',  'aggregate', 'pivot', and 'join'
*	flexible load and save methods for a variety of file formats, including separated values (SV), binary, HTML, and a hierarchical data format
*	support for hierarchical groupings of columns

**Note to NumPy Users:**  The **tabarray** object is based on the `record array <http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html?highlight=recarray#numpy.recarray>`_ object from the Numerical Python package (`NumPy <http://numpy.scipy.org/>`_), and the Tabular package is built to interface well with NumPy in general.  In particular, users of NumPy can get many of the benefits of Tabular, e.g. the spreadsheet-style operations, without having replace their usual NumPy objects with tabarrays, since most of the useful functional pieces of Tabular are written to work directly on NumPy ndarrays and record arrays.

Tabular is in beta!  More to come.  You will need NumPy 1.3. 

See documentation at http://www.parsemydata.com/tabular.

You can also clone our mercurial (hg) repository from bitbucket: http://bitbucket.org/elaine/tabular/.

"""

import sys
from setuptools import setup, find_packages

import tabular

if sys.version_info < (2, 5):
	print "WARNING:  Tabular has not been tested Python earlier than 2.5"
elif sys.version_info >= (3, 0):
	print "WARNING:  Tabular has not been tested on Python 3.0 or later."

setup(
	name = "tabular",
	version = "0.0.4",
	
	# Project uses NumPy 1.3 or later
	install_requires = ['numpy>=1.3'],
	
	scripts = ['ez_setup.py'],
	
	packages = find_packages(), 		# include all packages in source control
	
	include_package_data = True,    # include everything in source control
	
	# ... but exclude 'docs' and test data from all packages
	exclude_package_data = {'tests': ['tabularTestData']},
	
	# run nosetests by typing "python setup.py test"
	test_suite="nose.collector", 
	tests_require=["nose"],
	
	# metadata for upload to PyPI
	author = "Elaine Angelino and Daniel Yamins",
	author_email = "elaine.angelino at gmail dot com, dyamins at gmail dot com",
	description = "Tabular data container and associated convenience routines in Python",
	license = "MIT",
	keywords = "tabular data spreadsheet hierarchical",
	url = "http://pypi.python.org/pypi/tabular/",
	
	classifiers=[
		'Development Status :: 4 - Beta',
		'Programming Language :: Python',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
		'Topic :: Text Processing',
	],
	
	long_description = long_desc,
)