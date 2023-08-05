#!/usr/bin/python

###############################################################################
# NAME: pyp_metrics.py
# VERSION: 2.01 (28JAN2004)
# AUTHOR: John B. Cole, PhD (jcole@funjackals.com)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   min_max_f()
#   a_effective_founders_lacy()
#   a_effective_founders_boichard()
#   a_effective_ancestors_definite()
#   a_coefficients()
#   theoretical_ne_from_metadata()
#   pedigree_completeness()
###############################################################################

from string import *
from time import *
from Numeric import *

def min_max_f(myped,filetag='_min_max_f_',a='',n=10):
    """Given a pedigree or relationship matrix, return a list of the
    individuals with the n largest and n smallest coefficients of
    inbreeding."""
    if not a:
        a = a_matrix(myped)
    l = len(myped)
    f_min = 1.0
    min_f_list = []
    min_f_code_list = []
    # id_map_from_file()
    # id_map_new_to_old()
    # Initialize the lists to length n so that we do not have to
    # worry about bounds checking.
    for i in range(n):
        min_f_list.append(1.0)
        min_f_code_list.append(0)
    for row in range(l):
        for col in range(row):
            f = 1. - a[row,row]
            if f < f_min:
                minindex = min_f_list.index(f_min)
                code = '%s:%s' % (row,f)
                min_f_list[minindex] = f
                min_f_code_list[minindex] = code
                f_min = max(min_f_list)

def a_effective_founders_lacy(myped,filetag='_f_e_lacy_',a=''):
    """Calculate the number of effective founders in a pedigree using the exact method of Lacy."""
    if not a:
        from pyp_nrm import fast_a_matrix
        a = fast_a_matrix(myped)
    l = len(myped)
    # form lists of founders and descendants
    n_f = 0
    n_d = 0
    fs = []
    ds = []
    for i in range(l):
        if myped[i].founder == 'y':
            n_f = n_f + 1
            fs.append(myped[i].animalID)
        else:
            n_d = n_d + 1
            ds.append(myped[i].animalID)
    #from Numeric import *
    from Numeric import zeros
    p = zeros([n_d,n_f],Float)
    # create a table listing relationship between founders and descendants
    for row in range(n_f):
        for col in range(n_d):
            p[col,row] = a[fs[row]-1,ds[col]-1]
    # sum each column
    p_sums= []
    for col in range(n_f):
        p_sum = 0.
        for row in range(n_d):
            if p[row,col] != 0:
                p_sum = p_sum + p[row,col]
        p_sums.append(p_sum)
    # weight sums by counts to get relative contributions
    rel_p = []
    rel_p_sq = []
    for i in range(len(p_sums)):
        rel_p.append(p_sums[i] / n_d)
        rel_p_sq.append(rel_p[i] * rel_p[i])
    # sum  the squared relative contributions and take the reciprocal to get f_e
    sum_rel_p_sq = 0.
    for i in range(len(rel_p_sq)):
        sum_rel_p_sq = sum_rel_p_sq + rel_p_sq[i]
    #print 'p_sums:\t%s' % (p_sums)
    #print 'rel_ps:\t%s' % (rel_p)
    if sum_rel_p_sq == 0.:
        f_e = 0.
    else:
        f_e = 1. / sum_rel_p_sq
    #print 'animals:\t%s' % (l)
    #print 'founders:\t%s' % (n_f)
    #print 'descendants:\t%s' % (n_d)
    #print 'f_e:\t\t%5.3f' % (f_e)
    #print '='*60

    # write some output to a file for later use
    outputfile = '%s%s%s' % (filetag,'_fe_lacy_','.dat')
    aout = open(outputfile,'w')
    line1 = '%s animals\n' % (l)
    line2 = '%s founders: %s\n' % (n_f,fs)
    line3 = '%s descendants: %s\n' % (n_d,ds)
    line4 = 'effective number of founders: %s\n' % (f_e)
    line5 = '='*60+'\n'
    aout.write(line5)
    aout.write(line1)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line5)
    aout.close()

