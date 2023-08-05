#!/usr/bin/python

###############################################################################
# NAME: pyp_nrm.py
# VERSION: 2.0.0a17 (19MAY2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
################################################################################ FUNCTIONS:
#   a_matrix()
#   fast_a_matrix()
#   fast_a_matrix_r()
#   inbreeding()
#   inbreeding_vanraden()
#   recurse_pedigree()
#   recurse_pedigree_n()
#   recurse_pedigree_onesided()
#   recurse_pedigree_idonly()
#   inbreeding_tabular()
#   a_decompose()
#   form_d_nof()
#   a_inverse_dnf()
#   a_inverse_df()
###############################################################################

##
# pyp_nrm contains several procedures for computing numerator relationship matrices and for
# performing operations on those matrices.  It also contains routines for computing CoI on
# large pedigrees using the recursive method of VanRaden (1992).
##

import copy
import string
import numarray
import pyp_utils

##
# a_matrix() is used to form a numerator relationship matrix from a pedigree.  DEPRECATED.
# use fast_a_matrix() instead.
# @param pedobj A PyPedal pedigree object.
# @param save Flag to indicate whether or not the relationship matrix is written to a file.
# @return The NRM as a numarray matrix.
# @defreturn array
def a_matrix(pedobj,save=0):
    """Form a numerator relationship matrix from a pedigree."""
    l = pedobj.medata.num_recs
    # Grab some array tools
    a = numarray.zeros([l,l],Float)  # initialize a matrix of zeros of appropriate dimension
    for row in range(l):
        for col in range(row,l):
            # cast these b/c items are read from the pedigree file as characters, not integers
            pedobj.pedigree[col].animalID = int(pedobj.pedigree[col].animalID)
            pedobj.pedigree[col].sireID = int(pedobj.pedigree[col].sireID)
            pedobj.pedigree[col].damID = int(pedobj.pedigree[col].damID)
            if pedobj.pedigree[col].sireID == 0 and pedobj.pedigree[col].damID == 0:
                if row == col:
                    # both parents unknown and assumed unrelated
                    a[row,col] = 1.
                else:
                    a[row,col] = 0.
                    a[col,row] = a[row,col]
            elif pedobj.pedigree[col].sireID == 0:
                # sire unknown, dam known
                if row == col:
                    a[row,col] = 1.
                else:
                    a[row,col] = 0.5 * a[row,pedobj.pedigree[col].damID-1]
                    a[col,row] = a[row,col]
            elif pedobj.pedigree[col].damID == 0:
                # sire known, dam unknown
                if row == col:
                    a[row,col] = 1.
                else:
                    a[row,col] = 0.5 * a[row,pedobj.pedigree[col].sireID-1]
                    a[col,row] = a[row,col]
            elif pedobj.pedigree[col].sireID > 0 and pedobj.pedigree[col].damID > 0:
                # both parents known
                if row == col:
                    a[row,col] = 1. + ( 0.5 * a[pedobj.pedigree[col].sireID-1,pedobj.pedigree[col].damID-1] )
                else:
                    intermediate = a[row,pedobj.pedigree[col].sireID-1] + a[row,pedobj.pedigree[col].damID-1]
                    finprod = 0.5 * intermediate
                    a[row,col] = 0.5 * intermediate
                    a[col,row] = a[row,col]
            else:
                print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (pedobj.pedigree[col].sireID,pedobj.pedigree[col].damID,pedobj.pedigree[col].animalID)
                break
    # print a
    if save:
        a_outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_matrix_','.dat')
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

