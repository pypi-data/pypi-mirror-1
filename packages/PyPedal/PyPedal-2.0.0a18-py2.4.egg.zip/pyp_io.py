#!/usr/bin/python

###############################################################################
# NAME: pyp_io.py
# VERSION: 2.01 (28JAN2004)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#	id_map_from_file()
#	a_matrix_to_file()
#	a_matrix_from_file()
#	a_matrix_from_text_file()
#	a_inverse_from_file()
#	a_inverse_to_file()
###############################################################################

from string import *
from time import *
from Numeric import *

def id_map_from_file(inputfile):
	"""Read an ID map from a file and place it into a Python dictionary
	such that the new IDs are the keys and the original IDs are the
	values."""
	id_map = {}
	mapin = open(inputfile,'r')
	while 1:
		line = mapin.readline()
                if not line:
                        break
                else:
                        line = line[:-1]
                        if line[0] == '#':
                                pass
			else:
				l = split(line,',')
				id_map[l[1]] = l[0]
	mapin.close()
	return id_map

def a_matrix_to_file(myped,filetag='_pickled_',a=''):
	"""Use the Python pickle system for persistent objects to write a relationship matrix to a file."""
	from pickle import Pickler
	if not a:
		a = a_matrix(myped)
	a_outputfile = '%s%s%s' % (filetag,'_a_matrix_pickled_','.pkl')
	aout = open(a_outputfile,'w')
	ap = pickle.Pickler(aout)
	ap.dump(a)
	aout.close()

def a_matrix_from_file(inputfile):
	"""Use the Python pickle system for persistent objects to read a relationship matrix from a file."""
	from pickle import Pickler
	ain = open(inputfile,'r')
	au = pickle.Unpickler(ain)
	a = au.load()
	return a

def a_matrix_from_text_file():
	"""This is a placeholder.  The a_matrix() procedure currently writes
	A to a text file after A is formed and before the function returns.
	It would be handy to have a nice procedure to suck that back into
	an onject."""
	pass

def a_inverse_to_file(myped,filetag='_pickled_',ainv=''):
	"""Use the Python pickle system for persistent objects to write the inverse of a relationship matrix to a file."""
	from pickle import Pickler
	if not ainv:
		ainv = a_inverse_df(myped,filetag)
	a_outputfile = '%s%s%s' % (filetag,'_a_inverse_pickled_','.pkl')
	aout = open(a_outputfile,'w')
	ap = pickle.Pickler(aout)
	ap.dump(a)
	aout.close()

def a_inverse_from_file(inputfile):
	"""Use the Python pickle system for persistent objects to read the inverse of a relationship matrix from a file."""
	from pickle import Pickler
	ain = open(inputfile,'r')
	au = pickle.Unpickler(ain)
	a_inv = au.load()
	return a_inv

def dissertation_pedigree_to_file(myped,filetag='_diss'):
	# This procedure assumes that the pedigree passed to it is in 'asdxfg' format.
	length = len(myped)
	#print 'DEBUG: length of pedigree is %s' % (length)
	outputfile = '%s%s%s' % (filetag,'_diss','.ped')
	print '\t\tWriting dissertation pedigree to %s' % (outputfile)
	aout = open(outputfile,'w')
	aout.write('# DISSERTATION pedigree produced by PyPedal.\n')
	aout.write('% asdbxfg\n')
	for l in range(length):
		line = '%s,%s,%s,%s,%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID,myped[l].by,
			myped[l].sex,myped[l].fa,myped[l].gen)
		aout.write(line)
		# print line
	aout.close()

def dissertation_pedigree_to_pedig_format(myped,filetag='_diss'):
	# Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
	# Boichard's 'pedig' suite of programs, and writes them to a file.
	length = len(myped)
	outputfile = '%s%s%s' % (filetag,'_pedig','.ped')
	aout = open(outputfile,'w')
	for l in range(length):
		if myped[l].sex == 'm' or myped[l].sex == 'M':
				sex = 1
		else:
			sex = 2
		line = '%s %s %s %s %s %s %s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID,myped[l].by,
			sex,'1','1')
		aout.write(line)
	aout.close()

def dissertation_pedigree_to_pedig_interest_format(myped,filetag='_diss'):
	# Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
	# Boichard's parente program for the studied individuals file
	length = len(myped)
	outputfile = '%s%s%s' % (filetag,'_parente','.ped')
	aout = open(outputfile,'w')
	for l in range(length):
		line = '%s %s\n' % (myped[l].animalID,'1')
		aout.write(line)
	aout.close()

def dissertation_pedigree_to_pedig_format_mask(myped,filetag='_diss_mask'):
        # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
        # Boichard's 'pedig' suite of programs, and writes them to a file.
	#
	# THIS FUNCTION MASKS THE GENERATION ID WITH A FAKE BIRTH YEAR AND WRITES
	# THE FAKE BIRTH YEAR TO THE FILE INSTEAD OF THE TRUE BIRTH YEAR.  THIS IS
	# AN ATTEMPT TO FOOL PWDIG TO GET f_e, f_a et al. BY GENERATION.
	from string import *
        length = len(myped)
        outputfile = '%s%s%s' % (filetag,'_pedig_mask','.ped')
        aout = open(outputfile,'w')
        for l in range(length):
		## mask generations (yes, this could be shorter - but this is easy to debug
		mygen = float(myped[l].gen)
		if ( mygen > 0 and mygen <= 1.25 ):
			_gen = 10
		elif ( mygen > 1.25 and mygen <= 1.75 ):
			_gen = 15
		elif ( mygen > 1.75 and mygen <= 2.25 ):
                        _gen = 20
		elif ( mygen > 2.25 and mygen <= 2.75 ):
                        _gen = 25
		elif ( mygen > 2.75 and mygen <= 3.25 ):
                        _gen = 30
		elif ( mygen > 3.25 and mygen <= 3.75 ):
                        _gen = 35
		elif ( mygen > 3.75 and mygen <= 4.25 ):
                        _gen = 40
		elif ( mygen > 4.25 and mygen <= 4.75 ):
                        _gen = 45
		elif ( mygen > 4.75 and mygen <= 5.25 ):
                        _gen = 50
		elif ( mygen > 5.25 and mygen <= 5.75 ):
                        _gen = 55
		elif ( mygen > 5.75 and mygen <= 6.25 ):
                        _gen = 60
		elif ( mygen > 6.25 and mygen <= 6.75 ):
                        _gen = 65
		elif ( mygen > 6.75 and mygen <= 7.25 ):
                        _gen = 70
		elif ( mygen > 7.25 and mygen <= 7.75 ):
                        _gen = 75
		else:
			_gen = 0
		_maskgen = 1950 + _gen
		#print 'DEBUG: _gen = %d' % (_gen)
		#print 'DEBUG: myped[l].gen = %s' % (myped[l].gen)
		#print 'DEBUG: _maskgen = %d' % (_maskgen)
		## convert sexes
                if myped[l].sex == 'm' or myped[l].sex == 'M':
                                sex = 1
                else:
                        sex = 2
		#print 'DEBUG: An: %s\tSire: %s\tDam: %s\tGen: %s\tmg: %s' % (myped[l].animalID,myped[l].sireID,myped[l].damID,myped[l].gen,_maskgen)
                line = '%s %s %s %s %s %s %s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID,_maskgen,
                        sex,'1','1')
                aout.write(line)
        aout.close()
