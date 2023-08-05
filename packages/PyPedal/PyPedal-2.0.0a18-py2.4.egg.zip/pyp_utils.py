#!/usr/bin/python

###############################################################################
# NAME: pyp_utils.py
# VERSION: 2.01 (28JAN2004)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#	preprocess()
#	reorder()
#	fast_reorder()
#	renumber()
#	id_map_new_to_old()
#	trim_pedigree_to_year()
###############################################################################

from string import *
from time import *
from Numeric import *
from pyp_classes import *

def preprocess(inputfile,sepchar=',',debug=0):
	"""Preprocess a pedigree file, which includes reading the animals into a list, forming lists of sires and dams, and checking for common errors."""
	#from pyp_classes import *
	lineCounter = 0		# count the number of lines in the pedigree file
	animalCounter = 0	# count the number of animal records in the pedigree file
	animals= []		# holds a list of Animal() objects
	_animals = {}
	males = {}		# holds a list of male IDs in the pedigree
	females = {}		# holds a list of female IDs in the pedigree
	unknowns = {}		# holds a list of animals of unknown sex
	pedformat = ''		# stores the pedigree format string
	#sepchar = ','		# default column separator is a comma
	infile=open(inputfile,'r')
	while 1:
		line = infile.readline()
		if not line:
			break
		else:
			if debug > 1:
				print line
			line = string.strip(line[:-1])
			lineCounter = lineCounter + 1
			if line[0] == '#':
				pass
			elif line[0] == '%':
				pedformat = strip(line[1:]) # this lets us specify the format of the pedigree file
				pass
			else:
				if fmod(animalCounter,10000) == 0:
					print'%s ' % (animalCounter)
				animalCounter = animalCounter + 1
				l = split(line,sepchar)
				# Some people *cough* Brad Heins *cough* insist on sending me pedigree
				# files vomited out by Excel, which pads cells in a column with spaces
				# to right-align them...
				for i in range(len(l)):
					l[i] = string.strip(l[i])
				if len(l) < 3:
					errorString = 'The record on line %s of file %s is too short - all records must contain animal, sire, and dam ID numbers (%s fields detected).\n' % (lineCounter,inputfile,len(l))
					print '[ERROR]: %s' % (errorString)
					break
				# now we have to deal with different pedigree data formats...
				if pedformat == '':
					pedformat = 'asd'
				if pedformat == 'asd':
					an = Animal(l[0],l[1],l[2])
				elif pedformat == 'asdg':
					an = Animal(l[0],l[1],l[2],gen=l[3])
				elif pedformat == 'asdx':
					an = Animal(l[0],l[1],l[2],l[3])
				elif pedformat == 'asdb':
					an = Animal(l[0],l[1],l[2],by=l[3])
				elif pedformat == 'asdf':
					an = Animal(l[0],l[1],l[2],fa=l[3])
				elif pedformat == 'asdxb':
					an = Animal(l[0],l[1],l[2],sex=l[3],by=l[4])
				elif pedformat == 'asdxf':
					an = Animal(l[0],l[1],l[2],sex=l[3],fa=l[4])
				elif pedformat == 'asdbf':
					an = Animal(l[0],l[1],l[2],by=l[3],fa=l[4])
				elif pedformat == 'asdxbf':
					an = Animal(l[0],l[1],l[2],sex=l[3],by=l[4],fa=l[5])
				elif pedformat == 'asdyxfg':
					# This is the format that I have put the TSEI pedigrees into for preprocessing.
					if len(l[3]) > 0:
						splityear = l[3].split('/')
						birthyear = splityear[2]
					else:
						birthyear = '1950'
					an = Animal(l[0],l[1],l[2],by=birthyear,sex=l[4],fa=l[5],gen=l[6])
					#print 'DEBUG: %s' % (line)
					#an.printme()
				elif pedformat == 'asdbxfg':
					# This is the format that PyPedal puts TSEI pedigrees into for analysis.
					an = Animal(l[0],l[1],l[2],by=l[3],sex=l[4],fa=l[5],gen=l[6])
				else:
					errorString = 'Pedigree file %s has an invalid format code (%s) on line %s.\n' % (inputfile,pedformat,counter)
					print '[ERROR]: %s' % (errorString)
				# NOTE: we have an odd situation where animals may appear in both unknown and known
				# [sex] lists b/c the sex of sires and dams is inferred from their location in the
				# animal record.  Base animals without sex codes are assigned a sex of 'u' (unknown)
				# by default if no code is included in the pedigree file.  When those parents appear
				# later as parents, they will be placed in the appropriate list.  The program does
				# remove animals from the UNKNOWN list once they are placed in a sex-specific list.
				#
				# There is a problem with the current implementation here.  An "if animal in list"
				# statement is used, which is fine for small pedigrees.  It degrades very badly for
				# large pedigrees.  Hm...maybe a dictionary?  Dictionaries are insanely faster.  The
				# right tool...
				#
				# Do not insert duplicate males into the MALES list
				try:
					_i =  males[an.sireID]
				except KeyError:
					males[an.sireID] = an.sireID
				# Do not insert duplicate females into the FEMALES list
				try:
                                        _i =  females[an.damID]
                                except KeyError:
                                        females[an.damID] = an.damID
				# Check the sex code to see which list an animal should be placed in
				# 'M' or 'm' codes for males
				if an.sex == 'M' or an.sex == 'm':
					try:
	                                        _i =  males[an.animalID]
	                                except KeyError:
        	                                males[an.animalID] = an.animalID
				# 'F' or 'f' codes for females
				elif an.sex == 'F' or an.sex == 'f':
					try:
                                                _i =  females[an.animalID]
                                        except KeyError:
                                                females[an.animalID] = an.animalID
				# Any other character is treated as unknown
				else:
					unknowns[an.animalID] = an.animalID
				# Make sure that sires are not also coded as dams
				try:
					_i = females[an.sireID]
					if _i == 0:
						pass
					else:
						print '[ERROR]: Animal %s is coded as a sire (male) for some animal records, but as a dam (female) for other animal records (check record %s - animal ID %s)' % (an.sireID,animalCounter,an.animalID)
                                        	break
				except:
					pass
				# Make sure that dams are not also coded as sires
				try:
                                        _i = males[an.damID]
                                        if _i == 0:
                                                pass
                                        else:
                                                print '[ERROR]: Animal %s is coded as a dam (female) for some animal records, but as a sire (male) for other animal records (check record %s - animal ID %s)' % (an.damID,animalCounter,an.animalID)
                                                break
                                except:
                                        pass

				# Infers the sex of an animal with unknown gender based on whether or not they later appear as a sire
				# or a dam in the pedigree file.
				try:
					_i = unknowns[an.sireID]
					del unknowns[an.sireID]
				except KeyError:
					pass
				try:
                                        _i = unknowns[an.damID]
                                        del unknowns[an.damID]
                                except KeyError:
                                        pass

				# Suppose that base animals are not given an individual entry in the
				# pedigree file...it is necessary to catch that case and add an animal
				# object to the list for them.
				# First for sires...
				try:
					_i = _animals[an.sireID]
				except KeyError:
					_an = Animal(an.sireID,'0','0')
					_animals[an.sireID] = an.sireID
					animals.append(_an)
				# ...and then for dams
				try:
                                        _i = _animals[an.damID]
                                except KeyError:
                                        _an = Animal(an.damID,'0','0')
                                        _animals[an.damID] = an.damID
                                        animals.append(_an)

				animals.append(an)
				_animals[an.animalID] = an.animalID
			#print '[DEBUG]: males ', males
			#print '[DEBUG]: females ', females
			#print '[DEBUG]: unknowns ', unknowns

	infile.close()
	if debug:
		print '[MESSAGE]: %s animal records read from pedigree file %s'  %(animalCounter,inputfile)
		print '[MESSAGE]: %s animal records created from the pedigree file' % (len(animals))
		print '[MESSAGE]: %s unique sires found in the pedigree file' % (len(males))
		print '[MESSAGE]: %s unique dams found in the pedigree file' % (len(females))
		print '[MESSAGE]: %s unique animals of unknown gender found in the pedigree file' % (len(unknowns))
		print ''
	return animals

