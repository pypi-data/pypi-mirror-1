 #!/usr/bin/python

###############################################################################
# NAME: pyp_newclasses.py
# VERSION: 2.0.0a19 (03AUGUST2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################

##
# pyp_newclasses contains the new class structure that will be a part of PyPedal 2.0.0Final.
# It includes a master class to which most of the computational routines will be bound as
# methods, a NewAnimal() class, and a PedigreeMetadata() class.
##

import cPickle
import logging
import numarray
import os
import string
import sys

# Import the other pieces of PyPedal.  This will probably go away as most of these are rolled into
# NewPedigree as methods.
import pyp_demog
import pyp_io
import pyp_metrics
import pyp_nrm
import pyp_utils

try:
    from psyco.classes import __metaclass__
except ImportError:
    pass

##
# The NewPedigree class is the main data structure for PyP 2.0.0Final.
class NewPedigree:
    def __init__(self,kw):
        """Initialize a new Pedigree."""
        # Handle the Main Keywords.
        if not kw.has_key('pedfile'): raise PedigreeInputFileNameError
        if not kw.has_key('pedformat'): kw['pedformat'] = 'asd'
        if not kw.has_key('pedname'): kw['pedname'] = 'Untitled'
        if not kw.has_key('messages'): kw['messages'] = 'verbose'
        if not kw.has_key('renumber'): kw['renumber'] = 0
        if not kw.has_key('reorder'): kw['reorder'] = 0
        if not kw.has_key('pedigree_is_renumbered'): kw['pedigree_is_renumbered'] = 0
        if not kw.has_key('set_generations'): kw['set_generations'] = 0
        if not kw.has_key('set_ancestors'): kw['set_ancestors'] = 0
        if not kw.has_key('set_alleles'): kw['set_alleles'] = 0
        if not kw.has_key('set_offspring'): kw['set_offspring'] = 0
        if not kw.has_key('set_sexes'): kw['set_sexes'] = 0
        if not kw.has_key('sepchar'): kw['sepchar'] = ' '
        if not kw.has_key('alleles_sepchar'): kw['alleles_sepchar'] = '/'
        if not kw.has_key('counter'): kw['counter'] = 1000
        if not kw.has_key('slow_reorder'): kw['slow_reorder'] = 1
        if not kw.has_key('missing_parent'): kw['missing_parent'] = '0'
        if not kw.has_key('file_io'): kw['file_io'] = '1'
        if not kw.has_key('debug_messages'): kw['debug_messages'] = 0
        if not kw.has_key('form_nrm'): kw['form_nrm'] = 0
        if not kw.has_key('nrm_method'): kw['nrm_method'] = 'nrm'
        if not kw.has_key('f_computed'): kw['f_computed'] = 0
        if not kw.has_key('log_ped_lines'): kw['log_ped_lines'] = 0
        if not kw.has_key('log_long_filenames'): kw['log_long_filenames'] = 0
        if 'f' in kw['pedformat']:
            kw['f_computed'] = 1
        kw['filetag'] = string.split(kw['pedfile'],'.')[0]
        if len(kw['filetag']) == 0:
            kw['filetag'] = 'untitled_pedigree'
        if not kw.has_key('database_name'): kw['database_name'] = 'pypedal'
        if not kw.has_key('dbtable_name'):
            kw['dbtable_name'] = pyp_utils.string_to_table_name(kw['filetag'])
        else:
            kw['dbtable_name'] = pyp_utils.string_to_table_name(kw['dbtable_name'])
        self.kw = kw

        # Initialize the Big Main Data Structures to null values
        self.pedigree = []                         # We may start storing animals in a dictionary rather than in a list.  Maybe,
        self.metadata = {}                         # Metadata will also be stored in a dictionary.
        self.idmap = {}                            # Used to map between original and renumbered IDs.
        self.backmap = {}                          # Used to map between renumbered and original IDs.
        # Maybe these will go in a configuration file later
        self.starline = '*'*80
        # Start logging!
        if not self.kw.has_key('logfile'):
            if kw['log_long_filenames']:
                self.kw['logfile'] = '%s_%s.log' % ( self.kw['filetag'], pyp_utils.pyp_datestamp() )
            else:
                self.kw['logfile'] = '%s.log' % ( self.kw['filetag'] )
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%a, %d %b %Y %H:%M:%S',
            filename=self.kw['logfile'],
            filemode='w')
        logging.info('Logfile %s instantiated.',self.kw['logfile'])
        if self.kw['messages'] == 'verbose':
            print '[INFO]: Logfile %s instantiated.' % (self.kw['logfile'])
        # Deal with abberant cases of log_ped_lines here.
        try:
            _lpl = kw['log_ped_lines']
            kw['log_ped_lines'] = int(kw['log_ped_lines'])
        except ValueError:
            kw['log_ped_lines'] = 0
            log.warning('An incorrect value (%s) was provided for the option log_ped_lines, which must be a number greater than or equal 0.  It has been set to 0.', _lpl)
        if  kw['log_ped_lines'] < 0:
            kw['log_ped_lines'] = 0
            log.warning('A negative value (%s) was provided for the option log_ped_lines, which must be greater than or equal 0.  It has been set to 0.', kw['log_ped_lines'])

    ##
    # load() wraps several processes useful for loading and preparing a pedigree for
    # use in an analysis, including reading the animals into a list of animal objects,
    # forming lists of sires and dams, checking for common errors, setting ancestor
    # flags, and renumbering the pedigree.
    # @param renum Flag to indicate whether or not the pedigree is to be renumbered.
    # @param alleles Flag to indicate whether or not pyp_metrics/effective_founder_genomes() should be called for a single round to assign alleles.
    # @return None
    # @defreturn None
    def load(self,pedsource='file'):