##
# Form a numerator relationship matrix from a pedigree.  fast_a_matrix() is a hacked version of a_matrix()
# modified to try and improve performance.  Lists of animal, sire, and dam IDs are formed and accessed rather
# than myped as it is much faster to access a member of a simple list rather than an attribute of an object in a
# list.  Further note that only the diagonal and upper off-diagonal of A are populated.  This is done to save
# n(n+1) / 2 matrix writes.  For a 1000-element array, this saves 500,500 writes.
# @param pedigree A PyPedal pedigree.
# @param pedopts PyPedal options.
# @param save Flag to indicate whether or not the relationship matrix is written to a file.
# @return The NRM as Numarray matrix.
# @defreturn matrix
def fast_a_matrix(pedigree,pedopts,save=0):
    """Form a numerator relationship matrix from a pedigree.  fast_a_matrix() is a hacked version of a_matrix()
    modified to try and improve performance.  Lists of animal, sire, and dam IDs are formed and accessed rather
    than myped as it is much faster to access a member of a simple list rather than an attribute of an object in a
    list.  Further note that only the diagonal and uppef off diagonal of A are populated.  This is done to save
    n(n+1) / 2 matix writes.  For a 1000-element array, this saves 500,500 writes."""
    animals = []
    sires = []
    dams = []
    _animals = {}
    _sires = {}
    _dams = {}
    l = len(pedigree)
    # print '[DEBUG]: l = %s' % (l)
    # Grab some array tools
    a = numarray.zeros([l,l],'Float')  # initialize a matrix of zeros of appropriate dimension
    if pedopts['debug_messages'] and pedopts['messages'] != 'quiet':
        print '\t\tStarted forming animal, sire, and dam lists at %s' %  pyp_utils.pyp_nice_time()
    for i in range(l):
        animals.append(int(pedigree[i].animalID))
        sires.append(int(pedigree[i].sireID))
        dams.append(int(pedigree[i].damID))
        # Experiment to move a computation out of the inner loop
        a[i,i] = 1.0
        # Experiment to see of using dicts instead of lists gives us anything
        try:
            _a = _animals[i]
        except KeyError:
            _animals[i] = int(pedigree[i].animalID)
        try:
            _s = _sires[i]
        except KeyError:
            _sires[i] = int(pedigree[i].sireID)
        try:
            _d = _dams[i]
        except KeyError:
            _dams[i] = int(pedigree[i].damID)
    if pedopts['debug_messages'] and pedopts['messages'] != 'quiet':
        print '\t\tFinished forming animal, sire, and dam lists at %s' %  pyp_utils.pyp_nice_time()
        print '\t\tStarted computing A at %s' %  pyp_utils.pyp_nice_time()
    for row in range(l):
        for col in range(row,l):
            if _sires[col] == 0 and _dams[col] == 0:
                pass
            elif _sires[col] == 0:
                # sire unknown, dam known
                if row == col:
                    pass
                else:
                    a[row,col] = 0.5 * a[row,_dams[col]-1]
                    a[col,row] = a[row,col]
            elif _dams[col] == 0:
                # sire known, dam unknown
                if row == col:
                    pass
                else:
                    a[row,col] = 0.5 * a[row,_sires[col]-1]
                    a[col,row] = a[row,col]
            elif _sires[col] > 0 and _dams[col] > 0:
                # both parents known
                if row == col:
                    a[row,col] = a[row,col] + ( 0.5 * a[_sires[col]-1,_dams[col]-1] )
                else:
                    intermediate = a[row,_sires[col]-1] + a[row,_dams[col]-1]
                    a[row,col] = 0.5 * intermediate
                    a[col,row] = a[row,col]
            else:
                print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (pedobj.pedigree[col].sireID,pedobj.pedigree[col].damID,pedobj.pedigree[col].animalID)
                break
    if pedopts['debug_messages'] and pedopts['messages'] != 'quiet':
        print '\t\tFinished computing A at %s' %  pyp_utils.pyp_nice_time()
    #print a
    if save == 1:
        a_outputfile = '%s%s%s' % (pedopts['filetag'],'_new_a_matrix_','.dat')
        aout = open(a_outputfile,'w')
        label = 'Produced by pyp_nrm/fast_a_matrix()\n'
        aout.write(label)
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

