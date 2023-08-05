#!/usr/bin/python

###############################################################################
# NAME: pyp_nrm.py
# VERSION: 2.01 (28JAN2004)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
################################################################################ FUNCTIONS:
#	a_matrix()
#	fast_a_matrix()
#	a_decompose()
#	form_d_nof()
#	a_inverse_dnf()
#	a_inverse_df()
###############################################################################

from string import *
from time import *
from Numeric import *

def a_matrix(myped,filetag='_a_matrix_',save=0):
	"""Form a numerator relationship matrix from a pedigree."""
	l = len(myped)
	# Grab some array tools
	from Numarray import zeros
	a = zeros([l,l],Float)	# initialize a matrix of zeros of appropriate dimension
	for row in range(l):
		for col in range(row,l):
			# cast these b/c items are read from the pedigree file as characters, not integers
			myped[col].animalID = int(myped[col].animalID)
			myped[col].sireID = int(myped[col].sireID)
			myped[col].damID = int(myped[col].damID)
			if myped[col].sireID == 0 and myped[col].damID == 0:
				if row == col:
					# both parents unknown and assumed unrelated
					a[row,col] = 1.
				else:
					a[row,col] = 0.
					a[col,row] = a[row,col]
			elif myped[col].sireID == 0:
				# sire unknown, dam known
				if row == col:
					a[row,col] = 1.
				else:
					a[row,col] = 0.5 * a[row,myped[col].damID-1]
					a[col,row] = a[row,col]
			elif myped[col].damID == 0:
				# sire known, dam unknown
				if row == col:
					a[row,col] = 1.
				else:
					a[row,col] = 0.5 * a[row,myped[col].sireID-1]
					a[col,row] = a[row,col]
			elif myped[col].sireID > 0 and myped[col].damID > 0:
				# both parents known
				if row == col:
					a[row,col] = 1. + ( 0.5 * a[myped[col].sireID-1,myped[col].damID-1] )
				else:
					intermediate = a[row,myped[col].sireID-1] + a[row,myped[col].damID-1]
					finprod = 0.5 * intermediate
					a[row,col] = 0.5 * intermediate
					a[col,row] = a[row,col]
			else:
				print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (myped[col].sireID,myped[col].damID,myped[col].animalID)
				break
	# print a
	if save == 1:
		a_outputfile = '%s%s%s' % (filetag,'_a_matrix_','.dat')
		aout = open(a_outputfile,'w')
		for row in range(l):
			line = ''
			for col in range(l):
				if col == 0:
					line = '%7.5f' % (a[row,col])
				else:
					line = '%s%s%s' % (line,',',a[row,col])
			line = '%s%s' % (line,'\n')
			aout.write(line)
		aout.close()
	return a

def fast_a_matrix(myped,filetag='_new_a_matrix_',save=0):
	"""Form a numerator relationship matrix from a pedigree.  fast_a_matrix() is a hacked version of a_matrix()
	modified to try and improve performance.  Lists of animal, sire, and dam IDs are formed and accessed rather
	than myped as it is much faster to access a member of a simple list rather than an attribute of an object in a
	list.  Further note that only the diagonal and uppef off diagonal of A are populated.  This is done to save
	n(n+1) / 2 matix writes.  For a 1000-element array, this saves 1,001,000 writes."""
	animals = []
	sires = []
	dams = []
	l = len(myped)
	# Grab some array tools
	from Numeric import zeros
	a = zeros([l,l],Float)	# initialize a matrix of zeros of appropriate dimension
	for i in range(l):
		animals.append(int(myped[i].animalID))
		sires.append(int(myped[i].sireID))
		dams.append(int(myped[i].damID))
	for row in range(l):
		for col in range(row,l):
			if sires[col] == 0 and dams[col] == 0:
				if row == col:
					# both parents unknown and assumed unrelated
					a[row,col] = 1.
				#else:
				#	a[row,col] = 0.
					#a[col,row] = a[row,col]
			elif sires[col] == 0:
				# sire unknown, dam known
				if row == col:
					a[row,col] = 1.
				else:
					a[row,col] = 0.5 * a[row,dams[col]-1]
					a[col,row] = a[row,col]
			elif dams[col] == 0:
				# sire known, dam unknown
				if row == col:
					a[row,col] = 1.
				else:
					a[row,col] = 0.5 * a[row,sires[col]-1]
					a[col,row] = a[row,col]
			elif sires[col] > 0 and dams[col] > 0:
				# both parents known
				if row == col:
					a[row,col] = 1. + ( 0.5 * a[sires[col]-1,dams[col]-1] )
				else:
					intermediate = a[row,sires[col]-1] + a[row,dams[col]-1]
					finprod = 0.5 * intermediate
					a[row,col] = 0.5 * intermediate
					a[col,row] = a[row,col]
			else:
				print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (myped[col].sireID,myped[col].damID,myped[col].animalID)
				break
	# print a
	if save == 1:
		a_outputfile = '%s%s%s' % (filetag,'_new_a_matrix_','.dat')
		aout = open(a_outputfile,'w')
		for row in range(l):
			line = ''
			for col in range(l):
				if col == 0:
					line = '%7.5f' % (a[row,col])
				else:
					line = '%s%s%s' % (line,',',a[row,col])
			line = '%s%s' % (line,'\n')
			aout.write(line)
		aout.close()
	return a