def a_effective_founders_boichard(myped,filetag='_f_e_boichard_',a=''):
    """The algorithm in Appendix A of Boichard et al. (1996) is not very well written.
    a_effective_founders_boichard() implements that algorithm (successfully, I hope).
    Note that answers from this function will not necessarily match those from
    a_effective_founders_lacy()."""
    if not a:
        from pyp_nrm import fast_a_matrix
        a = fast_a_matrix(myped)
    l = len(myped)
    # count founders and descendants
    n_f = 0
    n_d = 0
    fs = []
    ds = []
    gens = []
    ngen = 0    # number of individuals in the most recent generation
    # loop through the pedigree quickly and count founders and descendants
    # also, make a list of generations present in the pedigree
    for i in range(l):
        if myped[i].founder == 'y':
            n_f = n_f + 1
            fs.append(myped[i].animalID)
        else:
            n_d = n_d + 1
            ds.append(myped[i].animalID)
        #g = int(myped[i].gen)
        g = myped[i].gen
        if g in gens:
            pass
        else:
            gens.append(g)
    # OK - now we have a list of generations sorted in reverse (descending) order
    gens.sort()
    gens.reverse()
    #print gens
    #print fs
    #print ds
    # make a copy of myped
    tempped = myped
    # reverse the elements of tempped in place
    # now animals are ordered from oldest to youngest in tempped
    tempped.reverse()
    # form q, a vector of that will contain the probabilities of gene origin when we are done
    #from Numeric import *
    from Numeric import zeros
    # We are going to initialize a vector of zeros to form q, and then we will addones to q that
    # correspond to members of the youngest generation.
    q = zeros([l],Float)
    for i in range(l):
        #if int(myped[i].gen) == gens[0]:
        if myped[i].gen == gens[0]:
            # be careful messing with this or the elements of q will end up in the wrong
            # columns
            q[l-i-1] = 1.
            ngen = ngen + 1
        else:
            pass
    # loop through the pedigree and form the final version of q (the vector of
    # individual contributions)
    for i in range(l):
        if tempped[i].sireID == 0 and tempped[i].damID == 0:
            # both parents unknown
            pass
        elif tempped[i].sireID == 0:
            # sire unknown, dam known
            q[i] = q[tempped[i].animalID-1] * 0.5
            q[tempped[i].damID-1] = q[tempped[i].damID-1] + (0.5 * q[tempped[i].animalID-1])
        elif tempped[i].damID == 0:
            # sire known, dam unknown
            q[tempped[i].animalID-1] * 0.5
            q[tempped[i].sireID-1] = q[tempped[i].sireID-1] + (0.5 * q[tempped[i].animalID-1])
        else:
            # both parents known
            q[tempped[i].sireID-1] = q[tempped[i].sireID-1] + (0.5 * q[tempped[i].animalID-1])
            q[tempped[i].damID-1] = q[tempped[i].damID-1] + (0.5 * q[tempped[i].animalID-1])
    #print q
    # divide the elements of q by the number of individuals in the pedigree.  this should
    # ensure that the founder contributions sum to 1.
    q = q / ngen
    #q = q / 10
    # accumulate the sum of squared founder contributions
    sum_sq = 0.
    sum_fn = 0.
    #print fs
    for i in fs:
        sum_sq = sum_sq + ( q[i-1] * q[i-1] )
        sum_fn = sum_fn + q[i-1]
    #print 'sum_fn:\t%s' % (sum_fn)
    #print 'sum_sq:\t%s' % (sum_sq)
    if sum_sq == 0.:
        f_e = 0.
    else:
        f_e = 1. / sum_sq
    #print 'animals:\t%s' % (l)
    #print 'founders:\t%s' % (n_f)
    #print 'descendants:\t%s' % (n_d)
    #print 'f_e:\t\t%5.3f' % (f_e)
    #print '='*60

    # write some output to a file for later use
    outputfile = '%s%s%s' % (filetag,'_fe_boichard_','.dat')
    aout = open(outputfile,'w')
    line1 = 'q: %s\n' % (q)
    line2 = '%s founders: %s\n' % (n_f,fs)
    line3 = '%s descendants: %s\n' % (n_d,ds)
    line4 = 'generations: %s\n' % (gens)
    line5 = '%s animals in generation %s\n' % (ngen,gens[0])
    line6 = 'effective number of founders: %s\n' % (f_e)
    line7 = '='*60+'\n'
    aout.write(line7)
    aout.write(line1)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line5)
    aout.write(line6)
    aout.write(line7)
    aout.close()