##
# Form a relationship matrix from a pedigree.  fast_a_matrix_r() differs from fast_a_matrix() in that the
# coefficients of relationship are corrected for the inbreeding of the parents.
# @param pedobj A PyPedal pedigree object.
# @param save Flag to indicate whether or not the relationship matrix is written to a file.
# @return A relationship as Numarray matrix.
# @defreturn matrix
def fast_a_matrix_r(pedigree,pedopts,save=0):
    animals = []
    sires = []
    dams = []
    l = len(pedigree)
    #print '[DEBUG]: l = %s' % (l)
    # Grab some array tools
    a = numarray.zeros([l,l],'Float')  # initialize a matrix of zeros of appropriate dimension
    for i in range(l):
        animals.append(int(pedobj.pedigree[i].animalID))
        sires.append(int(pedobj.pedigree[i].sireID))
        dams.append(int(pedobj.pedigree[i].damID))
    # Poorly-written code -- loops twice.  Once to compute CoI and a second time to
    # correct CoR for parental inbreeding.
    for row in range(l):
        for col in range(row,l):
            #print '[DEBUG]: row = %s\tcol = %s' % (row,col)
            if sires[col] == 0 and dams[col] == 0:
                if row == col:
                    # both parents unknown and assumed unrelated
                    a[row,col] = 1.
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
                    a[row,col] = 0.5 * intermediate
                    a[col,row] = a[row,col]
            else:
                if pedopts['debug_messages'] and pedopts['messages'] != 'quiet':
                    print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (pedobj.pedigree[col].sireID,pedobj.pedigree[col].damID,pedobj.pedigree[col].animalID)
                break
    for row in range(l):
        for col in range(row,l):
            if sires[col] == 0 and dams[col] == 0:
                pass
            elif sires[col] == 0:
                # sire unknown, dam known
                if row != col and a[row,col] > 0.:
                    numerator = 0.5 * a[row,dams[col]-1]
                    denominator = sqrt ( a[dams[col]-1,dams[col]-1] )
                    try:
                        coefficient = numerator / denominator
                    except:
                        coefficient = 0.
                    a[row,col] = coefficient
                    a[col,row] = a[row,col]
            elif dams[col] == 0:
                # sire known, dam unknown
                if row != col and a[row,col] > 0.:
                    numerator = 0.5 * a[row,sires[col]-1]
                    denominator = sqrt ( a[sires[col]-1,sires[col]-1] )
                    try:
                        coefficient = numerator / denominator
                    except:
                        coefficient = 0.
                    a[row,col] = coefficient
                    a[col,row] = a[row,col]
            elif sires[col] > 0 and dams[col] > 0:
                # both parents known
                if row != col and a[row,col] > 0.:
                    numerator = 0.5 * ( a[row,sires[col]-1] + a[row,dams[col]-1] )
                    denominator = sqrt ( ( a[sires[col]-1,sires[col]-1] ) * ( a[dams[col]-1,dams[col]-1] ) )
                    try:
                        coefficient = numerator / denominator
                    except:
                        coefficient = 0.
                    a[row,col] = coefficient
                    a[col,row] = a[row,col]
            else:
                pass
    # print a
    if save == 1:
        a_outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_matrix_r_','.dat')
        aout = open(a_outputfile,'w')
        label = 'Produced by pyp_nrm/fast_a_matrix_r()\n'
        aout.write(label)
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

