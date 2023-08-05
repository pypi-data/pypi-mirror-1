#!/usr/bin/python

###############################################################################
# NAME: pyp_io.py
# VERSION: 2.0.0a19 (22AUGUST2005)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   a_inverse_from_file()
#   a_inverse_to_file()
#   dissertation_pedigree_to_file()
#   dissertation_pedigree_to_pedig_format()
#   dissertation_pedigree_to_pedig_interest_format()
#   dissertation_pedigree_to_pedig_format_mask()
#   pyp_file_header()
#   pyp_file_footer()
#   renderTitle()
#   renderBodyText()
#   pickle_pedigree()
#   unpickle_pedigree()
#   summary_inbreeding()
###############################################################################

##
# pyp_io contains several procedures for writing structures to and reading them from
# disc (e.g. using pickle() to store and retrieve A and A-inverse).  It also includes a set
# of functions used to render strings as HTML or plaintext for use in generating output
# files.
##

import logging, numarray, pickle, string, time
import pyp_utils

global LINE1
global LINE2
LINE1 = '%s' % ('='*80)
LINE2 = '%s' % ('-'*80)

##
# a_inverse_to_file() uses the Python pickle system for persistent objects to write the
# inverse of a relationship matrix to a file.
# @param pedobj A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @return True (1) on success, false (0) on failure
# @defreturn integer
def a_inverse_to_file(pedobj,ainv=''):
    """Use the Python pickle system for persistent objects to write the inverse of a relationship matrix to a file."""
    try: logging.info('Entered a_inverse_to_file()')
    except: pass
    try:
        from pickle import Pickler
        if not ainv:
            ainv = a_inverse_df(pedobj.pedigree,pedobj.kw['filetag'])
        a_outputfile = '%s%s%s' % (filetag,'_a_inverse_pickled_','.pkl')
        aout = open(a_outputfile,'w')
        ap = pickle.Pickler(aout)
        ap.dump(a)
        aout.close()
        _r = 1
    except:
        _r = 0

    try: logging.info('Exited a_inverse_to_file()')
    except: pass
    return _r

##
# a_inverse_from_file() uses the Python pickle system for persistent objects to read the inverse of
# a relationship matrix from a file.
# @param inputfile The name of the input file.
# @return The inverse of a numerator relationship matrix.
# @defreturn matrix
def a_inverse_from_file(inputfile):
    """Use the Python pickle system for persistent objects to read the inverse of a relationship matrix from a file."""
    try: logging.info('Entered a_inverse_from_file()')
    except: pass
    try:
        from pickle import Pickler
        ain = open(inputfile,'r')
        au = pickle.Unpickler(ain)
        a_inv = au.load()
    except:
        a_inv = numarray.zeros([1,1],Float)
    try: logging.info('Exited a_inverse_from_file()')
    except: pass
    return a_inv

##
# dissertation_pedigree_to_file() takes a pedigree in 'asdxfg' format and writes is to a file.
# @param pedobj A PyPedal pedigree object.
# @return True (1) on success, false (0) on failure
# @defreturn integer
def dissertation_pedigree_to_file(pedobj):
    # This procedure assumes that the pedigree passed to it is in 'asdxfg' format.
    try: logging.info('Entered dissertation_pedigree_to_file()')
    except: pass
    try:
        length = len(pedobj.pedigree)
        #print 'DEBUG: length of pedigree is %s' % (length)
        outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_diss','.ped')
        print '\t\tWriting dissertation pedigree to %s' % (outputfile)
        aout = open(outputfile,'w')
        aout.write('# DISSERTATION pedigree produced by PyPedal.\n')
        aout.write('% asdbxfg\n')
        for l in range(length):
            aout.write('%s,%s,%s,%s,%s,%s,%s\n' % pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,pedobj.pedigree[l].by, pedobj.pedigree[l].sex,pedobj.pedigree[l].fa,pedobj.pedigree[l].gen)
        aout.close()
        _r = 1
    except:
        _r = 0
    try: logging.info('Exited dissertation_pedigree_to_file()')
    except: pass
    return _r

##
# dissertation_pedigree_to_pedig_format() takes a pedigree in 'asdbxfg' format, formats it into
# the form used by Didier Boichard's 'pedig' suite of programs, and writes it to a file.
# @param pedobj A PyPedal pedigree object.
# @return True (1) on success, false (0) on failure
# @defreturn integer
def dissertation_pedigree_to_pedig_format(pedobj):
    # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
    # Boichard's 'pedig' suite of programs, and writes them to a file.
    try: logging.info('Entered dissertation_pedigree_to_pedig_format()')
    except: pass
    try:
        length = len(pedobj.pedigree)
        outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_pedig','.ped')
        aout = open(outputfile,'w')
        for l in range(length):
            if pedobj.pedigree[l].sex == 'm' or pedobj.pedigree[l].sex == 'M':
                    sex = 1
            else:
                sex = 2
            aout.write('%s %s %s %s %s %s %s\n' % pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,pedobj.pedigree[l].by,sex,'1','1')
        aout.close()
        _r = 1
    except:
        _r = 0
    try: logging.info('Exited dissertation_pedigree_to_pedig_format()')
    except: pass
    return _r