def reorder(myped,filetag='_reordered_',io='no'):
	"""Renumber a pedigree such that parents precede their offspring in the
 pedigree.  In order to minimize overhead as much as is reasonably possible,
 a list of animal IDs that have already been seen is kept.  Whenever a parent
 that is not in the seen list is encountered, the offspring of that parent is
 moved to the end of the pedigree.  This should ensure that the pedigree is
 properly sorted such that all parents precede their offspring.  myped is
 reordered in place.

 reorder() is VERY slow, but I am pretty sure that it works correctly."""

	# This is crufty and therefore offensive.  Furthermore, it will only work when
	# animal IDs are integers.  Some solution to this problem needs to be found.  Perhaps a
	# strcmp()-type string method can be used for generalization...
	l = len(myped)
	print 'Pedigree contains %s animals.' % (l)
	for i in range(l):
		myped[i].animalID = int(myped[i].animalID)
		myped[i].sireID = int(myped[i].sireID)
		myped[i].damID = int(myped[i].damID)
	pedordered = 0		# the pedigree is not known to be ordered
	passnum = 0		# we are going to count how many passes through the pedigree are needed
				# to sort it
 	while(1):
		#
		# Loop over the pedigree.  Whenever a parent follows their offspring in the
		# pedigree, move the child to the end of the pedigree.  Continue until all parents precede
		# their offspring.
		#
		if ( passnum == 0 ) or ( passnum % 10 == 0 ):
			print '...%s' % (passnum)
		order = []
		for i in range(l):
			order.append(myped[i].animalID)
		passnum = passnum + 1
		order = []		# list of animal IDs in the order in which they appear in myped
		kill = []		# list of indices to delete
		seen = []		# list of animal IDs already encountered
		l = len(myped)
		for i in range(l):
			if ( myped[i].sireID in seen or myped[i].sireID == 0 ) and ( myped[i].damID in seen or myped[i].damID == 0 ) :
				if myped[i].animalID in seen:
					pass
				else:
					seen.append(myped[i].animalID)
			else:
				# move current record to end of list
				myped.append(myped[i])
				if myped[i].sireID in seen:
					pass
				else:
					seen.append(myped[i].sireID)
				if myped[i].damID in seen:
					pass
				else:
					seen.append(myped[i].damID)
				kill.append(i)
		#
		# Use the list 'kill' to remove records that have been duplicated at the end
		# of the pedigree list.  This insures that there is only a single copy of
		# each unique record in the pedigree.
		#
		kill.reverse()
		for k in kill:
			del myped[k]
		for i in range(l):
			order.append(myped[i].animalID)
		#
		# This next bit of code loops over the pedigree once it has been reordered.
		# If all parents precede their children, then the pedigree is fully reordered
		# and the loop is exited.  Else continue looping.
		#
		for i in range(l):
			ano = order.index(myped[i].animalID)
			if myped[i].sireID != 0:
				sro = order.index(myped[i].sireID)
			else:
				sro = -999
			if myped[i].damID != 0:
				dmo = order.index(myped[i].damID)
			else:
				dmo = -999
			if ( sro < 0 ) :
				pass
			if ( dmo < 0 ):
				pass
			if ( ano < sro ) or ( ano < dmo ):
				pedordered = 0
				break
			else:
				pedordered = 1
		if pedordered == 1:
			break
	if io == 'yes':
		# Write the reordered pedigree to a file and return the ordered pedigree.
		# Note that the reordered pedigree is currently only writte in the 'asd'
		# format, regardless of the format of the original file.
		a_outputfile = '%s%s%s' % (filetag,'_reordered','.ped')
		aout = open(a_outputfile,'w')
		aname = '# FILE: %s\n' % (a_outputfile)
		aout.write(aname)
		aout.write('# REORDERED pedigree produced by PyPedal.\n')
		aout.write('% asd\n')
		for l in range(len(myped)):
			line = '%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
			aout.write(line)
		aout.close()
	return myped

