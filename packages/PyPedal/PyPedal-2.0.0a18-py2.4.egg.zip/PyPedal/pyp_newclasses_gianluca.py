#!/usr/bin/env python

# GS: It's better to use env: env, as a standard command of the shell is always in /usr/bin, rather than python that can be everything
# JB:  You are right,

###############################################################################
# NAME: pyp_newclasses.py
# VERSION: 2.0.0a8 (30AUGUST2004)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################

##
# pyp_newclasses contains the new class structure that will be a part of PyPedal 2.0.0Final.
# It includes a master class to which most of the computational routines will be bound as
# methods, a NewAnimal() class, and a PedigreeMetadata() class.
##

# JB: It is important to remember that this file is more notes on my thought process than
#     final, working code.  You will see that some of the code is cut-and-pasted from other
#     files.  The code that actually works (however poorly) is found in pyp_classes.py.

from string import *
from time import *
from numarray import *

import os
import sys

# Import the other pieces of PyPedal.  This will probably go away as most of these are rolled into
# NewPedigree as methods.
import pyp_demog
import pyp_exceptions
import pyp_io
import pyp_metrics
import pyp_nrm
import pyp_peel
import pyp_utils

##
# The NewPedigree class is the main data structure for PyP 2.0.0Final.
# GS: Using a lot of ifs in the initialisation class can result in a (little overhed). 

class NewPedigree:
    def __init__(self,source,format='asd',title='Unnamed',messages='terse',**kw):
        """Initialize a new Pedigree."""
        # Handle the main keywords.  Is there a better way to do this?  I think maybe so -- such as reading
        # a bunch of default values for, e.g., the reorder and renumber flags, from an input file.
        
        self.source = source
        #GS: sorce is a mandatoryarguments, so at the moment no check is needed. Further you'll check for file existence, 
        # GS: off course, but I think there may be the opportunity to write some factory functions that can load data from different
        # GS: sources, build a list, a tuple or a dictionary and using it to initialize the Pedigree Class.
        # GS: In other words, IMHO, source must be a list, a dictionary or a tuple. What do you prefer?
        # JB: At the moment source is not checked until the file is opened (if if exists), so for now it assumes that the
        #     user will know what to do when Python throws a file-not-found exception.  We can check it here to save a little
        #     time, I guess.
        # JB: As far as source being multiple files...we would have to do a little more work to make sure that there are no
        #     animalID collisions between the two files but I do not see any reason why pedigree data could not be loaded
        #     from more than one source.  This would require multiple calls to load() but that is doable.

        self.format = format

        self.title = title

        self.messages = messages
        
        # GS: Here all arguments specified in kw becomes class attributes: (python 2.2 and later)
        # JB: I have not used the **kw construct before, but I want to.  If you look at some of the
        #     procedures in pyp_utils.py you will see that a ridiculous number of aprameters are
        #     passed explicitly.  Using **kw is a little bit better way to handle that.
        for k,v in kw.items():
          self.__dict__[k]=v

        # So let's learn how to read things in from a configuration file.
        #GS: for such kind of operations I prefer to use XML file. Xmls are harder to modify by and, by easier to
        #GS: modify by a routine. Please, remeber me to send you a little class to manage configuration xml.
        # JB: This is probably a matter of personal preference.  I feel that an XML configuration file is needlessly
        #     complex.  In fact, I feel strongly enough about that to insist on using ConfigParser OR to support both
        #     styles of configuration file.  You can try and change my mind if you like, but you probably will not
        #     succeed.  :-)
            
        import ConfigParser #GS: import xml.dom.minidom
        config = ConfigParser.SafeConfigParser() 
        config.readfp(open('PyPedal.ini'))
        
        # Initialize the Big Main Data Structures to null values
        self.pedigree = []                         # We may start storing animals in a dictionary rather than in a list.  Maybe,
        self.metadata = {}                        # Metadata will also be stored in a dictionary.
        # Maybe these will go in a configuration file later
        self.starline = '*'*80
    ##
    # load() wraps several processes useful for loading and preparing a pedigree for use in an
    # analysis, including reading the animals into a list of animal objects, forming lists of sires and dams,
    # checking for common errors, setting ancestor flags, and renumbering the pedigree.
    # @param renum Flag to indicate whether or not the pedigree is to be renumbered.
    # @param alleles Flag to indicate whether or not pyp_metrics/effective_founder_genomes() should be called for a single round to assign alleles.
    # @return None
    def load(self,renum=1,alleles=0):
        self.myped = self.preprocess_pedigree()
        #GS: You nowhere declare self.renumber , do you mean renum?
        # JB: Yes.  This is code that was cut-and-pasted.  The original procedure call
        #     probably used renumber.
        if self.renumber:
            if self.messages == 'verbose':
                print '%s\n\tCalling fast_reorder() at %s' % (starline,asctime(localtime(time())))
            self.pedigree = fast_reorder(self.pedigree)
            if self.messages == 'verbose':
                print '%s\n\tCalling renumber() at %s' % (starline,asctime(localtime(time())))
            #GS: From where renumber comes? have you forgotten module reference?
            # JB: This is NOT working code.  The idea is that renumber will be moved from
            #     pyp_utils.py to a method of this class.
            self.pedigree = renumber(self.pedigree)
        if self.messages == 'verbose':
            print '%s\n\tCalling set_generation() at %s' % (starline,asctime(localtime(time())))
        #GS: Same. this function return values or it modifies self.pedigree? 
        # JB: When working, this will modify self.pedigree.
        set_generation(self.pedigree)
        if self.messages == 'verbose':
            print '%s\n\tCalling set_ancestor() at %s' % (starline,asctime(localtime(time())))
        #GS: Same
        # JB: As above.
        set_ancestor_flag(self.pedigree)
        if alleles:
            if self.messages == 'verbose':
                print '%s\n\tCalling pyp_metrics.effective_founder_genomes() at %s' % (starline,asctime(localtime(time())))
            pyp_metrics.effective_founder_genomes(self.pedigree)
        if self.messages == 'verbose':
            print '%s\n\tCalling pyp_classes/PedigreeMetadata() at %s' % (starline,asctime(localtime(time())))
        self.metadata = PedigreeMetadata(self.pedigree)

