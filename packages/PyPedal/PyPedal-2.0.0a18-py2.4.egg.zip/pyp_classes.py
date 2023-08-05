#!/usr/bin/python

###############################################################################
# NAME: pyp_classes.py
# VERSION: 2.01 (28JAN2004)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
###############################################################################

from string import *
from time import *
from Numeric import *

class Animal:
	"""A simple class to hold animals records read from a pedigree file."""
	def __init__(self,animalID,sireID,damID,gen='0',by='1950',sex='u',fa=0.):
		"""Initialize and animal record."""
		self.animalID = string.strip(animalID)
		self.sireID = string.strip(sireID)
		self.damID = string.strip(damID)
		self.gen = gen
		self.sex = sex
		self.by = by
		self.fa = fa
		if self.sireID == '0' and self.damID == '0':
			self.founder = 'y'
		else:
			self.founder = 'n'
		self.paddedID = self.pad_id_new()
		#self.trap()
		#self.animalID = int(self.animalID)
		#self.sireID = int(self.sireID)
		#self.damID = int(self.damID)
	def printme(self):
		"""Print the contents of an animal record - used for debugging."""
		self.animalID = int(self.animalID)
		self.sireID = int(self.sireID)
		self.damID = int(self.damID)
		self.by = int(self.by)
		print 'ANIMAL %s RECORD\n' % (self.animalID)
		print '\tAnimal ID:\t%s\n' % (self.animalID)
		print '\tSire ID:\t%s\n' % (self.sireID)
		print '\tDam ID:\t%s\n' % (self.damID)
		print '\tGeneration:\t%s\n' % (self.gen)
		print '\tBirth Year:\t%s\n' % (self.by)
		print '\tSex:\t%s\n' % (self.sex)
		print '\tCoI (f_a):\t%s\n' % (self.fa)
		print '\tFounder:\t%s\n' % (self.founder)
	def trap(self):
		"""Trap common errors in pedigree file entries."""
		if int(self.animalID) == int(self.sireID):
			print '[ERROR]: Animal %s has an ID number equal to its sire\'s ID (sire ID %s).\n' % (self.animalID,self.sireID)
		if int(self.animalID) == int(self.damID):
			print '[ERROR]: Animal %s has an ID number equal to its dam\'s ID (dam ID %s).\n' % (self.animalID,self.damID)
		if int(self.animalID) < int(self.sireID):
			print '[ERROR]: Animal %s is older than its sire (sire ID %s).\n' % (self.animalID,self.sireID)
		if int(self.animalID) < int(self.damID):
			print '[ERROR]: Animal %s is older than its dam (dam ID %s).\n' % (self.animalID,self.damID)
	def pad_id(self):
		"""Take an Animal ID, pad it to fifteen digits, and prepend the birthyear (or 1950 if the birth year is unknown)"""
		l = len(self.animalID)
		pl = 15 - l - 1
		if pl > 0:
			zs = '0'*pl
			pid = '%s%s%s%s' % (self.by,self.animalID,l,zs)
		else:
			pid = '%s%s%s' % (self.by,self.animalID,l)
		return pid
	def pad_id_new(self):
		"""Take an Animal ID, pad it to fifteen digits, and prepend the birthyear (or 1950 if the birth year is unknown)"""
                l = len(self.animalID)
                pl = 15 - l - 1
                if pl > 0:
                        zs = '0'*pl
                        pid = '%s%s%s%s' % (self.by,self.animalID,zs,l)
                else:
                        pid = '%s%s%s' % (self.by,self.animalID,l)
                return pid

