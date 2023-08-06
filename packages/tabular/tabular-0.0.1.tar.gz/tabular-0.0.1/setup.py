"""
Setup script for the Tabular package.

"""

import ez_setup

long_desc = """
The **Tabular** package provides a container for tabular data, called **tabarray**.  It is based on the `record array <http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html?highlight=recarray#numpy.recarray>`_ object from the Numerical Python package (`NumPy <http://numpy.scipy.org/>`_), adding some additional structure and convenience functions.  The **tabarray** has:
	
*	excellent filtering and subselection
*	column-oriented (hierarchical) structure
*	ability to attach row-by-row structured metadata
*	flexible load and save methods for several file formats
*  spreadsheet-style operations, including 'sort', 'replace', 'pivot' and 'aggregate'

Tabular is in beta! Definitely not stable.  You will need numpy.  Documentation and a bitbucket distribution are coming. 

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
	version = "0.0.1",
	
	# Project uses NumPy 1.3 or later
	install_requires = ['numpy>=1.3'],
	
	scripts = ['ez_setup.py'],
	
	packages = find_packages(), 		# include all packages in source control
	
	include_package_data = True,    # include everything in source control
	
	# ... but exclude 'docs' and test data from all packages
	exclude_package_data = {'tests': ['tabularTestData']},
	
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