def a_effective_ancestors_definite(myped,filetag='_f_a_definite_',a=''):
    """The algorithm in Appendix B of Boichard et al. (1996) is not very well written.
    a_effective_ancestors_definite() implements that algorithm (successfully, I hope).

	NOTE: One problem here is that if you pass a pedigree WITHOUT generations and error
	is not thrown.  You simply end up wth a list of generations that contains the default
	value for Animal() objects, 0.
	"""
    if not a:
        from pyp_nrm import fast_a_matrix
        a = fast_a_matrix(myped)
    l = len(myped)  # number of animals in the pedigree file
                        # count founders and descendants
    n_f = 0     # number of founders
    n_d = 0     # number of descendants
    fs = []     # list of founders
    ds = []     # list of descendants
    gens = []       # list of generation IDs in the pedigree
    ancestors = []  # list of ancestors already processed
    contribs = []   # ancestor contributions
    ngen = 0        # number of individuals in the most recent generation
    # loop through the pedigree quickly and count founders and descendants
    # also, make a list of generations present in the pedigree
    for i in range(l):
        if myped[i].founder == 'y':
            n_f = n_f + 1
            fs.append(myped[i].animalID)
        else:
            n_d = n_d + 1
            ds.append(myped[i].animalID)
        #g = int(myped[i].gen)
        g = myped[i].gen
        if g in gens:
            pass
        else:
            gens.append(g)
    # OK - now we have a list of generations sorted in reverse (descending) order
    gens.sort()
    #print 'DEBUG: gens: %s' % (gens)
    gens.reverse()
    # make a copy of myped - note that tempped = myped would only have created areference to
    # myped, not an actual separate copy of myped.
    tempped = myped[:]
    # now animals are ordered from oldest to youngest in tempped
    tempped.reverse()
    # form q, a vector of that will contain the probabilities of gene origin when we are done
    from Numeric import zeros
    # We are going to initialize a vector of zeros to form q, and then we will add ones to q that
    # correspond to members of the youngest generation.
    younglist = []
    q = zeros([l],Float)
    for i in range(l):
        if myped[i].gen == gens[0]:
            q[myped[i].animalID-1] = 1.
            ngen = ngen + 1
            younglist.append(myped[i].animalID)
    #print 'Original q: %s' % (q)
    # loop through the pedigree and form the initial version of q
    #single_parents = []
    for i in range(l):
        if tempped[i].sireID == 0 and tempped[i].damID == 0:
            # both parents unknown
            # print 'DEBUG: Animal %s is a founder' % (tempped[i].animalID)
            pass
        elif tempped[i].sireID == 0:
            # sire unknown, dam known
            q[tempped[i].animalID-1] = q[tempped[i].animalID-1] * 0.5
            q[tempped[i].damID-1] = q[tempped[i].damID-1] + (0.5 * q[tempped[i].animalID-1])
        elif tempped[i].damID == 0:
            # sire known, dam unknown
            q[tempped[i].animalID-1] = q[tempped[i].animalID-1] * 0.5
            q[tempped[i].sireID-1] = q[tempped[i].sireID-1] + (0.5 * q[tempped[i].animalID-1])
        else:
            # both parents known
            q[tempped[i].sireID-1] = q[tempped[i].sireID-1] + (0.5 *q[tempped[i].animalID-1])
            q[tempped[i].damID-1] = q[tempped[i].damID-1] + (0.5 * q[tempped[i].animalID-1])
        #print 'An: %s\tSire: %s\tDam: %s' % (tempped[i].animalID,tempped[i].sireID,tempped[i].damID)
        #print 'STEP %s: q: %s' % (i,q)
    # divide the elements of q by the number of individuals in the pedigree.  this should
    # ensure that the founder contributions sum to 1.
    #print '# in Latest Generation: %s' % (ngen)
    for y in younglist:
        q[y-1] = 0.
    #print 'Uncorrected q: %s' % (q)
    q = q / ngen
    #print 'Corrected q: %s' % (q)

    # Find largest value of q
    max_p_index = argmax(q)
    max_p = q[max_p_index]
    contribs.append(max_p)
    picked = []
    picked.append(max_p_index)

    for j in range(l-ngen):
        #print '*'*60

        # Delete the pedigree info for the animal with largest q
        myped[max_p_index].sireID = 0.          # delete sire in myped (forward order)
        myped[max_p_index].damID = 0.           # delete dam in myped (forward order)
        tempped[l-max_p_index-1].sireID = 0.        # delete sire in tempped (reverse order)
        tempped[l-max_p_index-1].damID = 0.     # delete dam in tempped (reverse order)
        ancestors.append(myped[max_p_index].animalID)   # add the animal with largest q to the
                                                # list of ancestors

        # form q, the vector of contributions we are going to use
        q = zeros([l],Float)
        a = zeros([l],Float)
        for i in range(l):
            if myped[i].gen == gens[0]:
                q[myped[i].animalID-1] = 1.
        for j in picked:
            a[j] = 1.

        # Loop through pedigree to process q
        #-- q must be processed from YOUNGEST to OLDEST
        #-- a must be processed from OLDEST to YOUNGEST
        for i in range(l):
            if tempped[i].sireID == 0 and tempped[i].damID == 0:
                # both parents unknown
                pass
            elif tempped[i].sireID == 0:
                # sire unknown, dam known
                q[tempped[i].damID-1] = q[tempped[i].damID-1] + (0.5 * q[tempped[i].animalID-1])
                a[i] = a[i] + ( 0.5 * a[myped[i].damID-1] )
            elif tempped[i].damID == 0:
                # sire known, dam unknown
                q[tempped[i].sireID-1] = q[tempped[i].sireID-1] + (0.5 * q[tempped[i].animalID-1])
                a[i] = a[i] + ( 0.5 * a[myped[i].sireID-1] )
            else:
                # both parents known
                q[tempped[i].sireID-1] = q[tempped[i].sireID-1] + (0.5 * q[tempped[i].animalID-1])
                q[tempped[i].damID-1] = q[tempped[i].damID-1] + (0.5 * q[tempped[i].animalID-1])
                foos = int(myped[i].sireID-1)
                food = int(myped[i].damID-1)
                a[i] = a[i] + ( 0.5 * a[foos] )
                a[i] = a[i] + ( 0.5 * a[food] )

        #print 'DEBUG: q: %s' % (q)
        #print 'DEBUG: a: %s' % (a)
        # Loop through the pedigree to process p
        p = zeros([l],Float)
        for i in range(l):
            p[i] = q[i] * ( 1. - a[i] )
        #print 'DEBUG: p: %s' % (p)

        # Find largest p
        p_temp = p[:]

        for y in younglist:
            p_temp[y-1] = -1.
        for c in picked:
            p_temp[y-1] = -1.

        max_p_index = argmax(p_temp)
        max_p = p_temp[max_p_index]
        max_p = max_p / ngen
        contribs.append(max_p)
        picked.append(max_p_index)
        #print 'DEBUG: p_temp: %s' % (p_temp)
        #print 'DEBUG: picked: %s' % (picked)
        #print 'DEBUG: contribs: %s' % (contribs)

    sum_p_sq = 0.
    for i in range(len(contribs)):
        sum_p_sq = sum_p_sq + ( contribs[i] * contribs[i] )
    f_a = 1. / sum_p_sq
    #print 'DEBUG: f_a: %s' % (f_a)
    # write some output to a file for later use
    outputfile = '%s%s%s' % (filetag,'_fa_boichard_definite_','.dat')
    aout = open(outputfile,'w')
    line2 = '%s founders: %s\n' % (n_f,fs)
    line3 = '%s descendants: %s\n' % (n_d,ds)
    line4 = 'generations: %s\n' % (gens)
    line5 = '%s animals in generation %s\n' % (ngen,gens[0])
    line6 = 'effective number of ancestors: %s\n' % (f_a)
    line7 = 'ancestors: %s\n' % (ancestors)
    line8 = 'ancestor contributions: %s\n' % (contribs)
    line = '='*60+'\n'
    aout.write(line)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line5)
    aout.write(line6)
    aout.write(line7)
    aout.write(line8)
    aout.write(line)
    aout.close()