##
# inbreeding() is a proxy function used to dispatch pedigrees to the appropriate
# function for computing CoI.  By default, small pedigrees < 10,000 animals) are
# processed with the tabular method directly.  For larger pedigrees, or if requested,
# the recursive method of VanRaden (1992) is used.
# @param pedobj A PyPedal pedigree object.
# @param method Keyword indicating which method of computing CoI should be used (tabular|vanraden).
# @return A dictionary of CoI keyed to renumbered animal IDs.
# @defreturn dictionary
def inbreeding(pedobj,method='tabular'):
    """Proxy function -- dispatch pedigree to appropriate function."""
    if method not in ['vanraden','tabular']:
        method = 'tabular'
    if method == 'vanraden' or pedobj.metadata.num_records > 10000:
        fx = inbreeding_vanraden(pedobj)
    else:
        fx = inbreeding_tabular(pedobj)

    #
    # Write summary stats to a file.
    #
    a_outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_inbreeding','.dat')
    aout = open(a_outputfile,'w')
    aout.write('# Inbreeding coefficients\n')
    aout.write('# Orig ID\tRenum ID\tf_x\n')
    f_sum = 0.0
    f_min = 999.0
    f_max = -999.0
    for k, v in fx.iteritems():
        line = '%s\t%s\t%s\n' % (pedobj.pedigree[int(k)-1].originalID,k,v)
        aout.write(line)
        #
        # Update self.fa for each Animal object in the pedigree.
        #
        pedobj.pedigree[int(k)-1].fa = v
        f_sum = f_sum + v
        if v > f_max:
            f_max = v
        if v < f_min:
            f_min = v
    f_rng = f_max - f_min
    f_avg = f_sum / len(fx.keys())
    line = '='*80
    aout.write('%s\n' % line)
    aout.write('Inbreeding Statistics\n')
    line = '-'*80
    aout.write('%s\n' % line)
    aout.write('Mean:\t%s\n'%f_avg)
    aout.write('Min:\t%s\n'%f_min)
    aout.write('Max:\t%s\n'%f_max)
    aout.close()
    return fx

##
# inbreeding_vanraden() uses VanRaden's (1992) method for computing coefficients of
# inbreeding in a large pedigree.  The method works as follows:
#   1.  Take a large pedigree and order it from youngest animal to oldest (n, n-1, ..., 1);
#   2.  Recurse through the pedigree to find all of the ancestors of that animal n;
#   3.  Reorder and renumber that "subpedigree";
#   4.  Compute coefficients of inbreeding for that "subpedigree" using the tabular
#       method (Emik and Terrill, 1949);
#   5.  Put the coefficients of inbreeding in a dictionary;
#   6.  Repeat 2 - 5 for animals n-1 through 1; the process is slowest for the early
#       pedigrees and fastest for the later pedigrees.
# @param pedobj A PyPedal pedigree object.
# @param cleanmaps Flag to denote whether or not subpedigree ID maps should be delete after they are used (0|1)
# @return A dictionary of CoI keyed to renumbered animal IDs
# @defreturn dictionary
def inbreeding_vanraden(pedobj,cleanmaps=1):
    fx = {}         # This will hold our coefficients of inbreeding
    _ped = []       # This is a temporary pedigree
    _anids = []     # This is a list of distinct animal IDs from pedobj.pedigree
    for i in range(pedobj.medata.num_recs):
        _anids.append(pedobj.pedigree[i].animalID)
    _anids.sort()       # sort from oldest to youngest
    _anids.reverse()    # reverse the list to put the youngest animals first
    _counter = 0
    for i in _anids:
        if pedobj.kw['debug_messages']:
            if numarray.fmod(_counter,5000) == 0:
                print'%s animal pedigrees processed' % (_counter)
        try:
            _k = fx[i]  # If an exception is thrown, an animal is not in the
                        # dictionary yet.
        except KeyError:
            _tag = '%s_%s' % (pedobj.kw['filetag'],i)
            _ped = recurse_pedigree(pedobj,i,_ped)  # Recurse to build animal i's
                                                    # pedigree.
            _r = []     # This list will hold a copy of the objects in _ped
                    # so that we can renumber animal i's pedigree without
                    # changing the data in pedobj.pedigree.
            for j in range(len(_ped)):
                # This is VERY important -- rather than append a reference
                # to _ped[j-1] to _r we need to append a COPY of _ped[j-1]
                # to _r.  If you change this code and get rid of the call to
                # copy.copy() then things will not work correctly.  You will
                # realize what you have done when your renumberings seem to
                # be spammed.
                _r.append(copy.copy(_ped[j-1]))
            _r = pyp_utils.fast_reorder(_r,_tag)      # Reorder the pedigree
            _s = pyp_utils.renumber(_r,_tag,debug=debug)  # Renumber the pedigree
            _a = fast_a_matrix(_s,_tag)     # Form the NRM w/the tabular method
            _map = pyp_utils.load_id_map(_tag)        # Load the ID map from the renumbering
                                # procedure so that the CoIs are assigned
                                # to the correct animals.
            for j in range(len(_ped)):
                _orig_id = _map[_s[j].animalID]
                fx[_orig_id] = _a[j][j] - 1.
            if cleanmaps:               # Clean up the subpedigree ID maps that we are
                pyp_utils.delete_id_map(_tag)     # not going to use again.
            _map = {}               # Empty our working dictionary and lists
            _a = []
            _s = []
            _r = []
            _ped = []
        _counter = _counter + 1
    return fx