def fast_reorder(myped,filetag='_new_reordered_',io='no'):
	"""Renumber a pedigree such that parents precede their offspring in the
 pedigree.  In order to minimize overhead as much as is reasonably possible,
 a list of animal IDs that have already been seen is kept.  Whenever a parent
 that is not in the seen list is encountered, the offspring of that parent is
 moved to the end of the pedigree.  This should ensure that the pedigree is
 properly sorted such that all parents precede their offspring.  myped is
 reordered in place.

 reorder() is VERY slow, but I am pretty sure that it works correctly.  fast_reorder()
 appears to be VERY fast, but I am not sure if it works correctly all of the time or not.
 Use this procedure at your own risk!"""

	l = len(myped)
	idlist = []
	animalmap = {}
	## <kludge>
	myped.reverse()
	## </kludge>
	## print '\tPedigree contains %s animals.' % (l)
	## print '\tMaking a dictionary of animal objects'
	## print '\tMaking a list of padded animal IDs'
	for i in range(l):
		## print '\tDEBUG\tID %s = %s' % (i,myped[i].paddedID)
		animalmap[myped[i].paddedID] = myped[i]
		idlist.append(myped[i].paddedID)

	## print '\tSorting padded animal IDs'
	idlist.sort()
	myped = []
	## print '\tReforming myped'
	l = len(idlist)
	## print '\tDEBUG\t%s elements in idlist' % (l)
	for i in range(len(idlist)):
		myped.append(animalmap[idlist[i]])
	if io == 'yes':
		# Write the reordered pedigree to a file and return the ordered pedigree.
		# Note that the reordered pedigree is currently only written in the 'asd'
		# format, regardless of the format of the original file.
		a_outputfile = '%s%s%s' % (filetag,'_reord','.ped')
		aout = open(a_outputfile,'w')
		aname = '# FILE: %s\n' % (a_outputfile)
		aout.write(aname)
		aout.write('# REORDERED pedigree produced by PyPedal using new_reorder().\n')
		aout.write('% asd\n')
		for l in range(len(myped)):
			line = '%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
			aout.write(line)
		aout.close()
	return myped