def a_coefficients(myped,filetag='_coefficients_',a=''):
    """Write population average coefficients of inbreeding and relationship to a
    file, as well as individual animal IDs and coefficients of inbreeding."""
    if not a:
        from pyp_nrm import fast_a_matrix
        a = fast_a_matrix(myped)
    l = len(myped)
    # Grab some array tools
    #from Numeric import *
    f_avg = f_sum = f_n = 0.
    fnz_avg = fnz_sum = fnz_n = 0.
    r_avg = r_sum = r_n = 0.
    rnz_avg = rnz_sum = rnz_n = 0.

    # calculate average coefficients of inbreeding
    for row in range(l):
        f_sum = f_sum + a[row,row] - 1.
        f_n = f_n + 1
    f_avg = f_sum / f_n

    # calculate average non-zero coefficients of inbreeding
    for row in range(l):
        if ( a[row,row] > 1. ):
            fnz_sum = fnz_sum + a[row,row] - 1.
            fnz_n = fnz_n + 1
    if fnz_sum > 0.:
        fnz_avg = fnz_sum / fnz_n
    else:
        fnz_avg = 0

    # calculate average coefficients of relationship
    for row in range(l):
        for col in range(row):
            r_sum = r_sum + a[row,col]
            r_n = r_n + 1
    r_avg = r_sum / r_n

    # calculate average non-zero coefficients of relationship
    for row in range(l):
        for col in range(row):
            if ( a[row,col] > 0. ):
                rnz_sum = rnz_sum + a[row,col]
                rnz_n = rnz_n + 1
    if rnz_sum > 0.:
        rnz_avg = rnz_sum / rnz_n
    else:
        rnz_avg = 0.

    # calculate the average relationship between each individual in the population
    # and all other animals in the population and write it to a file
    outputfile2 = '%s%s%s' % (filetag,'_rel_to_pop_','.dat')
    aout2 = open(outputfile2,'w')
    line1_2 = '# Average relationship to population (renumbered ID, r)\n'
    for row in range(l):
        r_pop_avg = 0.
        for col in range(l):
            if ( row == col ):
                pass
            else:
                r_pop_avg = r_pop_avg + a[row,col]
        r_pop_avg = r_pop_avg / l
        line = '%s %s\n' % (myped[row].animalID,r_pop_avg)
        aout2.write(line)
    aout2.close()

    # output population average coefficients
    outputfile = '%s%s%s' % (filetag,'_population_coefficients_','.dat')
    aout = open(outputfile,'w')
    line1 = '# Population average coefficients of inbreeding and relationship\n'
    line2 = '#   f_avg [fnz_avg] = average [nonzero] coefficient of inbreeding\n'
    line3 = '#   f_n [fnz_n] = number of diagonal elements (animals) [>1] in the relationship matrix\n'
    line4 = '#   f_sum [fnz_sum] = sum of [nonzero] coefficients of inbreeding\n'
    line5 = '#   r_avg [rnz_avg] = average [nonzero] coefficient of relationship\n'
    line6 = '#   r_n [rnz_n] = number of [non-zero] elements in the upper off-diagonal of A\n'
    line7 = '#   r_sum [rnz_sum] = sum of [non-zero] elements in the upper off-diagonal of A\n'
    line_f = 'f_n: %s\nf_sum: %s\nf_avg: %5.3f\n' % (f_n,f_sum,f_avg)
    line_fnz = 'fnz_n: %s\nfnz_sum: %s\nfnz_avg: %5.3f\n' % (fnz_n,fnz_sum,fnz_avg)
    line_r = 'r_n: %s\nr_sum: %s\nr_avg: %5.3f\n' % (r_n,r_sum,r_avg)
    line_rnz = 'rnz_n: %s\nrnz_sum: %s\nrnz_avg: %5.3f\n' % (rnz_n,rnz_sum,rnz_avg)
    aout.write(line1)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line5)
    aout.write(line6)
    aout.write(line7)
    aout.write(line_f)
    aout.write(line_fnz)
    aout.write(line_r)
    aout.write(line_rnz)
    aout.close()
    # output individual coefficients of inbreeding
    outputfile = '%s%s%s' % (filetag,'_individual_coefficients_','.dat')
    aout = open(outputfile,'w')
    line1 = '# individual coefficients of inbreeding\n'
    line2 = '# animalID f_a\n'
    aout.write(line1)
    aout.write(line2)
    for row in range(l):
        line = '%s\t%6.4f\n' % (myped[row].animalID,a[row,row]-1.)
        aout.write(line)
    aout.close()