##
# recurse_pedigree() performs the recursion needed to build the subpedigrees used by
# inbreeding_vanraden().  For the animal with animalID anid recurse_pedigree() will
# recurse through the pedigree myped and add references to the relatives of anid to
# the temporary pedigree, _ped.
# @param pedobj A PyPedal pedigree.
# @param anid The ID of the animal whose relatives are being located.
# @param _ped A temporary PyPedal pedigree that stores references to relatives of anid.
# @return A list of references to the relatives of anid contained in myped.
# @defreturn list
def recurse_pedigree(pedobj,anid,_ped):
    """Recurse through a pedigree and return a 'subpedigree' containing
    only relatives of anid."""
    anid = int(anid)
    if anid != 0:
        if pedobj.pedigree[anid-1] not in _ped:
            _ped.append(pedobj.pedigree[anid-1])
    _sire = pedobj.pedigree[anid-1].sireID
    _dam = pedobj.pedigree[anid-1].damID
    if _sire != 0 and _sire != '0':
        recurse_pedigree(pedobj,_sire,_ped)
    if _dam != 0 and _dam != '0':
        recurse_pedigree(pedobj,_dam,_ped)
    return _ped

##
# recurse_pedigree_n() recurses to build a pedigree of depth n.  A depth less than 1 returns
# the animal whose relatives were to be identified.
# @param pedobj A PyPedal pedigree.
# @param anid The ID of the animal whose relatives are being located.
# @param _ped A temporary PyPedal pedigree that stores references to relatives of anid.
# @param depth The depth of the pedigree to return.
# @return A list of references to the relatives of anid contained in myped.
# @defreturn list
def recurse_pedigree_n(pedobj,anid,_ped,depth=3):
    anid = int(anid)
    if anid != 0:
        if pedobj.pedigree[anid-1] not in _ped:
            _ped.append(pedobj.pedigree[anid-1])
    if depth > 0:
        _sire = pedobj.pedigree[anid-1].sireID
        _dam = pedobj.pedigree[anid-1].damID
        if _sire != 0 and _sire != '0':
            recurse_pedigree_n(pedobj,_sire,_ped,depth-1)
        if _dam != 0 and _dam != '0':
            recurse_pedigree_n(pedobj,_dam,_ped,depth-1)
    return _ped

##
# recurse_pedigree_onsided() recurses to build a subpedigree from either the sire
# or dam side of a pedigree.
# @param pedobj A PyPedal pedigree.
# @param side The side to build: 's' for sire and 'd' for dam.
# @param anid The ID of the animal whose relatives are being located.
# @param _ped A temporary PyPedal pedigree that stores references to relatives of anid.
# @return A list of references to the relatives of anid contained in myped.
# @defreturn list
def recurse_pedigree_onesided(pedobj,anid,_ped,side):
    """Recurse through a pedigree and return a 'subpedigree' containing
    only relatives of anid."""
    anid = int(anid)
    if anid != 0:
        if pedobj.pedigree[anid-1] not in _ped:
            _ped.append(pedobj.pedigree[anid-1])
    if side == 's':
        _sire = pedobj.pedigree[anid-1].sireID
        if _sire != 0 and _sire != '0':
            recurse_pedigree(pedobj,_sire,_ped)
    else:
        _dam = pedobj.pedigree[anid-1].damID
        if _dam != 0 and _dam != '0':
            recurse_pedigree(pedobj,_dam,_ped)
    return _ped