class Pedigree:
	"""A class to hold metadata about pedigrees.  Hopefully this will help improve performance in some procedures, as well as
	provide some useful summary data."""
	def __init__(self,myped,inputfile,name,pedcode='asd',reord=0,renum=0):
		"""Initialize an animal record."""
		self.name = name
		self.filename = inputfile
		self.myped = myped
		self.pedcode = pedcode
		self.num_records = len(self.myped)
		self.num_unique_sires, self.unique_sire_list = self.nus()
		self.num_unique_dams, self.unique_dam_list = self.nud()
		self.reordered = reord
		self.renumbered = renum
		self.num_unique_gens, self.unique_gen_list = self.nug()
		self.num_unique_years, self.unique_year_list = self.nuy()
		self.num_unique_founders, self.unique_founder_list = self.nuf()
		self.myped = []
	def printme(self):
		"""Print the pedigree metadata."""
		print 'PEDIGREE %s (%s)\n' % (self.name,self.filename)
		print '\tRecords:\t%s\n' % (self.num_records)
		print '\tUnique Sires:\t%s\n' % (self.num_unique_sires)
		print '\tUnique Dams:\t%s\n' % (self.num_unique_dams)
		print '\tUnique Gens:\t%s\n' % (self.num_unique_gens)
		print '\tUnique Years:\t%s\n' % (self.num_unique_years)
		print '\tUnique Founders:\t%s\n' % (self.num_unique_founders)
		print '\tPedigree Code:\t%s\n' % (self.pedcode)
	def fileme(self):
		"""Save the pedigree metadata to a file."""
		outputfile = '%s%s%s' % (self.name,'_ped_metadata_','.dat')
		aout = open(outputfile,'w')
		line1 = 'PEDIGREE %s (%s)\n' % (self.name,self.filename)
		line2 = '\tRecords:\t%s\n' % (self.num_records)
		line3 = '\tUnique Sires:\t%s\n' % (self.num_unique_sires)
		line4 = '\tUnique Dams:\t%s\n' % (self.num_unique_dams)
		line5 = '\tPedigree Code:\t%s\n' % (self.pedcode)
		line6 = '\tUnique Founders:\t%s\n' % (self.num_unique_founders)
		line7 =  '\tUnique Gens:\t%s\n' % (self.num_unique_gens)
		line8 = '\tUnique Years:\t%s\n' % (self.num_unique_years)
		line9 = '='*80
		line10 = '\tUnique Sire List:\t%s\n' % (self.unique_sire_list)
		line11 = '\tUnique Dam List:\t%s\n' % (self.unique_dam_list)
		line12 = '\tUnique Gen List:\t%s\n' % (self.unique_gen_list)
		line13 = '\tUnique Year List:\t%s\n' % (self.unique_year_list)
		line14 = '\tUnique Founder List:\t%s\n' % (self.num_founder_list)
		aout.write(line1)
		aout.write(line2)
		aout.write(line3)
		aout.write(line4)
		aout.write(line5)
		aout.write(line6)
		aout.write(line7)
		aout.write(line8)
		aout.write(line9)
		aout.write(line10)
		aout.write(line11)
		aout.write(line12)
		aout.write(line13)
		aout.write(line14)
		aout.close()
	def nus(self):
		"""Count the number of unique sire IDs in the pedigree.  Returns an integer count and a Python list of the
		unique sire IDs."""
		sirelist = []
		for l in range(self.num_records):
			if self.myped[l].sireID not in sirelist:
				sirelist.append(self.myped[l].sireID)
		n = len(sirelist)
		return n, sirelist
	def nud(self):
		"""Count the number of unique dam IDs in the pedigree.  Returns an integer count and a Python list of the
		unique dam IDs."""
		damlist = []
		for l in range(self.num_records):
			if self.myped[l].damID not in damlist:
				damlist.append(self.myped[l].damID)
		n = len(damlist)
		return n, damlist
	def nug(self):
		"""Count the number of unique generations in the pedigree.  Returns an integer count and a Python list of the
		unique generations."""
		genlist = []
		for l in range(self.num_records):
			if self.myped[l].gen not in genlist:
				genlist.append(self.myped[l].gen)
		n = len(genlist)
		return n, genlist
	def nuy(self):
		"""Count the number of unique birth years in the pedigree.  Returns an integer count and a Python list of the
		unique birth years."""
		yearlist = []
		for l in range(self.num_records):
			if self.myped[l].by not in yearlist:
				yearlist.append(self.myped[l].by)
		n = len(yearlist)
		return n, yearlist
	def nuf(self):
		"""Count the number of unique founders in the pedigree."""
		founderlist = []
		for l in range(self.num_records):
			if self.myped[l].founder == 'y':
				founderlist.append(self.myped[l].animalID)
		n = len(founderlist)
		return n, founderlist