#         print self.kw
        if pedsource == 'db':
            logging.warning('Loading pedigrees from a database is not yet \
                implemented.')
            pass
        else:
            logging.info('Preprocessing %s',self.kw['pedfile'])
            if self.kw['messages'] == 'verbose':
                print '[INFO]: Preprocessing %s' % (self.kw['pedfile'])
            self.preprocess()
            if self.kw['renumber'] == 1:
                self.renumber()
            if self.kw['reorder'] == 1 and not self.kw['renumber']:
                if self.kw['messages'] == 'verbose':
                    print '\t[INFO]: Reordering pedigree at %s' % ( pyp_utils.pyp_nice_time() )
                logging.info('Reordering pedigree')
                if not self.kw['slow_reorder']:
                    self.pedigree = pyp_utils.fast_reorder(self.pedigree)
                else:
                    self.pedigree = pyp_utils.reorder(self.pedigree)
            if self.kw['set_generations']:
                logging.info('Assigning generations')
                if self.kw['messages'] == 'verbose':
                  print '\t[INFO]: Assigning generations at %s' % ( pyp_utils.pyp_nice_time() )
                self.pedigree = pyp_utils.set_generation(self.pedigree)
            if self.kw['set_ancestors']:
                logging.info('Setting ancestor flags')
                if self.kw['messages'] == 'verbose':
                    print '\t[INFO]: Setting ancestor flags at %s' % ( pyp_utils.pyp_nice_time() )
                self.pedigree = pyp_utils.set_ancestor_flag(self.pedigree)
            if self.kw['set_alleles']:
                logging.info('Gene dropping to compute founder genome equivalents')
                if self.kw['messages'] == 'verbose':
                    print '\t[INFO]: Gene dropping at %s' % ( pyp_utils.pyp_nice_time() )
                pyp_metrics.effective_founder_genomes(self)
            if self.kw['form_nrm']:
                logging.info('Forming numerator relationship matrix')
                if self.kw['messages'] == 'verbose':
                    print '\t[INFO]: Forming numerator relationship matrix at %s' % ( pyp_utils.pyp_nice_time() )
                self.nrm = NewAMatrix(self.kw)
                self.nrm.form_a_matrix(self.pedigree)
            if self.kw['set_offspring'] and not self.kw['renumber']:
                logging.info('Assigning offspring')
                if self.kw['messages'] == 'verbose':
                    print '\t[INFO]: Assigning offspring at %s' % ( pyp_utils.pyp_nice_time() )
                pyp_utils.assign_offspring(self)
            if self.kw['set_sexes']:
                logging.info('Assigning sexes')
                if self.kw['messages'] == 'verbose':
                    print '\t[INFO]: Assigning sexes at %s' % ( pyp_utils.pyp_nice_time() )
                pyp_utils.assign_sexes(self)
            if self.kw['messages'] == 'verbose':
                print '[INFO]: Creating pedigree metadata object'
            self.metadata = PedigreeMetadata(self.pedigree,self.kw)
            if self.kw['messages'] != 'quiet':
                self.metadata.printme()

    ##
    # save() writes a PyPedal pedigree to a user-specified file.  The saved pedigree includes
    # all fields recognized by PyPedal, not just the original fields read from the input pedigree
    # file.
    # @param filename The file to which the pedigree should be written.
    # @param outformat The format in which the pedigree should be written: 'o' for original (as read) and 'l' for long version (all available variables).
    # @param idformat Write 'o' (original) or 'r' (renumbered) animal, sire, and dam IDs.
    # @return A save status indicator (0: failed, 1: success)
    # @defreturn integer
    def save(self,filename='',outformat='o',idformat='o'):
        #
        # This is VERY important: never overwrite the user's data if it looks like an accidental
        # request!  If the user does not pass a filename to save() save the pedigree to a file
        # whose name is derived from, but not the same as, the original pedigree file.
        #
        if filename == '':
            filename = '%s_saved.ped' % ( self.kw['filetag'] )
            if self.kw['messages'] == 'verbose':
                print '[WARNING]: Saving pedigree to file %s to avoid overwriting %s.' % ( filename, self.kw['pedfile'] )
            logging.warning('Saving pedigree to file %s to avoid overwriting %s.',filename,self.kw['pedfile'])
        try:
            ofh = file(filename,'w')
            if self.kw['messages'] == 'verbose':
                print '[INFO]: Opened file %s for pedigree save at %s.' % ( filename, pyp_utils.pyp_nice_time() )
            logging.info('Opened file %s for pedigree save at %s.',filename, pyp_utils.pyp_nice_time())

            if outformat == 'l':
                # We have to form the new pedformat.
                _newpedformat = 'asdgx'
                if 'y' in self.kw['pedformat']:
                    _newpedformat = '%sy' % ( _newpedformat )
                else:
                    _newpedformat = '%sb' % ( _newpedformat )
                _newpedformat = '%sfrnle' % (_newpedformat )
            else:
                if self.kw['f_computed']:
                    _newpedformat = '%sf' % ( self.kw['pedformat'] )
                else:
                    _newpedformat = self.kw['pedformat']

            # Write file header.
            ofh.write('# %s created by PyPedal at %s\n' % ( filename, pyp_utils.pyp_nice_time() ) )
            ofh.write('# Current pedigree metadata:\n')
            ofh.write('#\tpedigree file: %s\n' % (filename) )
            ofh.write('#\tpedigree name: %s\n' % (self.kw['pedname']) )
            ofh.write('#\tpedigree format: \'%s\'\n' % ( _newpedformat) )
            if idformat == 'o':
                ofh.write('#\tNOTE: Animal, sire, and dam IDs are RENUMBERED IDs, not original IDs!\n')
            ofh.write('# Original pedigree metadata:\n')
            ofh.write('#\tpedigree file: %s\n' % (self.kw['pedfile']) )
            ofh.write('#\tpedigree name: %s\n' % (self.kw['pedname']) )
            ofh.write('#\tpedigree format: %s\n' % (self.kw['pedformat']) )
            for _a in self.pedigree:
                if idformat == 'o':
                    _outstring = '%s %s %s' % \
                        (_a.originalID, self.pedigree[int(_a.sireID)-1].originalID, \
                        self.pedigree[int(_a.damID)-1].originalID )
                else:
                    _outstring = '%s %s %s' % (_a.animalID, _a.sireID, _a.damID )
                if 'g' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.gen )
                if 'x' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.sex )
                if 'y' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.bd )
                else:
                    _outstring = '%s %s' % ( _outstring, _a.by )
                if 'f' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.fa )
                if 'r' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.breed )
                if 'n' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.name )
                if 'l' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.alive )
                if 'e' in _newpedformat:
                    _outstring = '%s %s' % ( _outstring, _a.age )
                ofh.write( '%s\n' % (_outstring) )
            ofh.close()
            if self.kw['messages'] == 'verbose':
                print '[INFO]: Closed file %s after pedigree save at %s.' % ( filename, pyp_utils.pyp_nice_time() )
            logging.info('Closed file %s after pedigree save at %s.',filename, pyp_utils.pyp_nice_time())
            return 1
        except:
            if self.kw['messages'] == 'verbose':
                print '[ERROR]: Unable to open file %s for pedigree save!' % ( filename )
            logging.error('Unable to open file %s for pedigree save.',filename)
            return 0

    ##
    # preprocess() processes a pedigree file, which includes reading the animals
    # into a list of animal objects, forming lists of sires and dams, and checking for
    # common errors.
    # @param None
    # @return None
    # @defreturn None
    def preprocess(self):
        """Preprocess a pedigree file, which includes reading the animals into a list, forming lists of sires and dams, and checking for common errors."""
        lineCounter = 0     # count the number of lines in the pedigree file
        animalCounter = 0   # count the number of animal records in the pedigree file
        pedformat_codes = ['a','s','d','g','x','b','f','r','n','y','l','e','A','S','D','L','Z']
        critical_count = 0  # Number of critical errors encountered
        pedformat_locations = {} # Stores columns numbers for input data
        _sires = {}         # We need to track the sires and dams read from the pedigree
        _dams = {}          # file in order to insert records for any parents that do not
                            # have their own records in the pedigree file.
        # A variable, 'pedformat, is passed as a parameter that indicates the format of the
        # pedigree in the input file.  Note that A PERIGREE FORMAT STRING IS NO LONGER
        # REQUIRED in the input file, and any found will be ignored.  The index of the single-
        # digit code in the format string indicates the column in which the corresponding
        # variable is found.  Duplicate values in the pedformat atring are ignored.
        if not self.kw['pedformat']:
            self.kw['pedformat'] = 'asd'
            logging.error('Null pedigree format string assigned a default value.')
            if self.kw['messages'] == 'verbose':
                print '[ERROR]: Null pedigree format string assigned a default value.'
        # This is where we check the format string to figure out what we have in the input file.
        # Check for valid characters...
        _pedformat = []
        for _char in self.kw['pedformat']:
            if _char in pedformat_codes and _char != 'Z':
                _pedformat.append(_char)
            elif _char in pedformat_codes and _char == 'Z':
                _pedformat.append('.')
                if self.kw['messages'] == 'verbose':
                    print '[INFO]: Skipping one or more columns in the input file'
                logging.info('Skipping one or more columns in the input file as requested by the pedigree format string %s',self.kw['pedformat'])
            else:
                # Replace the invalid code with a period, which is ignored when the string is parsed.
                _pedformat.append('.')
                if self.kw['messages'] == 'verbose':
                    print '[DEBUG]: Invalid format code, %s, encountered!' % (_char)
                logging.error('Invalid column format code %s found while reading pedigree format string %s',_char,self.kw['pedformat'])
        for _char in _pedformat:
            try:
                pedformat_locations['animal'] = _pedformat.index('a')
            except ValueError:
                try:
                    pedformat_locations['animal'] = _pedformat.index('A')
                except ValueError:
                    print '[CRITICAL]: No animal identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)
                    critical_count = critical_count + 1
            try:
                pedformat_locations['sire'] = _pedformat.index('s')
            except ValueError:
                try:
                    pedformat_locations['sire'] = _pedformat.index('S')
                except ValueError:
                    print '[CRITICAL]: No sire identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)
                    critical_count = critical_count + 1
            try:
                pedformat_locations['dam'] = _pedformat.index('d')
            except ValueError:
                try:
                    pedformat_locations['dam'] = _pedformat.index('D')
                except ValueError:
                    print '[CRITICAL]: No dam identification code was specified in the pedigree format string %s!  This is a critical error and the program will halt.' % (_pedformat)
                    critical_count = critical_count + 1
            try:
                pedformat_locations['generation'] = _pedformat.index('g')
            except ValueError:
                pedformat_locations['generation'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No generation code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['sex'] = _pedformat.index('x')
            except ValueError:
                pedformat_locations['sex'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No sex code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['birthyear'] = _pedformat.index('b')
            except ValueError:
                pedformat_locations['birthyear'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No birth date (YYYY) code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['inbreeding'] = _pedformat.index('f')
            except ValueError:
                pedformat_locations['inbreeding'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No coeffcient of inbreeding code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['breed'] = _pedformat.index('r')
            except ValueError:
                pedformat_locations['breed'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No breed code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['name'] = _pedformat.index('n')
            except ValueError:
                pedformat_locations['name'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No name code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['birthdate'] = _pedformat.index('y')
            except ValueError:
                pedformat_locations['birthdate'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No birth date (MMDDYYYY) code was specified in the pedigree format string %s.  This program will continue.' % ( self.kw['pedformat'] )
            try:
                pedformat_locations['alive'] = _pedformat.index('l')
            except ValueError:
                pedformat_locations['alive'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No alive/dead code was specified in the pedigree format string %s.  This program will continue.' % ( self.kw['pedformat'] )
            try:
                pedformat_locations['age'] = _pedformat.index('e')
            except ValueError:
                pedformat_locations['age'] = -999
                if self.kw['messages'] == 'all':
                    print '[DEBUG]: No age code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
            try:
                pedformat_locations['alleles'] = _pedformat.index('L')
                if self.kw['alleles_sepchar'] == self.kw['sepchar']:
                    if self.kw['messages'] == 'all':
                        print '[DEBUG]: The same separating character was specified for both columns of input (option sepchar) and alleles (option alleles_sepchar) in an animal\'s allelotype.  The allelotypes will not be used in this pedigree.'
                    logging.warning('The same separating character was specified for both columns of input (option sepchar) and alleles (option alleles_sepchar) in an animal\'s allelotype.  The allelotypes will not be used in this pedigree.')
                    pedformat_locations['alleles'] = -999
            except ValueError:
                    pedformat_locations['alleles'] = -999
                    if self.kw['messages'] == 'all':
                        print '[DEBUG]: No alleles code was specified in the pedigree format string %s.  This program will continue.' % (self.kw['pedformat'])
        if critical_count > 0:
            sys.exit(0)
        else:
            if self.kw['messages'] == 'verbose':
                print '[INFO]: Opening pedigree file'
            logging.info('Opening pedigree file')
            infile = open(self.kw['pedfile'],'r')
            while 1:
                line = infile.readline()
                #print line
                if not line:
                    logging.warning('Reached end-of-line in %s after reading %s lines.', self.kw['pedfile'],lineCounter)
                    break
                else:
                    # 29 March 2005
                    # This causes problems b/c it eats the last column of the last record in a pedigree
                    # file.  I think I added it way back when to deal with some EOL-character annoyance,
                    # but I am not sure.  So...I am turning it off (for now).
                    #line = string.strip(line[:-1])
                    lineCounter = lineCounter + 1
                    if lineCounter <= self.kw['log_ped_lines']:
                        logging.info('Pedigree (line %s): %s',lineCounter,string.strip(line))
                    if line[0] == '#':
                        logging.info('Pedigree comment (line %s): %s',lineCounter,string.strip(line))
                        pass
                    elif line[0] == '%':
                        self.kw['old_pedformat'] = string.strip(line[1:]) # this lets us specify the format of the pedigree file
                        logging.warning('Encountered deprecated pedigree format string (%s) on line %s of the pedigree file.',line,lineCounter)
                    # Thomas von Hassel sent me a pedigree whose last line was blank but for a tab.  In
                    # debugging that problem I realized that there was no check for null lines.  This 'elif'
                    # catches blank lines so that they are not treated as actuall records and logs them.
                    elif len(string.strip(line)) == 0:
                        logging.warning('Encountered an empty (blank) record on line %s of the pedigree file.',lineCounter)
                    else:
                        animalCounter = animalCounter + 1
                        if numarray.fmod(animalCounter,self.kw['counter']) == 0:
                            logging.info('Records read: %s ',animalCounter)
                        l = string.split(line,self.kw['sepchar'])
                        # I am adding in a check here to make sure that the number of fields
                        # expected from the pedigree format string and the number of fields in
                        # the datalines of the pedigree are the same.  If they are not, there is
                        # a problem that the user needs to handle.
                        if len(self.kw['pedformat']) == len(l):
                            #print line
                            #print l
                            # Some people *cough* Brad Heins *cough* insist on sending me pedigree
                            # files vomited out by Excel, which pads cells in a column with spaces
                            # to right-align them...
                            for i in range(len(l)):
                                l[i] = string.strip(l[i])
                            if len(l) < 3:
                                errorString = 'The record on line %s of file %s is too short - all records must contain animal, sire, and dam ID numbers (%s fields detected).\n' % (lineCounter,self.kw['pedfile'],len(l))
                                print '[ERROR]: %s' % (errorString)
                                print '[ERROR]: %s' % (line)
                                sys.exit(0)
                            else:
                                an = NewAnimal(pedformat_locations,l,self.kw)
                                if int(an.sireID) != 0:
                                    _sires[an.sireID] = an.sireID
                                if int(an.damID) != 0:
                                    _dams[an.damID] = an.damID
                                self.pedigree.append(an)
                                self.idmap[an.animalID] = an.animalID
                                self.backmap[an.animalID] = an.animalID
                        else:
                            errorString = 'The record on line %s of file %s does not have the same number of columns (%s) as the pedigree format string (%s) says that it should (%s). Please check your pedigree file and the pedigree format string for errors.\n' % ( lineCounter, self.kw['pedfile'], len(l), \
                            self.kw['pedformat'], len(self.kw['pedformat']) )
                            print '[ERROR]: %s' % (errorString)
                            logging.error(errorString)
                            sys.exit(0)
            #
            # This is where we deal with parents with no pedigree file entry.
            #
            _null_locations = pedformat_locations
            for _n in _null_locations.keys():
                _null_locations[_n] = -999
            _null_locations['animal'] = 0
            _null_locations['sire'] = 1
            _null_locations['dam'] = 2
#            print _null_locations
#            print 'INFO: _sires = %s' % (_sires)
#            print 'INFO: _dam = %s' % (_dams)
            for _s in _sires.keys():
                try:
                    _i = self.idmap[_s]
                except KeyError:
                    an = NewAnimal(_null_locations,[_s,'0','0'],self.kw)
#                    an.printme()
                    self.pedigree.append(an)
                    self.idmap[an.animalID] = an.animalID
                    self.backmap[an.animalID] = an.animalID
                    logging.info('Added pedigree entry for sire %s' % (_s))
            for _d in _dams.keys():
                try:
                    _i = self.idmap[_d]
                except KeyError:
                    an = NewAnimal(_null_locations,[_d,'0','0'],self.kw)
#                    an.printme()
                    self.pedigree.append(an)
                    self.idmap[an.animalID] = an.animalID
                    self.backmap[an.animalID] = an.animalID
                    logging.info('Added pedigree entry for dam %s' % (_d))
            #
            # Finish up.
            #
            logging.info('Closing pedigree file')
            infile.close()

    ##
    # renumber() updates the ID map after a pedigree has been renumbered so that all references
    # are to renumbered rather than original IDs.
    # @param None
    # @return None
    # @defreturn None
    def renumber(self):
        if self.kw['messages'] == 'verbose':
            print '\t[INFO]: Renumbering pedigree at %s' % ( pyp_utils.pyp_nice_time() )
            print '\t\t[INFO]: Reordering pedigree at %s' % ( pyp_utils.pyp_nice_time() )
        logging.info('Reordering pedigree')
        if 'b' in self.kw['pedformat'] or 'y' in self.kw['pedformat'] and not self.kw['slow_reorder']:
            self.pedigree = pyp_utils.fast_reorder(self.pedigree)
        else:
            self.pedigree = pyp_utils.reorder(self.pedigree)
        if self.kw['messages'] == 'verbose':
            print '\t\t[INFO]: Renumbering at %s' % ( pyp_utils.pyp_nice_time() )
        logging.info('Renumbering pedigree')
        self.pedigree = pyp_utils.renumber(self.pedigree)
        if self.kw['messages'] == 'verbose':
            print '\t\t[INFO]: Updating ID map at %s' % ( pyp_utils.pyp_nice_time() )
        logging.info('Updating ID map')
        self.updateidmap()
        if self.kw['messages'] == 'verbose':
            print '\t[INFO]: Assigning offspring at %s' % ( pyp_utils.pyp_nice_time() )
        logging.info('Assigning offspring')
        pyp_utils.assign_offspring(self)
        self.kw['pedigree_is_renumbered'] = 1
        self.kw['assign_offspring'] = 1


    ##
    # updateidmap() updates the ID map after a pedigree has been renumbered so that all references
    # are to renumbered rather than original IDs.
    # @param None
    # @return None
    # @defreturn None
    def updateidmap(self):
        self.idmap = {}
        self.backmap = {}
        for _a in self.pedigree:
            try:
                self.idmap[_a.originalID] = _a.animalID
                self.backmap[_a.renumberedID] = _a.originalID
                #print '%s => %s' % ( _a.renumberedID, self.backmap[_a.renumberedID] )
            except KeyError:
                 pass
#         print self.idmap
#         print self.backmap

##
# The NewAnimal() class is holds animals records read from a pedigree file.
class NewAnimal:
    """A simple class to hold animals records read from a pedigree file."""
    ##
    # __init__() initializes a NewAnimal() object.
    # @param locations A dictionary containing the locations of variables in the input line.
    # @param data The line of input read from the pedigree file.
    # @return An instance of a NewAnimal() object populated with data
    # @defreturn object
    def __init__(self,locations,data,mykw):
        """Initialize an animal record."""
#         print locations
#         print data
        if locations['animal'] != -999:
            # If the animal's ID is actually a string, we need to be clever.  Put a copy of
            # the string in the 'Name' field.  Then use the hash function to convert the ID
            # to an integer.
            if 'A' in mykw['pedformat']:
                #print string.strip(data[locations['animal']])
                self.name = string.strip(data[locations['animal']])
                self.animalID = self.string_to_int(data[locations['animal']])
                self.originalID = self.string_to_int(data[locations['animal']])
            else:
                self.animalID = string.strip(data[locations['animal']])
                self.originalID = string.strip(data[locations['animal']])
        if locations['sire'] != -999 and string.strip(data[locations['sire']]) != mykw['missing_parent']:
            if 'S' in mykw['pedformat']:
                self.sireID = self.string_to_int(data[locations['sire']])
            else:
                self.sireID = string.strip(data[locations['sire']])
        else:
            self.sireID = '0'
        if locations['dam'] != -999 and string.strip(data[locations['dam']]) != mykw['missing_parent']:
            if 'D' in mykw['pedformat']:
                self.damID = self.string_to_int(data[locations['dam']])
            else:
                self.damID = string.strip(data[locations['dam']])
        else:
            self.damID = '0'
        if locations['generation'] != -999:
            self.gen = data[locations['generation']]
        else:
            self.gen = -999
        if locations['sex'] != -999:
            self.sex = string.strip(data[locations['sex']])
        else:
            self.sex = 'u'
        if locations['birthdate'] != -999:
            self.bd = string.strip(data[locations['birthdate']])
        else:
            self.bd = '01011900'
        if locations['birthyear'] != -999:
            #print locations['birthyear']
            #print data
            self.by = int(string.strip(data[locations['birthyear']]))
            if self.by == 0:
                self.by = 1900
            #print self.animalID, self.by
            #print self.animalID, data
        elif locations['birthyear'] == -999 and locations['birthdate'] != -999:
            self.by = int(string.strip(data[locations['birthdate']]))
            self.by = self.by[:4]
        else:
#             if self.sireID == '0' and self.damID == '0':
#                 self.by = 1900
#             else:
#                 self.by = 1901
            self.by = 1900
        if locations['inbreeding'] != -999:
            self.fa = float(string.strip(data[locations['inbreeding']]))
        else:
            self.fa = 0.
        if locations['name'] != -999:
            self.name = string.strip(data[locations['name']])
        else:
            if 'A' not in mykw['pedformat']:
                self.name = 'Unknown'
        if locations['breed'] != -999:
            self.breed = string.strip(data[locations['breed']])
        else:
            self.breed = 'Unknown'
        if locations['age'] != -999:
            self.age = int(string.strip(data[locations['age']]))
        else:
            self.age = -999
        if locations['alive'] != -999:
            self.alive = int(string.strip(data[locations['alive']]))
        else:
            self.alive = 0
        self.renumberedID = -999
        self.igen = -999
        if self.sireID == '0' and self.damID == '0':
            self.founder = 'y'
        else:
            self.founder = 'n'
        self.paddedID = self.pad_id()
        #print self.animalID, self.paddedID
        self.ancestor = 0
        self.sons = {}
        self.daus = {}
        self.unks = {}
        # Assign alleles for use in gene-dropping runs.  Automatically assign two
        # distinct alleles to founders.
        if locations['alleles'] != -999:
            self.alleles = [string.split(data[locations['alleles']], self.kw['alleles_sepchar'])[0], \
                string.split(data[locations['alleles']],self.kw['alleles_sepchar'])[1]]
        else:
            if self.founder == 'y':
                _allele_1 = '%s%s' % (self.paddedID,'__1')
                _allele_2 = '%s%s' % (self.paddedID,'__2')
                self.alleles = [_allele_1,_allele_2]
            else:
                self.alleles = ['','']
        self.pedcomp = -999.9

    ##
    # printme() prints a summary of the data stored in the Animal() object.
    # @param self Reference to the current Animal() object
    def printme(self):
        """Print the contents of an animal record - used for debugging."""
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
        """Take an Animal ID, pad it to fifteen digits, and prepend the birthyear (or 1900 if the birth year is unknown)"""
        l = len(self.animalID)
        pl = 15 - l - 1
        if pl > 0:
            zs = '0'*pl
            pid = '%s%s%s%s' % (self.by,zs,self.animalID,l)
        else:
            pid = '%s%s%s' % (self.by,self.animalID,l)
        return pid

    ##
    # string_to_int() takes an Animal/Sire/Dam ID as a string and returns a string that can be represented as an
    # integer by replacing each character in the string with its corresponding ASCII table value.
    def string_to_int(self,idstring):
        """Convert a string to an integer by converting each character in the string to its corresponding ASCII code."""
        idint = ''
        for _i in idstring:
            idint = '%s%s' % ( idint, ord(_i) )
        return idint

##
# The PedigreeMetadata() class stores metadata about pedigrees.  Hopefully this will help improve performance in some procedures,
# as well as provide some useful summary data.
class PedigreeMetadata:
    """A class to hold metadata about pedigrees.  Hopefully this will help improve performance in some procedures, as well as
    provide some useful summary data."""
    ##
    # __init__() initializes a PedigreeMetadata object.
    # @param self Reference to the current Pedigree() object
    # @param myped A PyPedal pedigree.
    # @param kw A dictionary of options.
    # @return An instance of a Pedigree() object populated with data
    # @defreturn object
    def __init__(self,myped,kw):
        """Initialize a pedigree record."""
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Instantiating a new PedigreeMetadata() object...'
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Naming the Pedigree()...'
        self.name = kw['pedname']
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Assigning a filename...'
        self.filename = kw['pedfile']
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Attaching a pedigree...'
        self.myped = myped
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Setting the pedcode...'
        self.pedcode = kw['pedformat']
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Counting the number of animals in the pedigree...'
        self.num_records = len(self.myped)
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Counting and finding unique sires...'
        self.num_unique_sires, self.unique_sire_list = self.nus()
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Counting and finding unique dams...'
        self.num_unique_dams, self.unique_dam_list = self.nud()
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Setting renumber flag...'
        self.renumbered = kw['renumber']
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Counting and finding unique generations...'
        self.num_unique_gens, self.unique_gen_list = self.nug()
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Counting and finding unique birthyears...'
        self.num_unique_years, self.unique_year_list = self.nuy()
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Counting and finding unique founders...'
        self.num_unique_founders, self.unique_founder_list = self.nuf()
        if kw['messages'] == 'verbose':
            print '\t[INFO]:  Detaching pedigree...'
        self.myped = []
    ##
    # printme() prints a summary of the metadata stored in the Pedigree() object.
    # @param self Reference to the current Pedigree() object
    def printme(self):
        """Print the pedigree metadata."""
        print 'Metadata for  %s (%s)' % (self.name,self.filename)
        print '\tRecords:\t\t%s' % (self.num_records)
        print '\tUnique Sires:\t\t%s' % (self.num_unique_sires)
        #print '\tSires:\t\t%s' % (self.unique_sire_list)
        print '\tUnique Dams:\t\t%s' % (self.num_unique_dams)
        #print '\tDams:\t\t%s' % (self.unique_dam_list)
        print '\tUnique Gens:\t\t%s' % (self.num_unique_gens)
        #print '\tGenerations:\t\t%s' % (self.unique_gen_list)
        print '\tUnique Years:\t\t%s' % (self.num_unique_years)
        #print '\tYear:\t\t%s' % (self.unique_year_list)
        print '\tUnique Founders:\t%s' % (self.num_unique_founders)
        #print '\tFounders:\t\t%s' % (self.unique_founder_list)
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
        line = '='*60+'\n'
        aout.write('%s\n' % line)
        aout.write('PEDIGREE %s (%s)\n' % self.name,self.filename)
        aout.write('\tRecords:\t%s\n' % self.num_records)
        aout.write('\tUnique Sires:\t%s\n' % self.num_unique_sires)
        aout.write('\tUnique Dams:\t%s\n' % self.num_unique_dams)
        aout.write('\tPedigree Code:\t%s\n' % self.pedcode)
        aout.write('\tUnique Founders:\t%s\n' % self.num_unique_founders)
        aout.write('\tUnique Gens:\t%s\n' % self.num_unique_gens)
        aout.write('\tUnique Years:\t%s\n' % self.num_unique_years)
        aout.write('%s\n' % line)
        aout.write('\tUnique Sire List:\t%s\n' % self.unique_sire_list)
        aout.write('\tUnique Dam List:\t%s\n' % self.unique_dam_list)
        aout.write('\tUnique Gen List:\t%s\n' % self.unique_gen_list)
        aout.write('\tUnique Year List:\t%s\n' % self.unique_year_list)
        aout.write('\tUnique Founder List:\t%s\n' % self.num_founder_list)
        aout.write('%s\n' % line)
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
                    _f = founderdict[self.myped[l].originalID]
                except KeyError:
                    founderdict[self.myped[l].originalID] = self.myped[l].originalID
        n = len(founderdict.keys())
        return n, founderdict.keys()

##
# NewAMatrix provides an instance of a numerator relationship matrix as a Numarray array of
# floats with some convenience methods.  The idea here is to provide a wrapper around a NRM
# so that it is easier to work with.  For large pedigrees it can take a long time to compute
# the elements of A, so there is real value in providing an easy way to save and retrieve a
# NRM once it has been formed.
class NewAMatrix:
    def __init__(self,kw):
        """Initialize a new numerator relationship matrix."""
        if not kw.has_key('messages'): kw['messages'] = 'verbose'
        if not kw.has_key('nrm_method'): kw['method'] = 'nrm'
        self.kw = kw

    ##
    # form_a_matrix() calls pyp_nrm/fast_a_matrix() or pyp_nrm/fast_a_matrix_r()
    # to form a NRM from a pedigree.
    # @param pedigree The pedigree used to form the NRM.
    # @return A NRM on success, 0 on failure.
    # @defreturn integer
    def form_a_matrix(self,pedigree):
        if self.kw['nrm_method'] not in ['nrm','frm']:
            self.kw['nrm_method'] = 'nrm'
        if self.kw['messages'] == 'verbose':
            print '[INFO]: Forming A-matrix from pedigree at %s.' % ( pyp_utils.pyp_nice_time() )
        logging.info('Forming A-matrix from pedigree')
        # Try and form the NRM where COI are not adjusted for the inbreeding
        # of parents.
        if self.kw['nrm_method'] == 'nrm':
            try:
                self.nrm = pyp_nrm.fast_a_matrix(pedigree,self.kw)
                if self.kw['messages'] == 'verbose':
                    print '[INFO]: Formed A-matrix from pedigree using pyp_nrm.fast_a_matrix() at %s.' % ( pyp_utils.pyp_nice_time() )
                logging.info('Formed A-matrix from pedigree using pyp_nrm.fast_a_matrix()')
            except:
                if self.kw['messages'] == 'verbose':
                    print '[ERROR]: Unable to form A-matrix from pedigree using pyp_nrm.fast_a_matrix() at %s.' % ( pyp_utils.pyp_nice_time() )
                logging.error('Unable to form A-matrix from pedigree using pyp_nrm.fast_a_matrix()')
                return 0
        # Otherwise try and form the NRM where COI are adjusted for the inbreeding
        # of parents.
        else:
            try:
                self.nrm = pyp_nrm.fast_a_matrix_r(pedigree)
                if self.kw['messages'] == 'verbose':
                    print '[INFO]: Formed A-matrix from pedigree using pyp_nrm.fast_a_matrix_r() at %s.' % ( pyp_utils.pyp_nice_time() )
                logging.info('Formed A-matrix from pedigree using pyp_nrm.fast_a_matrix_r()')
            except:
                if self.kw['messages'] == 'verbose':
                    print '[ERROR]: Unable to form A-matrix from pedigree using pyp_nrm.fast_a_matrix_r() at %s.' % ( pyp_utils.pyp_nice_time() )
                logging.error('Unable to form A-matrix from pedigree using pyp_nrm.fast_a_matrix_r()')
                return 0

    ##
    # load() uses the Numarray Array Function "fromfile()" to load an array from a
    # binary file.  If the load is successful, self.nrm contains the matrix.
    # @param nrm_filename The file from which the matrix should be read.
    # @return A load status indicator (0: failed, 1: success).
    # @defreturn integer
    def load(self,nrm_filename):
        import math
        if self.kw['messages'] == 'verbose':
            print '[INFO]: Loading A-matrix from file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
        logging.info('Loading A-matrix from file %s', nrm_filename)
        try:
            self.nrm = numarray.fromfile(nrm_filename,'Float64')
    #         print self.nrm.shape
    #         print self.nrm.shape[0]
    #         print int(math.sqrt(self.nrm.shape[0]))
            self.nrm = numarray.reshape( self.nrm, ( int(math.sqrt(self.nrm.shape[0])), int(math.sqrt(self.nrm.shape[0])) ) )
            if self.kw['messages'] == 'verbose':
                print '[INFO]: A-matrix successfully loaded from file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
            logging.info('A-matrix successfully loaded from file %s', nrm_filename)
            return 1
        except:
            if self.kw['messages'] == 'verbose':
                print '[ERROR]: Unable to load A-matrix from file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
            logging.error('Unable to load A-matrix from file %s', nrm_filename)
            return 0

    ##
    # save() uses the Numarray method "tofile()" to save an array to a binary file.
    # @param nrm_filename The file to which the matrix should be written.
    # @return A save status indicator (0: failed, 1: success).
    # @defreturn integer
    def save(self,nrm_filename):
        if self.kw['messages'] == 'verbose':
            print '[INFO]: Saving A-matrix to file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
        logging.info('Saving A-matrix to file %s', nrm_filename)
#         try:
        self.nrm.tofile(nrm_filename)
        if self.kw['messages'] == 'verbose':
            print '[INFO]: A-matrix successfully saved to file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
        logging.info('A-matrix successfully saved to file %s', nrm_filename)
#             return 1
#         except:
#             if self.kw['messages'] == 'verbose':
#                 print '[ERROR]: Unable to save A-matrix to file %s at %s.' % ( nrm_filename, pyp_utils.pyp_nice_time() )
#             logging.error('Unable to save A-matrix to file %s', nrm_filename)
#             return 0

    ##
    # info() uses the info() method of Numarray arrays to dump some information about
    # the NRM.  This is of use predominantly for debugging.
    # @param None
    # @return None
    # @defreturn None
    def info(self):
        try:
            self.nrm.info()
        except:
            pass