##
# recurse_pedigree_idonly() performs the recursion needed to build subpedigrees.
# @param pedobj A PyPedal pedigree.
# @param anid The ID of the animal whose relatives are being located.
# @param _ped A PyPedal list that stores the animalIDs of relatives of anid.
# @return A list of animalIDs of the relatives of anid contained in myped.
# @defreturn list
def recurse_pedigree_idonly(pedobj,anid,_ped):
    """Recurse through a pedigree and return a 'subpedigree' containing
    only relatives of anid."""
    anid = int(anid)
    if anid != 0:
        if pedobj.pedigree[anid-1].animalID not in _ped:
            _ped.append(pedobj.pedigree[anid-1].animalID)
    _sire = pedobj.pedigree[anid-1].sireID
    _dam = pedobj.pedigree[anid-1].damID
    if _sire != 0 and _sire != '0':
        recurse_pedigree_idonly(pedobj,_sire,_ped)
    if _dam != 0 and _dam != '0':
        recurse_pedigree_idonly(pedobj,_dam,_ped)
    return _ped

##
# inbreeding_tabular() computes CoI using the tabular method by calling
# fast_a_matrix() to form the NRM directly.  In order for this routine
# to return successfully requires that you are able to allocate a matrix
# of floats of dimension len(myped)**2.
# @param pedobj A PyPedal pedigree object.
# @return A dictionary of CoI keyed to renumbered animal IDs
# @defreturn dictionary
def inbreeding_tabular(pedobj):
    _a = fast_a_matrix(pedobj,filetag)
    fx = {}
    for i in range(pedobj.medata.num_recs):
        fx[pedobj.pedigree[i].animalID] = _a[i][i] - 1.
    _a = []
    return fx

##
# Form the decomposed form of A, TDT', directly from a pedigree (after
# Henderson, 1976; Thompson, 1977; Mrode, 1996).  Return D, a diagonal
# matrix, and T, a lower triagular matrix such that A = TDT'.
# @param pedobj A PyPedal pedigree object.
# @return A diagonal matrix, D, and a lower triangular matrix, T.
# @defreturn matrices
def a_decompose(pedobj):
    l = pedobj.metadata.num_recs
    # Grab some array tools
    T = numarray.identity(l)
    T = T.astype(Float)
    D = numarray.identity(l)
    D = D.astype(Float)
    for row in range(l):
        for col in range(row+1):
            # cast these b/c items are read from the pedigree file as characters, not  integers
            pedobj.pedigree[col].animalID = int(pedobj.pedigree[col].animalID)
            pedobj.pedigree[col].sireID = int(pedobj.pedigree[col].sireID)
            pedobj.pedigree[col].damID = int(pedobj.pedigree[col].damID)
            if pedobj.pedigree[row].sireID == 0 and pedobj.pedigree[row].damID == 0:
                if row == col:
                    # both parents unknown and assumed unrelated
                    foo = 1.
                    T[row,col] = foo

                    D[row,col] = 1.
                else:
                    foo = 0.
                    T[row,col] = foo
            elif pedobj.pedigree[row].sireID == 0:
                # sire unknown, dam known
                if row == col:
                    foo = 1.
                    T[row,col] = foo

                    fd = a[pedobj.pedigree[row].damID-1,pedobj.pedigree[row].damID-1] - 1.
                    D[row,col] = 0.75 - ( 0.5 * fd )
                else:
                    foo = 0.5 * T[pedobj.pedigree[row].damID-1,col]
                    T[row,col] = foo
            elif pedobj.pedigree[row].damID == 0:
                # sire known, dam unknown
                if row == col:
                    foo = 1.
                    T[row,col] = foo

                    fs = a[pedobj.pedigree[row].sireID-1,pedobj.pedigree[row].sireID-1] - 1.
                    D[row,col] = 0.75 - ( 0.5 * fs )
                else:
                    foo = 0.5 * T[pedobj.pedigree[row].sireID-1,col]
                    T[row,col] = foo
            elif pedobj.pedigree[row].sireID > 0 and pedobj.pedigree[row].damID > 0:
                # both parents known
                if row == col:
                    foo = 1.
                    T[row,col] = foo

                    fs = a[pedobj.pedigree[row].sireID-1,pedobj.pedigree[row].sireID-1] - 1.
                    fd = a[pedobj.pedigree[row].damID-1,pedobj.pedigree[row].damID-1] - 1.
                    D[row,col] = 0.5 - ( 0.25 * ( fs + fd ) )
                else:
                    foo = 0.5 * ( T[int(pedobj.pedigree[row].sireID)-1,col] + T[int(pedobj.pedigree[row].damID)-1,col] )
                    T[row,col] = foo
            else:
                print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (pedobj.pedigree[col].sireID,pedobj.pedigree[col].damID,pedobj.pedigree[col].animalID)
                break
    #print D
    #print T

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_decompose_d_','.dat')
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

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_decompose_t_','.dat')
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