##
# dissertation_pedigree_to_pedig_interest_format() takes a pedigree in 'asdbxfg' format,
# formats it into the form used by Didier Boichard's parente program for the studied
# individuals file.
# @param pedobj A PyPedal pedigree object.
# @return True (1) on success, false (0) on failure
# @defreturn integer
def dissertation_pedigree_to_pedig_interest_format(pedobj):
    # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
    # Boichard's parente program for the studied individuals file
    try: logging.info('Entered dissertation_pedigree_to_pedig_interest_format()')
    except: pass
    try:
        length = len(pedobj.pedigree)
        outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_parente','.ped')
        aout = open(outputfile,'w')
        for l in range(length):
            aout.write('%s %s\n' % pedobj.pedigree[l].animalID,'1')
        aout.close()
        _r = 1
    except:
        _r = 0
    try: logging.info('Exited dissertation_pedigree_to_pedig_interest_format()')
    except: pass
    return _r

##
# dissertation_pedigree_to_pedig_format_mask() Takes a pedigree in 'asdbxfg' format,
# formats it into the form used by Didier Boichard's 'pedig' suite of programs, and
# writes it to a file.  THIS FUNCTION MASKS THE GENERATION ID WITH A FAKE BIRTH YEAR
# AND WRITES THE FAKE BIRTH YEAR TO THE FILE INSTEAD OF THE TRUE BIRTH YEAR.  THIS IS
# AN ATTEMPT TO FOOL PEDIG TO GET f_e, f_a et al. BY GENERATION.
# @param pedobj A PyPedal pedigree object.
# @return True (1) on success, false (0) on failure
# @defreturn integer
def dissertation_pedigree_to_pedig_format_mask(pedobj):
    # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
    # Boichard's 'pedig' suite of programs, and writes them to a file.
    #
    # THIS FUNCTION MASKS THE GENERATION ID WITH A FAKE BIRTH YEAR AND WRITES
    # THE FAKE BIRTH YEAR TO THE FILE INSTEAD OF THE TRUE BIRTH YEAR.  THIS IS
    # AN ATTEMPT TO FOOL PEDIG TO GET f_e, f_a et al. BY GENERATION.
    try: logging.info('Entered dissertation_pedigree_to_pedig_format_mask()')
    except: pass
    try:
        length = len(pedobj.pedigree)
        outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_pedig_mask','.ped')
        aout = open(outputfile,'w')
        for l in range(length):
            ## mask generations (yes, this could be shorter - but this is easy to debug
            mygen = float(pedobj.pedigree[l].gen)
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
            #print 'DEBUG: pedobj.pedigree[l].gen = %s' % (pedobj.pedigree[l].gen)
            #print 'DEBUG: _maskgen = %d' % (_maskgen)
            ## convert sexes
            if pedobj.pedigree[l].sex == 'm' or pedobj.pedigree[l].sex == 'M':
                sex = 1
            else:
                sex = 2
            #print 'DEBUG: An: %s\tSire: %s\tDam: %s\tGen: %s\tmg: %s' % (pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,pedobj.pedigree[l].gen,_maskgen)
            aout.write('%s %s %s %s %s %s %s\n' % pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,_maskgen,sex,'1','1')
        aout.close()
        _r = 1
    except:
        _r = 0
    try: logging.info('Entered dissertation_pedigree_to_pedig_format_mask()')
    except: pass
    return _r

##
# pyp_file_header()
# @param ofhandle A Python file handle.
# @param caller A string indicating the name of the calling routine.
# @return None
def pyp_file_header(ofhandle,caller="Unknown PyPedal routine"):
    try:
        ofhandle.write('%s\n' % ('-'*80))
        ofhandle.write('Created by %s at %s\n' % (caller,pyp_utils.pyp_nice_time()))
        ofhandle.write('%s\n' % ('-'*80))
    except:
        pass

##
# pyp_file_footer()
# @param ofhandle A Python file handle.
# @param caller A string indicating the name of the calling routine.
# @return None
def pyp_file_footer(ofhandle,caller="Unknown PyPedal routine"):
    try:
        ofhandle.write('%s\n' % ('-'*80))
    except:
        pass