def renumber(myped,filetag='_renumbered_',io='no',outformat='0'):
	"""renumber() takes a pedigree as input and renumbers it such that the oldest
	animal in the pedigree has an ID of '1' and the n-th animal has an ID of 'n'.  If the
	pedigree is not ordered from oldest to youngest such that all offspring precede their
	offspring, the pedigree will be reordered.  The renumbered pedigree is written to disc in
	'asd' format and a map file that associates sequential IDs with original IDs is also
	written."""

#	myped = fast_reorder(myped,filetag)

	# In the dictionary id_map, the old IDs are the keys and the
	# new IDs are the values.
	id_map = {}
	idnum = 1		# starting ID number for renumbered IDs
	for l in range(len(myped)):
		if fmod(l,10000) == 0:
                    print'%s ' % (l)
		#print 'DEBUG: An:%s\tSire: %s\tDam: %s' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
		id_map[myped[l].animalID] = idnum
		#myped[l].animalID = id_map[myped[l].animalID]
		#print 'DEBUG: renumbering animal from %s to %s (iter %s)' % (myped[l].animalID,idnum,l)
		myped[l].animalID = idnum
		# We cannot forget to renumber parents, too!
		s = myped[l].sireID
		if s != '0' and s != 0:
			myped[l].sireID = id_map[s]
		d = myped[l].damID
		if d != '0' and d!= 0:
			myped[l].damID = id_map[d]
		idnum = idnum + 1
		#print 'DEBUG: animal ID = %s' % (myped[l].animalID)
		#print 'DEBUG: An:%s\tSire: %s\tDam: %s' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
		#print
	if io == 'yes':
		# Write the renumbered pedigree to a file
		ped_outputfile = '%s%s%s' % (filetag,'_renum','.ped')
		pout = open(ped_outputfile,'w')
		pname = '# FILE: %s\n' % (ped_outputfile)
		pout.write(pname)
		pout.write('# RENUMBERED pedigree produced by PyPedal.\n')
		pout.write('% asd\n')
		for l in range(len(myped)):
			if outformat == '0':
				line = '%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID)
			else:
				line = '%s,%s,%s,%s,%s,%s,%s\n' % (myped[l].animalID,myped[l].sireID,myped[l].damID,myped[l].by,
					myped[l].sex,myped[l].fa,myped[l].gen)
			pout.write(line)
		pout.close()
	# Write the old ID -> new ID mapping to a file
	map_outputfile = '%s%s%s' % (filetag,'_id_map','.map')
	mout = open(map_outputfile,'w')
	mname = '# FILE: %s\n' % (map_outputfile)
	mout.write(mname)
	mout.write('# Renumbered ID to Old ID mapping produced by PyPedal.\n')
	mout.write('# The lefthand column contains the original IDs.\n')
	mout.write('# The righthand column contains the renumbered IDs.\n')
	mout.write('Old ID\tRenum ID\n')
	k = id_map.keys()
	v = id_map.values()
	for l in range(len(id_map)):
		line = '%s,%s\n' % (k[l],v[l])
		#print 'Old ID = %s,  New ID = %s' % (k[l],v[l])
		mout.write(line)
	mout.close()
	return myped

def id_map_new_to_old(id_map,new_id):
	"""Given an ID from a renumbered pedigree, return the original
	ID number."""
	old_id = id_map.get(new_id,0)
	return old_id

def trim_pedigree_to_year(myped,year):
	# trim_pedigree_to_year() takes pedigrees and removes all individuals
	# who were not born in birthyear 'year'.  The reduced (trimmed) pedigree
	# is returned.
	indices = []
	modped = myped[:]
	for l in range(len(modped)):
		#print 'DEBUG: %s, %s' % (year,modped[l].by)
		if int(modped[l].by) == int(year):
			pass
		else:
			#del modped[l]
			indices.append(l)
	indices.reverse()
	for i in range(len(indices)):
		del modped[indices[i]]
	#print 'DEBUG: l_orig: %s, l_trim: %s' % (len(myped),len(modped))
	return modped