##
# Form the diagonal matrix, D, used in decomposing A and forming the direct
# inverse of A.  This function does not write output to a file - if you need D in
# a file, use the a_decompose()  function.  form_d() is a convenience function
# used by other functions.  Note that inbreeding is not considered in the
# formation of D.
# @param pedobj A PyPedal pedigree object.
# @return A diagonal matrix, D.
# @defreturn matrix
def form_d_nof(pedobj):
    l = pedobj.metadata.num_recs
    D = numarray.identity(l)
    D = D.astype(Float)
    for row in range(l):
        for col in range(row+1):
            # cast these b/c items are read from the pedigree file as characters, not integers
            pedobj.pedigree[col].animalID = int(pedobj.pedigree[col].animalID)
            pedobj.pedigree[col].sireID = int(pedobj.pedigree[col].sireID)
            pedobj.pedigree[col].damID = int(pedobj.pedigree[col].damID)
            if pedobj.pedigree[row].sireID == 0 and pedobj.pedigree[row].damID == 0:
                if row == col:
                    # both parents unknown and assumed unrelated
                    D[row,col] = 1.
                else:
                    pass
            elif pedobj.pedigree[row].sireID == 0:
                # sire unknown, dam known
                if row == col:
                    D[row,col] = 0.75
                else:
                    pass
            elif pedobj.pedigree[row].damID == 0:
                # sire known, dam unknown
                if row == col:
                    D[row,col] = 0.75
                else:
                    pass
            elif pedobj.pedigree[row].sireID > 0 and pedobj.pedigree[row].damID > 0:
                # both parents known
                if row == col:
                    D[row,col] = 0.5
                else:
                    pass
            else:
                print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (pedobj.pedigree[col].sireID,pedobj.pedigree[col].damID,pedobj.pedigree[col].animalID)
                break
    return D