##
# The NewAnimal() class is holds animals records read from a pedigree file.
class NewAnimal:
    """A simple class to hold animals records read from a pedigree file."""
    ##
    # __init__() initializes an Animal() object.
    # @param self Reference to the current Animal() object
    # @param animalID Animal ID number
    # @param sireID Sire ID number
    # @param damID Dam ID number
    # @param gen Generation to which the animal belongs
    # @param by Birthyear of the animal
    # @param sex Sex of the animal (m|f|u)
    # @param fa Coefficient of inbreeding of the animal
    # @param name Name of animal
    # @param alleles A two-element array of strings, which represent allelotypes.
    # @param species Species of animal
    # @param breed Breed of animal
    # @param age Age of animal
    # @param alive Status of animal (alive or dead)
    # @return An instance of an Animal() object populated with data
    # @defreturn object
    def __init__(self,animalID,sireID,damID,gen='0',by=1900,sex='u',fa=0.,name='u',alleles=['',''],species='u',breed='u',age=-999,alive=-999):
        #GS: Why to set by=1900? In humans pedigree this can provide some matters. I'd prefer None
        # JB: This is an arbitrary number.  The code was originally written to work with dog pedigrees that had complete
        #     birthdate information.  If we set it to None then we will need to trap that in some other procedures/methods.
        #     For example, the Boichard algorithms for effective founder and ancestor numbers require generation information.
        #     When generations are not provided in the pedigree file they are inferred using, in part, birth year.  I am open to
        #     changing this.
        # JB: Oh!  The pad_id() method uses the birthdate to form the padded ID.
        """Initialize an animal record."""
        self.animalID = string.strip(animalID)
        self.originalID = self.animalID
        self.renumberedID = -999
        self.sireID = string.strip(sireID)
        self.damID = string.strip(damID)
        self.gen = gen
        self.igen = -999
        self.sex = sex
        self.by = by
        self.fa = fa
        if self.sireID == '0' and self.damID == '0':
            self.founder = 'y'
        else:
            self.founder = 'n'
        self.paddedID = self.pad_id()
        self.ancestor = 0
        self.name = name
        self.sons = {}
        self.daus = {}
        self.unks = {}
        self.breed = breed
        # Assign alleles for use in gene-dropping runs.  Automatically assign two distinct alleles
        # to founders if no genotypes information is provided.  Otherwise, use the alleles passed
        # to Animal.__init__().
        
        #GS: As soon as I can understand only two alleles can be specified.
        # JB: Because I only added alleles to support gene dropping.  I am open to changing this as well --
        #     human geneticists probably need to handle more information than that.
        
        if alleles == ['',''] and self.founder == 'y':
            _allele_1 = '%s%s' % (self.paddedID,'__1')
            _allele_2 = '%s%s' % (self.paddedID,'__2')
            self.alleles = [_allele_1,_allele_2]
        else:
            self.alleles = alleles
        self.pedcomp = -999.9
        self.age = age
        self.alive = alive
        self.species = species
    ##
    # printme() prints a summary of the data stored in the Animal() object.
    # @param self Reference to the current Animal() object
    def printme(self):
        """Print the contents of an animal record - used for debugging."""
        #gs: This  concerns the feature I ask for. Do you think it is possible to use STRING animal's(person's) ID?
        #gs: perhaps with a mandatoru renumber.
        # JB: I think that it would not be too hard to do that.  We just need to hash the string to an integer somehow.
        #     Once that is done the reorder and renumber routines should handle it from there.
        self.animalID = int(self.animalID)
        self.sireID = int(self.sireID)
        self.damID = int(self.damID)
        self.by = int(self.by)
        print 'ANIMAL %s RECORD' % (self.animalID)
        print '\tAnimal ID:\t%s' % (self.animalID)
        print '\tAnimal name:\t%s' % (self.name)
        print '\tSire ID:\t%s' % (self.sireID)
        print '\tDam ID:\t\t%s' % (self.damID)
        print '\tGeneration:\t%s' % (self.gen)
        print '\tInferred gen.:\t%s' % (self.igen)
        print '\tBirth Year:\t%s' % (self.by)
        print '\tSex:\t\t%s' % (self.sex)
        print '\tCoI (f_a):\t%s' % (self.fa)
        print '\tFounder:\t%s' % (self.founder)
        print '\tSons:\t\t%s' % (self.sons)
        print '\tDaughters:\t%s' % (self.daus)
        print '\tUnknowns:\t%s' % (self.unks)
        print '\tAncestor:\t%s' % (self.ancestor)
        print '\tAlleles:\t%s' % (self.alleles)
        print '\tOriginal ID:\t%s' % (self.originalID)
        print '\tRenumbered ID:\t%s' % (self.renumberedID)
        print '\tPedigree Comp.:\t%s' % (self.pedcomp)
        print '\tSpecies:\t%s' % (self.species)
        print '\tBreed:\t%s' % (self.breed)
        print '\tAge:\t%s' % (self.age)
        print '\tAlive:\t%s' % (self.alive)
    ##
    # stringme() returns a summary of the data stored in the Animal() object
    # as a string.
    # @param self Reference to the current Animal() object
    def stringme(self):
        """Return the contents of an animal record as a string."""
        self.animalID = int(self.animalID)
        self.sireID = int(self.sireID)
        self.damID = int(self.damID)
        self.by = int(self.by)
        _me = ''
        _me = '%s%s' % ( _me, 'ANIMAL %s RECORD\n' % (self.animalID) )
        _me = '%s%s' % ( _me, '\tAnimal ID:\t%s\n' % (self.animalID) )
        _me = '%s%s' % ( _me, '\tAnimal name:\t%s\n' % (self.name) )
        _me = '%s%s' % ( _me, '\tSire ID:\t%s\n' % (self.sireID) )
        _me = '%s%s' % ( _me, '\tDam ID:\t\t%s\n' % (self.damID) )
        _me = '%s%s' % ( _me, '\tGeneration:\t%s\n' % (self.gen) )
        _me = '%s%s' % ( _me, '\tInferred gen.:\t%s\n' % (self.igen) )
        _me = '%s%s' % ( _me, '\tBirth Year:\t%s\n' % (self.by) )
        _me = '%s%s' % ( _me, '\tSex:\t\t%s\n' % (self.sex) )
        _me = '%s%s' % ( _me, '\tCoI (f_a):\t%s\n' % (self.fa) )
        _me = '%s%s' % ( _me, '\tFounder:\t%s\n' % (self.founder) )
        _me = '%s%s' % ( _me, '\tSons:\t\t%s\n' % (self.sons) )
        _me = '%s%s' % ( _me, '\tDaughters:\t%s\n' % (self.daus) )
        _me = '%s%s' % ( _me, '\tUnknowns:\t%s\n' % (self.unks) )
        _me = '%s%s' % ( _me, '\tAncestor:\t%s\n' % (self.ancestor) )
        _me = '%s%s' % ( _me, '\tAlleles:\t%s\n' % (self.alleles) )
        _me = '%s%s' % ( _me, '\tOriginal ID:\t%s\n' % (self.originalID) )
        _me = '%s%s' % ( _me, '\tRenumbered ID:\t%s\n' % (self.renumberedID) )
        _me = '%s%s' % ( _me, '\tPedigree Comp.:\t%s\n' % (self.pedcomp) )
        _me = '%s%s' % ( _me, '\tSpecies:\t%s' % (self.species) )
        _me = '%s%s' % ( _me, '\tBreed:\t%s' % (self.breed) )
        _me = '%s%s' % ( _me, '\tAge:\t%s' % (self.age) )
        _me = '%s%s' % ( _me, '\tAlive:\t%s' % (self.alive) )
        return _me
    ##
    # trap() checks for common errors in Animal() objects
    # @param self Reference to the current Animal() object
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
    ##
    # pad_id() takes an Animal ID, pads it to fifteen digits, and prepends the birthyear
    # (or 1950 if the birth year is unknown).  The order of elements is: birthyear, animalID,
    # count of zeros, zeros.
    # @param self Reference to the current Animal() object
    # @return A padded ID number that is supposed to be unique across animals
    # @defreturn integer
    def pad_id(self):
        """Take an Animal ID, pad it to fifteen digits, and prepend the birthyear (or 1950 if the birth year is unknown)"""
        #GS: len() cannot be used with numeric values. If you call stringme before pad_id you will raise an exception
        # JB: I have never called the methods in that order so I never noticed this.  D'oh!
        l = len(self.animalID)
        pl = 15 - l - 1
        if pl > 0:
            zs = '0'*pl
            pid = '%s%s%s%s' % (self.by,zs,self.animalID,l)
        else:
            pid = '%s%s%s' % (self.by,self.animalID,l)
        return pid