##
# renderTitle() ...  Produced HTML output by default.
def renderTitle(title_string,title_level="1"):
    # If we cannot find the PYPEDAL_OUTPUT_TYPE global
    # then default to HTML as the output format.
    if not PYPEDAL_OUTPUT_TYPE:
        PYPEDAL_OUTPUT_TYPE = 'html'
    # We are trying to keep it simple here.
    if ( not title_level ) or ( title_level < 1 ) or ( title_level > 3 ):
        title_level = 1
    if PYPEDAL_OUTPUT_TYPE == 'h':
        renderedTitle = '<H%s>%s</H%s>\n' % (title_level,title_string,title_level)
    else:
        _underline = '='*len(title_string)
        renderedTitle = '%s\n' % (title_string,_underline)
    return renderedTitle

def renderBodyText(text_string):
    if not PYPEDAL_OUTPUT_TYPE:
        PYPEDAL_OUTPUT_TYPE = 'html'
    if PYPEDAL_OUTPUT_TYPE == 'h':
        renderedBodyText = '<p>%s</p>' % (text_string)
    else:
        renderedBodyText = '%s\n' % (text_string)
    return renderedBodyText

##
# pickle_pedigree() pickles a pedigree.
# @param pedobj An instance of a PyPedal pedigree object.
# @param filename The name of the file to which the pedigree object should be pickled (optional).
# @return A 1 on success, a 0 otherwise.
# @defreturn integer
def pickle_pedigree(pedobj,filename=''):
    try: logging.info('Entered pickle_pedigree()')
    except: pass
#    try:
    _r = 1
    if not filename:
        _pfn = '%s.pkl' % ( pedobj.kw['filetag'] )
    else:
        _pfn = '%s.pkl' % ( filename )
    print _pfn
    pickle.dump(pedobj,open(_pfn,'w'))
    logging.info('Pickled pedigree %s to file %s', pedobj.kw['pedname'], _pfn )
    if pedobj.kw['messages'] == 'verbose':
        print 'Pickled pedigree %s to file %s' % ( pedobj.kw['pedname'], _pfn )
#    except:
#        logging.error('Unable to pickle pedigree %s to file %s', self.kw['pedname'], _pfn )
#        _r = 0
    try: logging.info('Exited pickle_pedigree()')
    except: pass
#    return _r

##
# unpickle_pedigree() reads a pickled pedigree in from a file and returns the unpacked
# pedigree object.
# @param filename The name of the pickle file.
# @return An instance of a NewPedigree object on success, a 0 otherwise.
# @defreturn object
def unpickle_pedigree(filename=''):
    try: logging.info('Entered unpickle_pedigree()')
    except: pass
#    try:
    if not filename:
        logging.error('No filename provided for pedigree unpickling!' )
        _r = 0
    else:
        _ck_pfn = string.split(filename,'.')
        if len(_ck_pfn) == 2:
            _pfn = filename
        else:
            _pfn = '%s.pkl' % ( filename )
            logging.info('No file extension provided for %s.  An extension (.pkl) was added.', filename )
        _myped = pickle.load(open(_pfn))
        logging.info('Unpickled pedigree %s from file %s', _myped.kw['pedname'], _pfn )
        _r = _myped
#    except:
#        logging.error('Unable to unpickle pedigree from file!' )
#        _r = 0
#    try: logging.info('Exited unpickle_pedigree()')
#    except: pass
    return _r

##
# summary_inbreeding() returns a string representation of the data contained in
# the 'metadata' dictionary contained in the output dictionary returned by
# pyp_nrm/pyp_inbreeding().
# @param f_metadata Dictionary of inbreeding metadata.
# @return A string on success, a 0 otherwise.
# @defreturn string
def summary_inbreeding(f_metadata):
    try:
        _summary = ''
        _summary = '%s' % (LINE1)
        _summary = '%s\n%s' % (_summary, 'Inbreeding Statistics')
        _summary = '\n%s\n%s' % (_summary, LINE1)
        _summary = '%s\n%s' % (_summary, 'All animals:')
        _summary = '\n%s\n%s' % (_summary, LINE2)
        for k,v in f_metadata['all'].iteritems():
            _line = '\t%s\t%s' % (k,v)
            _summary = '%s\n%s' % (_summary, _line)
        _summary = '\n%s\n%s' % (_summary, LINE1)
        _summary = '%s\n%s' % (_summary, 'Animals with non-zero CoI:')
        _summary = '\n%s\n%s' % (_summary, LINE2)
        for k,v in f_metadata['nonzero'].iteritems():
            _line = '\t%s\t%s' % (k,v)
            _summary = '%s\n%s' % (_summary, _line)
        _summary = '\n%s\n%s' % (_summary, LINE1)
        return _summary
    except:
        return '0'