def theoretical_ne_from_metadata(metaped,filetag='_ne_from_metadata_'):
    ns = float(metaped.num_unique_sires)
    nd = float(metaped.num_unique_dams)
    ne = 1. / ( (1./(4.*ns)) + (1./(4.*nd)) )
    outputfile = '%s%s%s' % (filetag,'_ne_from_metadata_','.dat')
    aout = open(outputfile,'w')
    line1 = '# Theoretical effective population size (N_e)\n'
    line2 = '#   n_sires = number of sires\n'
    line3 = '#   n_dams = number of dams\n'
    line4 = '#   n_e = effective population size\n'
    line_ns = 'n_sires: %s\n' % (ns)
    line_nd = 'n_dams: %s\n' % (nd)
    line_ne = 'n_e: %s\n' % (ne)
    aout.write(line1)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line_ns)
    aout.write(line_nd)
    aout.write(line_ne)
    aout.close()

def pedigree_completeness(myped,filetag='_pedigree_completeness_'):
    """For each animal in the pedigree compute an arbitrary measure
    of pedigree completeness.  Write a file of individual pedigree
    completeness coefficients to a file.  Als write a file of summary
    data for the population."""
    
    # At the moment we are just counting the number of pedigrees with both oarents unknown,
    # sire or dam unknown, and no parents unknown.  These numbers needto be augmented with
    # a better metric later.  In fac, this should be wrapped into the pedigree metadata object later.
    
    l = len(myped)
    n_bu = 0    # Pedigrees with both parents unknown.
    n_su = 0    # Pedigrees with sires unknown.
    n_du = 0    # Pedigrees with dams unknown.
    n_nu = 0    # Pedigrees with neither parent unknown.
    
    # Output individual data.
    outputfile = '%s%s%s' % (filetag,'_individual_pedigree_completeness_','.dat')
    aout = open(outputfile,'w')
    line1 = '# Individual pedigree completeness\n'
    line2 = '#   Records are: animalID sire_known dam_known number_known\n'
    line3 = '#   Example:\n'
    line4 = '#      1001 1 0 1\n'
    line5 = '#      1002 1 1 2\n'
    line6 = '#      1003 0 0 0\n'
    aout.write(line1)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line5)
    aout.write(line6)
    for p in xrange(l):
        if myped[p].sireID == '0' and myped[p].damID:
            n_bu = n_bu + 1
            individual = '%s %s %s %s\n' % (myped[p].animalID,0,0,0)
        elif myped[p].sireID == '0':
            n_su = n_su + 1
            individual = '%s %s %s %s\n' % (myped[p].animalID,1,0,1)
        elif myped[p].damID == '0':
            n_du = n_du + 1
            individual = '%s %s %s %s\n' % (myped[p].animalID,0,1,1)
        else:
            n_nu = n_nu + 1
            individual = '%s %s %s %s\n' % (myped[p].animalID,1,1,2)
        aout.write(individual)
    aout.close()
    
    # Output population data.
    p_bu = (1.*n_bu) / (1.*l)
    p_su = (1.*n_su) / (1.*l)
    p_du = (1.*n_du) / (1.*l)
    p_nu = (1.*n_nu) / (1.*l)
    
    outputfile = '%s%s%s' % (filetag,'_population_pedigree_completeness_','.dat')
    aout = open(outputfile,'w')
    line1 = '# Population pedigree completeness\n'
    line2 = '#   n = number of pedigrees\n'
    line3 = '#   n_b = number (%) of pedigrees with both parents unknown\n'
    line4 = '#   n_s = number (%) of pedigrees with sires unknown\n'
    line5 = '#   n_d = number (%) of pedigrees with dams unknown\n'
    line6 = '#   n_n = number (%) of pedigrees with neither parent unknown\n'
    line_n = 'n: %s\n' % (l)
    line_n_b = 'n_b: %s (%s)\n' % (n_bu,p_bu)
    line_n_s = 'n_s: %s (%s)\n' % (n_su,p_su)
    line_n_d = 'n_d: %s (%s)\n' % (n_du,p_du)
    line_n_n = 'n_n: %s (%s)\n' % (n_nu,p_nu)
    aout.write(line1)
    aout.write(line2)
    aout.write(line3)
    aout.write(line4)
    aout.write(line5)
    aout.write(line6)
    aout.write(line_n)
    aout.write(line_n_b)
    aout.write(line_n_s)
    aout.write(line_n_d)
    aout.write(line_n_n)
    aout.close()
