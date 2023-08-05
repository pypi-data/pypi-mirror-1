#!/usr/bin/python

###############################################################################
# NAME: pyp_exceptions.py
# VERSION: 2.0.0a8 (30AUGUST2004)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################

##
# pyp_exceptions contains the code for custom PyPedal exceptions etc.
##

from exceptions import Exception
import sys

##
# PypError is the base class, derived from exceptions.Exception(), from which all other PyPedal
# exceptions are derived.
class PypError(Exception):
	def __init__(self):
		pass

##
# PypInputFileError is raised when a pedigree file cannot be opened.  It takes an optional argument
# that indicates which file could not be opened.
class PypInputFileError(PypError):
	"""The __init__ method takes a filename as the argument so the user knows which file could not be opened."""
	def __init__(self,filename='<unknown file>'):
		self.message = 'Unable to open pedigree file %s for reading!' % (filename)
		print 'PypInputFileError: %s' % (self.message)

##
# PypPedigreeFormatError is raised when an invalid format code is encountered in a pedigree format string.
class PypPedigreeFormatError(PypError):
	def __init__(self,formatcode='<unknown code>'):
		self.message = 'The pedigree format code %s contained an invalid format specifier!' % (formatcode)
		print 'PypPedigreeFormatError: %s' % (self.message)