def a_decompose(myped,filetag='_a_decompose_',a=''):
	"""Form the decomposed form of A, TDT', directly from a pedigree (after
	Henderson, 1976; Thompson, 1977; Mrode, 1996).  Return D, a diagonal
	matrix, and T, a lower triagular matrix such that A = TDT'."""
	if not a:
		a = a_matrix(myped)
	l = len(myped)
	# Grab some array tools
	#from Numeric import *
	from Numeric import identity
	T = identity(l)
	T = T.astype(Float)
	D = identity(l)
	D = D.astype(Float)
	for row in range(l):
		for col in range(row+1):
			# cast these b/c items are read from the pedigree file as characters, not  integers
			myped[col].animalID = int(myped[col].animalID)
			myped[col].sireID = int(myped[col].sireID)
			myped[col].damID = int(myped[col].damID)
			if myped[row].sireID == 0 and myped[row].damID == 0:
				if row == col:
					# both parents unknown and assumed unrelated
					foo = 1.
					T[row,col] = foo

					D[row,col] = 1.
				else:
					foo = 0.
					T[row,col] = foo
			elif myped[row].sireID == 0:
				# sire unknown, dam known
				if row == col:
					foo = 1.
					T[row,col] = foo

					fd = a[myped[row].damID-1,myped[row].damID-1] - 1.
					D[row,col] = 0.75 - ( 0.5 * fd )
				else:
					foo = 0.5 * T[myped[row].damID-1,col]
					T[row,col] = foo
			elif myped[row].damID == 0:
				# sire known, dam unknown
				if row == col:
					foo = 1.
					T[row,col] = foo

					fs = a[myped[row].sireID-1,myped[row].sireID-1] - 1.
					D[row,col] = 0.75 - ( 0.5 * fs )
				else:
					foo = 0.5 * T[myped[row].sireID-1,col]
					T[row,col] = foo
			elif myped[row].sireID > 0 and myped[row].damID > 0:
				# both parents known
				if row == col:
					foo = 1.
					T[row,col] = foo

					fs = a[myped[row].sireID-1,myped[row].sireID-1] - 1.
					fd = a[myped[row].damID-1,myped[row].damID-1] - 1.
					D[row,col] = 0.5 - ( 0.25 * ( fs + fd ) )
				else:
					foo = 0.5 * ( T[int(myped[row].sireID)-1,col] + T[int(myped[row].damID)-1,col] )
					T[row,col] = foo
			else:
				print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (myped[col].sireID,myped[col].damID,myped[col].animalID)
				break
	#print D
	#print T

	outputfile = '%s%s%s' % (filetag,'_a_decompose_d_','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (D[row,col])
			else:
				line = '%s%s%s' % (line,',',D[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	outputfile = '%s%s%s' % (filetag,'_a_decompose_t_','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (T[row,col])
			else:
				line = '%s%s%s' % (line,',',T[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	return D,T

def form_d_nof(myped):
	"""Form the diagonal matrix, D, used in decomposing A and forming the direct
	inverse of A.  This function does not write output to a file - if you need D in
	a file, use the a_decompose()  function.  form_d() is a convenience function
	used by other functions.  Note that inbreeding is not considered in the
	formation of D."""
	l = len(myped)
	# Grab some array tools
	#from Numeric import *
	from Numeric import identity
	D = identity(l)
	D = D.astype(Float)
	for row in range(l):
		for col in range(row+1):
			# cast these b/c items are read from the pedigree file as characters, not integers
			myped[col].animalID = int(myped[col].animalID)
			myped[col].sireID = int(myped[col].sireID)
			myped[col].damID = int(myped[col].damID)
			if myped[row].sireID == 0 and myped[row].damID == 0:
				if row == col:
					# both parents unknown and assumed unrelated
					D[row,col] = 1.
				else:
					pass
			elif myped[row].sireID == 0:
				# sire unknown, dam known
				if row == col:
					D[row,col] = 0.75
				else:
					pass
			elif myped[row].damID == 0:
				# sire known, dam unknown
				if row == col:
					D[row,col] = 0.75
				else:
					pass
			elif myped[row].sireID > 0 and myped[row].damID > 0:
				# both parents known
				if row == col:
					D[row,col] = 0.5
				else:
					pass
			else:
				print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (myped[col].sireID,myped[col].damID,myped[col].animalID)
				break
	return D

def a_inverse_dnf(myped,filetag='_a_inverse_dnf_'):
	"""Form the inverse of A directly using the method of Henderson (1976) which
	does not account for inbreeding."""
	l = len(myped)
	# grab the diagonal matrix, d, and form its inverse
	d_inv = form_d_nof(myped)
	for i in range(l):
		d_inv[i,i] = 1. / d_inv[i,i]
	# Grab some array tools
	#from Numeric import *
	from Numeric import zeros
	a_inv = zeros([l,l],Float)
	for i in range(l):
		# cast these b/c items are read from the pedigree file as characters, not integers
		myped[i].animalID = int(myped[i].animalID)
		myped[i].sireID = int(myped[i].sireID)
		myped[i].damID = int(myped[i].damID)
		s = myped[i].sireID-1
		d = myped[i].damID-1
		if myped[i].sireID == 0 and myped[i].damID == 0:
			# both parents unknown and assumed unrelated
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
		elif myped[i].sireID == 0:
			# sire unknown, dam known
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
			a_inv[d,i] = a_inv[d,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,d] = a_inv[i,d] + ( (-0.5) * d_inv[i,i] )
			a_inv[d,d] = a_inv[d,d] + ( 0.25 * d_inv[i,i] )
		elif myped[i].damID == 0:
			# sire known, dam unknown
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
			a_inv[s,i] = a_inv[s,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,s] = a_inv[i,s] + ( (-0.5) * d_inv[i,i] )
			a_inv[s,s] = a_inv[s,s] + ( 0.25 * d_inv[i,i] )
		elif myped[i].sireID > 0 and myped[i].damID > 0:
			# both parents known
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
			a_inv[s,i] = a_inv[s,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,s] = a_inv[i,s] + ( (-0.5) * d_inv[i,i] )
			a_inv[d,i] = a_inv[d,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,d] = a_inv[i,d] + ( (-0.5) * d_inv[i,i] )
			a_inv[s,s] = a_inv[s,s] + ( 0.25 * d_inv[i,i] )
			a_inv[s,d] = a_inv[s,d] + ( 0.25 * d_inv[i,i] )
			a_inv[d,s] = a_inv[d,s] + ( 0.25 * d_inv[i,i] )
			a_inv[d,d] = a_inv[d,d] + ( 0.25 * d_inv[i,i] )
		else:
			print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (myped[col].sireID,myped[col].damID,myped[col].animalID)
			break

	outputfile = '%s%s%s' % (filetag,'_a_inverse_dnf_a_inv','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (a_inv[row,col])
			else:
				line = '%s%s%s' % (line,',',a_inv[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	outputfile = '%s%s%s' % (filetag,'_a_inverse_dnf_d_inv','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (d_inv[row,col])
			else:
				line = '%s%s%s' % (line,',',d_inv[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	return a_inv

def a_inverse_df(myped,filetag='_a_inverse_df_'):
	"""Directly form the inverse of A from the pedigree file - accounts for 
	inbreeding - using the method of Quaas (1976)."""
	l = len(myped)
	from math import sqrt
	# Grab some array tools
	#from Numeric import *
	from Numeric import zeros
	d_inv = zeros([l,l],Float)
	a_inv = zeros([l,l],Float)
	LL = zeros([l,l],Float)
	# Form L and D-inverse
	for row in range(l):
		for col in range(row+1):
			# cast these b/c items are read from the pedigree file as characters, not integers
			myped[col].animalID = int(myped[col].animalID)
			myped[col].sireID = int(myped[col].sireID)
			myped[col].damID = int(myped[col].damID)
			s = myped[row].sireID-1
			d = myped[row].damID-1
			s_sq = d_sq = 0.
			if row == col:
				for m in range(s+1):
					s_sq = s_sq + ( LL[s,m] * LL[s,m] )
				s_sq = 0.25 * s_sq
				for m in range(d+1):
					d_sq = d_sq + ( LL[d,m] * LL[d,m] )
				d_sq = 0.25 * d_sq
				LL[row,col] = sqrt(1. - s_sq - d_sq)
				d_inv[row,col] = 1. / ( LL[row,col] * LL[row,col] )
			else:
				LL[row,col] = 0.5 * ( LL[s,col] + LL[d,col] )
	# use D-inverse to compute A-inverse
	for i in range(l):
		s = myped[i].sireID-1
		d = myped[i].damID-1
		if myped[i].sireID == 0 and myped[i].damID == 0:
			# both parents unknown and assumed unrelated
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
		elif myped[i].sireID == 0:
			# sire unknown, dam known
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
			a_inv[d,i] = a_inv[d,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,d] = a_inv[i,d] + ( (-0.5) * d_inv[i,i] )
			a_inv[d,d] = a_inv[d,d] + ( 0.25 * d_inv[i,i] )
		elif myped[i].damID == 0:
			# sire known, dam unknown
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
			a_inv[s,i] = a_inv[s,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,s] = a_inv[i,s] + ( (-0.5) * d_inv[i,i] )
			a_inv[s,s] = a_inv[s,s] + ( 0.25 * d_inv[i,i] )
		elif myped[i].sireID > 0 and myped[i].damID > 0:
			# both parents known
			a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
			a_inv[s,i] = a_inv[s,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,s] = a_inv[i,s] + ( (-0.5) * d_inv[i,i] )
			a_inv[d,i] = a_inv[d,i] + ( (-0.5) * d_inv[i,i] )
			a_inv[i,d] = a_inv[i,d] + ( (-0.5) * d_inv[i,i] )
			a_inv[s,s] = a_inv[s,s] + ( 0.25 * d_inv[i,i] )
			a_inv[s,d] = a_inv[s,d] + ( 0.25 * d_inv[i,i] )
			a_inv[d,s] = a_inv[d,s] + ( 0.25 * d_inv[i,i] )
			a_inv[d,d] = a_inv[d,d] + ( 0.25 * d_inv[i,i] )

	outputfile = '%s%s%s' % (filetag,'_a_inverse_df_a_inv','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (a_inv[row,col])
			else:
				line = '%s%s%s' % (line,',',a_inv[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	outputfile = '%s%s%s' % (filetag,'_a_inverse_df_l','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (LL[row,col])
			else:
				line = '%s%s%s' % (line,',',LL[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	outputfile = '%s%s%s' % (filetag,'_a_inverse_df_d_inv','.dat')
	aout = open(outputfile,'w')
	for row in range(l):
		line = ''
		for col in range(l):
			if col == 0:
				line = '%7.5f' % (d_inv[row,col])
			else:
				line = '%s%s%s' % (line,',',d_inv[row,col])
		line = '%s%s' % (line,'\n')
		aout.write(line)
	aout.close()

	return a_inv
