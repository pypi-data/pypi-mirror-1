#!/usr/bin/python

###############################################################################
# NAME: pyp_io.py
# VERSION: 2.0.0a17 (19MAY2005)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#	a_inverse_from_file()
#	a_inverse_to_file()
#   dissertation_pedigree_to_file()
#   dissertation_pedigree_to_pedig_format()
#   dissertation_pedigree_to_pedig_interest_format()
#   dissertation_pedigree_to_pedig_format_mask()
#   pyp_file_header()
#   pyp_file_footer()
#	renderTitle()
#	renderBodyText()
###############################################################################

##
# pyp_io contains several procedures for writing structures to and reading them from
# disc (e.g. using pickle() to store and retrieve A and A-inverse).  It also includes a set
# of functions used to render strings as HTML or plaintext for use in generating output
# files.
##

import string
from time import *
from numarray import *
import pyp_utils

##
# a_inverse_to_file() uses the Python pickle system for persistent objects to write the
# inverse of a relationship matrix to a file.
# @param pedobj A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
def a_inverse_to_file(pedobj,ainv=''):
    """Use the Python pickle system for persistent objects to write the inverse of a relationship matrix to a file."""
    from pickle import Pickler
    if not ainv:
        ainv = a_inverse_df(pedobj.pedigree,pedobj.kw['filetag'])
    a_outputfile = '%s%s%s' % (filetag,'_a_inverse_pickled_','.pkl')
    aout = open(a_outputfile,'w')
    ap = pickle.Pickler(aout)
    ap.dump(a)
    aout.close()

##
# a_inverse_from_file() uses the Python pickle system for persistent objects to read the inverse of
# a relationship matrix from a file.
# @param inputfile The name of the input file.
# @return The inverse of a numerator relationship matrix.
# @defreturn matrix
def a_inverse_from_file(inputfile):
    """Use the Python pickle system for persistent objects to read the inverse of a relationship matrix from a file."""
    from pickle import Pickler
    ain = open(inputfile,'r')
    au = pickle.Unpickler(ain)
    a_inv = au.load()
    return a_inv

##
# dissertation_pedigree_to_file() takes a pedigree in 'asdxfg' format and writes is to a file.
# @param pedobj A PyPedal pedigree object.
def dissertation_pedigree_to_file(pedobj):
    # This procedure assumes that the pedigree passed to it is in 'asdxfg' format.
    length = len(pedobj.pedigree)
    #print 'DEBUG: length of pedigree is %s' % (length)
    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_diss','.ped')
    print '\t\tWriting dissertation pedigree to %s' % (outputfile)
    aout = open(outputfile,'w')
    aout.write('# DISSERTATION pedigree produced by PyPedal.\n')
    aout.write('% asdbxfg\n')
    for l in range(length):
        line = '%s,%s,%s,%s,%s,%s,%s\n' % (pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,pedobj.pedigree[l].by,
            pedobj.pedigree[l].sex,pedobj.pedigree[l].fa,pedobj.pedigree[l].gen)
        aout.write(line)
        # print line
    aout.close()

##
# dissertation_pedigree_to_pedig_format() takes a pedigree in 'asdbxfg' format, formats it into
# the form used by Didier Boichard's 'pedig' suite of programs, and writes it to a file.
# @param pedobj A PyPedal pedigree object.
def dissertation_pedigree_to_pedig_format(pedobj):
    # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
    # Boichard's 'pedig' suite of programs, and writes them to a file.
    length = len(pedobj.pedigree)
    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_pedig','.ped')
    aout = open(outputfile,'w')
    for l in range(length):
        if pedobj.pedigree[l].sex == 'm' or pedobj.pedigree[l].sex == 'M':
                sex = 1
        else:
            sex = 2
        line = '%s %s %s %s %s %s %s\n' % (pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,pedobj.pedigree[l].by,
            sex,'1','1')
        aout.write(line)
    aout.close()

##
# dissertation_pedigree_to_pedig_interest_format() takes a pedigree in 'asdbxfg' format,
# formats it into the form used by Didier Boichard's parente program for the studied
# individuals file.
# @param pedobj A PyPedal pedigree object.
def dissertation_pedigree_to_pedig_interest_format(pedobj):
    # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
    # Boichard's parente program for the studied individuals file
    length = len(pedobj.pedigree)
    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_parente','.ped')
    aout = open(outputfile,'w')
    for l in range(length):
        line = '%s %s\n' % (pedobj.pedigree[l].animalID,'1')
        aout.write(line)
    aout.close()

##
# dissertation_pedigree_to_pedig_format_mask() Takes a pedigree in 'asdbxfg' format,
# formats it into the form used by Didier Boichard's 'pedig' suite of programs, and
# writes it to a file.  THIS FUNCTION MASKS THE GENERATION ID WITH A FAKE BIRTH YEAR
# AND WRITES THE FAKE BIRTH YEAR TO THE FILE INSTEAD OF THE TRUE BIRTH YEAR.  THIS IS
# AN ATTEMPT TO FOOL PEDIG TO GET f_e, f_a et al. BY GENERATION.
# @param pedobj A PyPedal pedigree object.
def dissertation_pedigree_to_pedig_format_mask(pedobj):
        # Takes pedigrees in 'asdbxfg' format, formats them into the form used by Didier
        # Boichard's 'pedig' suite of programs, and writes them to a file.
        #
        # THIS FUNCTION MASKS THE GENERATION ID WITH A FAKE BIRTH YEAR AND WRITES
        # THE FAKE BIRTH YEAR TO THE FILE INSTEAD OF THE TRUE BIRTH YEAR.  THIS IS
        # AN ATTEMPT TO FOOL PEDIG TO GET f_e, f_a et al. BY GENERATION.
        #import string
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
            line = '%s %s %s %s %s %s %s\n' % (pedobj.pedigree[l].animalID,pedobj.pedigree[l].sireID,pedobj.pedigree[l].damID,_maskgen,sex,'1','1')
            aout.write(line)
        aout.close()

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