##
# Form the inverse of A directly using the method of Henderson (1976) which
# does not account for inbreeding.
# @param pedobj A PyPedal pedigree object.
# @return The inverse of the NRM, A, not accounting for inbreeding.
# @defreturn matrix
def a_inverse_dnf(pedobj,filetag='_a_inverse_dnf_'):
    """Form the inverse of A directly using the method of Henderson (1976) which
    does not account for inbreeding."""
    l = pedobj.medata.num_recs
    # grab the diagonal matrix, d, and form its inverse
    d_inv = form_d_nof(pedobj)
    for i in range(l):
        d_inv[i,i] = 1. / d_inv[i,i]
    a_inv = numarray.zeros([l,l],Float)
    for i in range(l):
        # cast these b/c items are read from the pedigree file as characters, not integers
        pedobj.pedigree[i].animalID = int(pedobj.pedigree[i].animalID)
        pedobj.pedigree[i].sireID = int(pedobj.pedigree[i].sireID)
        pedobj.pedigree[i].damID = int(pedobj.pedigree[i].damID)
        s = pedobj.pedigree[i].sireID-1
        d = pedobj.pedigree[i].damID-1
        if pedobj.pedigree[i].sireID == 0 and pedobj.pedigree[i].damID == 0:
            # both parents unknown and assumed unrelated
            a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
        elif pedobj.pedigree[i].sireID == 0:
            # sire unknown, dam known
            a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
            a_inv[d,i] = a_inv[d,i] + ( (-0.5) * d_inv[i,i] )
            a_inv[i,d] = a_inv[i,d] + ( (-0.5) * d_inv[i,i] )
            a_inv[d,d] = a_inv[d,d] + ( 0.25 * d_inv[i,i] )
        elif pedobj.pedigree[i].damID == 0:
            # sire known, dam unknown
            a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
            a_inv[s,i] = a_inv[s,i] + ( (-0.5) * d_inv[i,i] )
            a_inv[i,s] = a_inv[i,s] + ( (-0.5) * d_inv[i,i] )
            a_inv[s,s] = a_inv[s,s] + ( 0.25 * d_inv[i,i] )
        elif pedobj.pedigree[i].sireID > 0 and pedobj.pedigree[i].damID > 0:
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
            print '[ERROR]: There is a problem with the sire (ID %s) and/or dam (ID %s) of animal %s' % (pedobj.pedigree[col].sireID,pedobj.pedigree[col].damID,pedobj.pedigree[col].animalID)
            break

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_inverse_dnf_a_inv','.dat')
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

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_inverse_dnf_d_inv','.dat')
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

##
# Directly form the inverse of A from the pedigree file - accounts for
# inbreeding - using the method of Quaas (1976).
# @param pedobj A PyPedal pedigree object.
# @return The inverse of the NRM, A, accounting for inbreeding.
# @defreturn matrix
def a_inverse_df(pedobj):
    """Directly form the inverse of A from the pedigree file - accounts for
    inbreeding - using the method of Quaas (1976)."""
    l = pedobj.medata.num_recs
    from math import sqrt
    # Grab some array tools
    d_inv = numarray.zeros([l,l],Float)
    a_inv = numarray.zeros([l,l],Float)
    LL = numarray.zeros([l,l],Float)
    # Form L and D-inverse
    for row in range(l):
        for col in range(row+1):
            # cast these b/c items are read from the pedigree file as characters, not integers
            pedobj.pedigree[col].animalID = int(pedobj.pedigree[col].animalID)
            pedobj.pedigree[col].sireID = int(pedobj.pedigree[col].sireID)
            pedobj.pedigree[col].damID = int(pedobj.pedigree[col].damID)
            s = pedobj.pedigree[row].sireID-1
            d = pedobj.pedigree[row].damID-1
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
        s = pedobj.pedigree[i].sireID-1
        d = pedobj.pedigree[i].damID-1
        if pedobj.pedigree[i].sireID == 0 and pedobj.pedigree[i].damID == 0:
            # both parents unknown and assumed unrelated
            a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
        elif pedobj.pedigree[i].sireID == 0:
            # sire unknown, dam known
            a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
            a_inv[d,i] = a_inv[d,i] + ( (-0.5) * d_inv[i,i] )
            a_inv[i,d] = a_inv[i,d] + ( (-0.5) * d_inv[i,i] )
            a_inv[d,d] = a_inv[d,d] + ( 0.25 * d_inv[i,i] )
        elif pedobj.pedigree[i].damID == 0:
            # sire known, dam unknown
            a_inv[i,i] = a_inv[i,i] + d_inv[i,i]
            a_inv[s,i] = a_inv[s,i] + ( (-0.5) * d_inv[i,i] )
            a_inv[i,s] = a_inv[i,s] + ( (-0.5) * d_inv[i,i] )
            a_inv[s,s] = a_inv[s,s] + ( 0.25 * d_inv[i,i] )
        elif pedobj.pedigree[i].sireID > 0 and pedobj.pedigree[i].damID > 0:
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

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_inverse_df_a_inv','.dat')
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

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_inverse_df_l','.dat')
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

    outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_a_inverse_df_d_inv','.dat')
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