##
# The PedigreeMetadata() class stores metadata about pedigrees.  Hopefully this will help improve performance in some procedures,
# as well as provide some useful summary data.
class PedigreeMetadata:
    """A class to hold metadata about pedigrees.  Hopefully this will help improve performance in some procedures, as well as
    provide some useful summary data."""
    ##
    # __init__() initializes a Pedigree metata object.
    # @param self Reference to the current Pedigree() object
    # @param myped A PyPedal pedigree
    # @param inputfile The name of the file from which the pedigree was loaded
    # @param name The name assigned to the PyPedal pedigree
    # @param pedcode The format code for the PyPedal pedigree
    # @param reord Flag indicating whether or not the pedigree is reordered (0|1)
    # @param renum Flag indicating whether or not the pedigree is renumbered (0|1)
    # @return An instance of a Pedigree() object populated with data
    # @defreturn object
    def __init__(self,myped,inputfile,name,pedcode='asd',reord=0,renum=0,debug=0):
        """Initialize a pedigree record."""
        #GS: better to evitate ==1. I read somewhere that it's more efficient to do:
        # JB: At some point I was thinking of having different debug levels that would trigger messages based on
        #     values greater than 1.  This never happened.
        #GS: Another question. Why use debug variable? python tracebacks are not enough?
        # JB: The DEBUG statements should (perhaps) have a different name.  I use them to track what the program
        #    is doing even when it is working correctly.  Maybe a verbose switch would be a good replacement here.
        #    the debug statements are called even when there are no eceptions thrown (and therefore no tracebacks).
        if debug: #== 1:
            print '\t\t[DEBUG]:  Instantiating a new Pedigree() object...'
    
        if debug:# == 1:
            print '\t\t[DEBUG]:  Naming the Pedigree()...'
        self.name = name
        if debug:# == 1:
            print '\t\t[DEBUG]:  Assigning a filename...'
        self.filename = inputfile
        if debug:# == 1:
            print '\t\t[DEBUG]:  Attaching a pedigree...'
        self.myped = myped
        if debug:# == 1:
            print '\t\t[DEBUG]:  Setting the pedcode...'
        self.pedcode = pedcode
        if debug:# == 1:
            print '\t\t[DEBUG]:  Counting the number of animals in the pedigree...'
        self.num_records = len(self.myped)
        if debug:# == 1:
            print '\t\t[DEBUG]:  Counting and finding unique sires...'
        self.num_unique_sires, self.unique_sire_list = self.nus()
        if debug:# == 1:
            print '\t\t[DEBUG]:  Counting and finding unique dams...'
        self.num_unique_dams, self.unique_dam_list = self.nud()
        if debug:# == 1:
            print '\t\t[DEBUG]:  Setting reord flag...'
        self.reordered = reord
        if debug:# == 1:
            print '\t\t[DEBUG]:  Setting renum flag...'
        self.renumbered = renum
        if debug:# == 1:
            print '\t\t[DEBUG]:  Counting and finding unique generations...'
        self.num_unique_gens, self.unique_gen_list = self.nug()
        if debug:# == 1:
            print '\t\t[DEBUG]:  Counting and finding unique birthyears...'
        self.num_unique_years, self.unique_year_list = self.nuy()
        if debug:# == 1:
            print '\t\t[DEBUG]:  Counting and finding unique founders...'
        self.num_unique_founders, self.unique_founder_list = self.nuf()
        if debug:# == 1:
            print '\t\t[DEBUG]:  Detaching pedigree...'
        self.myped = []
    ##
    # printme() prints a summary of the metadata stored in the Pedigree() object.
    # @param self Reference to the current Pedigree() object
    def printme(self):
        """Print the pedigree metadata."""
        print 'PEDIGREE %s (%s)' % (self.name,self.filename)
        print '\tRecords:\t\t%s' % (self.num_records)
        print '\tUnique Sires:\t\t%s' % (self.num_unique_sires)
        print '\tUnique Dams:\t\t%s' % (self.num_unique_dams)
        print '\tUnique Gens:\t\t%s' % (self.num_unique_gens)
        print '\tUnique Years:\t\t%s' % (self.num_unique_years)
        print '\tUnique Founders:\t%s' % (self.num_unique_founders)
        print '\tPedigree Code:\t\t%s' % (self.pedcode)
    ##
    # stringme() returns a summary of the metadata stored in the pedigree as
    # a string.
    # @param self Reference to the current Pedigree() object
    def stringme(self):
        """Build a string from the pedigree metadata."""
        _me = ''
        _me = '%s%s' % ( _me, 'PEDIGREE %s (%s)\n' % (self.name,self.filename) )
        _me = '%s%s' % ( _me, '\tRecords:\t\t\t%s\n' % (self.num_records) )
        _me = '%s%s' % ( _me, '\tUnique Sires:\t\t%s\n' % (self.num_unique_sires) )
        _me = '%s%s' % ( _me, '\tUnique Dams:\t\t%s\n' % (self.num_unique_dams) )
        _me = '%s%s' % ( _me, '\tUnique Gens:\t\t%s\n' % (self.num_unique_gens) )
        _me = '%s%s' % ( _me, '\tUnique Years:\t\t%s\n' % (self.num_unique_years) )
        _me = '%s%s' % ( _me, '\tUnique Founders:\t%s\n' % (self.num_unique_founders) )
        _me = '%s%s' % ( _me, '\tPedigree Code:\t\t%s\n' % (self.pedcode) )
        return _me
    ##
    # fileme() writes the metada stored in the Pedigree() object to disc.
    # @param self Reference to the current Pedigree() object
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

    ##
    # nus() returns the number of unique sires in the pedigree along with a list of the sires
    # @param self Reference to the current Pedigree() object
    # @return The number of unique sires in the pedigree and a list of those sires
    # @defreturn integer-and-list
    def nus(self):
        """Count the number of unique sire IDs in the pedigree.  Returns an integer count and a Python list of the
        unique sire IDs."""
    siredict = {}
        for l in range(self.num_records):
        if int(self.myped[l].sireID) != 0:
            try:
            _s = siredict[self.myped[l].sireID]
                except KeyError:
            siredict[self.myped[l].sireID] = self.myped[l].sireID
        n = len(siredict.keys())
        return n, siredict.keys()
    ##
    # nud() returns the number of unique dams in the pedigree along with a list of the dams
    # @param self Reference to the current Pedigree() object
    # @return The number of unique dams in the pedigree and a list of those dams
    # @defreturn integer-and-list
    def nud(self):
        """Count the number of unique dam IDs in the pedigree.  Returns an integer count and a Python list of the
        unique dam IDs."""
        damdict = {}
        for l in range(self.num_records):
            if int(self.myped[l].damID) != 0:
                try:
                    _d = damdict[self.myped[l].damID]
                except KeyError:
                    damdict[self.myped[l].damID] = self.myped[l].damID
        n = len(damdict.keys())
        return n, damdict.keys()
    ##
    # nug() returns the number of unique generations in the pedigree along with a list of the generations
    # @param self Reference to the current Pedigree() object
    # @return The number of unique generations in the pedigree and a list of those generations
    # @defreturn integer-and-list
    def nug(self):
    """Count the number of unique generations in the pedigree.  Returns an integer count and a Python list of the
        unique generations."""
        gendict = {}
        for l in range(self.num_records):
            try:
                _g = gendict[self.myped[l].gen]
            except KeyError:
                gendict[self.myped[l].gen] = self.myped[l].gen
        n = len(gendict.keys())
        return n, gendict.keys()
    ##
    # nuy() returns the number of unique birthyears in the pedigree along with a list of the birthyears
    # @param self Reference to the current Pedigree() object
    # @return The number of unique birthyears in the pedigree and a list of those birthyears
    # @defreturn integer-and-list
    def nuy(self):
    """Count the number of unique birth years in the pedigree.  Returns an integer count and a Python list of the
        unique birth years."""
        yeardict = {}
        for l in range(self.num_records):
            try:
                _y = yeardict[self.myped[l].by]
            except KeyError:
                yeardict[self.myped[l].by] = self.myped[l].by
        n = len(yeardict.keys())
        return n, yeardict.keys()
    ##
    # nuf() returns the number of unique founders in the pedigree along with a list of the founders
    # @param self Reference to the current Pedigree() object
    # @return The number of unique founders in the pedigree and a list of those founders
    # @defreturn integer-and-list
    def nuf(self):
    """Count the number of unique founders in the pedigree."""
        founderdict = {}
        for l in range(self.num_records):
            if self.myped[l].founder == 'y':
                try:
                    _f = founderdict[self.myped[l].animalID]
                except KeyError:
                    founderdict[self.myped[l].animalID] = self.myped[l].animalID
        n = len(founderdict.keys())
        return n, founderdict.keys()
