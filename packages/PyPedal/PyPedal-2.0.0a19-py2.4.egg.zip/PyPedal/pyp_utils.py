#!/usr/bin/python

###############################################################################
# NAME: pyp_utils.py
# VERSION: 2.0.0a19 (22AUGUST2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   load_pedigree()
#   preprocess()
#   new_preprocess()
#   set_ancestor_flag()
#   set_generation()
#   set_age()
#   set_species()
#   assign_sexes()
#   assign_offspring()
#   reorder()
#   fast_reorder()
#   renumber()
#   load_id_map()
#   delete_id_map()
#   id_map_new_to_old()
#   trim_pedigree_to_year()
#   pedigree_range()
#   sort_dict_by_keys()
#   sort_dict_by_values()
#   simple_histogram_dictionary()
#   reverse_string()
#   pyp_nice_time()
#   string_to_table_name()
#   pyp_datestamp()
###############################################################################

##
# pyp_utils contains a set of procedures for creating and operating on PyPedal pedigrees.
# This includes routines for reordering and renumbering pedigrees, as well as for modifying
# pedigrees.
##

import logging, numarray, os, string, sys, time
import pyp_demog, pyp_metrics, pyp_newclasses

##
# set_ancestor_flag() loops through a pedigree to build a dictionary of all of the parents
# in the pedigree.  It then sets the ancestor flags for the parents.  set_ancestor_flag()
# expects a reordered and renumbered pedigree as input!
# @param pedobj A PyPedal NewPedigree object.
# @return 0 for failure and 1 for success.
# @defreturn integer
def set_ancestor_flag(pedobj):
    try:
        parents = {}        # holds a list of animals who are parents
        l = len(pedobj.pedigree)
        if l < 2:
            print '[ERROR]: pedobj.pedigree only contains one record -- nothing to do in set_ancestor_flag()!'
            return

        pedobj.pedigree.reverse()     # We want to go from young to old.
        for i in xrange(l):
            # Put the animalIDs of the animals parents in the parents list if
            # they are known and are not already in the dictionary.
            if pedobj.kw['messages'] == 'debug':
                print '[DEBUG]:\t\tanimal: %s\tsire: %s\tdam: %s' % (pedobj.pedigree[i].animalID,pedobj.pedigree[i].sireID,pedobj.pedigree[i].damID)
            if int(pedobj.pedigree[i].sireID) != 0:
                try:
                    _i = parents[int(pedobj.pedigree[i].sireID)]
                except:
                    parents[int(pedobj.pedigree[i].sireID)] = int(pedobj.pedigree[i].sireID)
                    pedobj.pedigree[int(pedobj.pedigree[i].sireID)-1].ancestor = 1

            if int(pedobj.pedigree[i].damID) != 0:
                try:
                    _i = parents[int(pedobj.pedigree[i].damID)]
                except:
                    parents[int(pedobj.pedigree[i].damID)] = int(pedobj.pedigree[i].damID)
                    pedobj.pedigree[int(pedobj.pedigree[i].damID)-1].ancestor = 1
        pedobj.pedigree.reverse()     # Put pedobj.pedigree back the way it was -- pass-by-reference, don't you know!

        if pedobj.kw['file_io']:
            try:
                a_outputfile = '%s%s%s' % (pedobj.kw['filetag'],'_ancestors','.dat')
                aout = open(a_outputfile,'w')
                aout.write('# FILE: %s\n' % a_outputfile)
                aout.write('# ANCESTOR list produced by PyPedal.\n')
                for l in parents.keys():
                    aout.write('%s\n' % l)
                aout.close()
                logging.info('pyp_utils/set_ancestor_flag() wrote file %s.' % (a_outputfile))
            except:
                logging.error('pyp_utils/set_ancestor_flag() could not write file %s.' % (a_outputfile))

        return 1

    except:
        logging.error('pyp_utils/set_ancestor_flag() could not write file %s.' % (a_outputfile))
        return 0

##
# set_generation() Works through a pedigree to infer the generation to which an animal
# belongs based on founders belonging to generation 1.  The igen assigned to an animal
# as the larger of sire.igen+1 and dam.igen+1.  This routine assumes that myped is
# reordered and renumbered.
# @param pedobj A PyPedal NewPedigree object.
# @return 0 for failure and 1 for success.
# @defreturn integer
def set_generation(pedobj):
    try:
        if pedobj.kw['messages'] == 'debug':
            print '[NOTE]: pyp_utils/set_generation() assigning inferred generations in pedigree %s.' % (pedobj.kw['pedname'])
        l = len(pedobj.pedigree)
        for i in range(l):
            if int(pedobj.pedigree[i].sireID) == 0 and int(pedobj.pedigree[i].damID) == 0:
                pedobj.pedigree[i].igen = 1
            elif int(pedobj.pedigree[i].sireID) == 0:
                pedobj.pedigree[i].igen = pedobj.pedigree[int(pedobj.pedigree[i].damID)-1].igen + 1
            elif int(pedobj.pedigree[i].damID) == 0:
                pedobj.pedigree[i].igen = pedobj.pedigree[int(pedobj.pedigree[i].sireID)-1].igen + 1
            else:
                pedobj.pedigree[i].igen = max(pedobj.pedigree[int(pedobj.pedigree[i].sireID)-1].igen + 1,pedobj.pedigree[int(pedobj.pedigree[i].damID)-1].igen + 1)
        logging.info('pyp_utils/set_generation() assigned inferred generations in pedigree %s' % (pedobj.kw['pedname']))
        return 1
    except:
        logging.error('pyp_utils/set_generation() was unable to assign inferred generations in pedigree %s' % (pedobj.kw['pedname']))
        return 0

##
# set_age() Computes ages for all animals in a pedigree based on the global
# BASE_DEMOGRAPHIC_YEAR defined in pyp_demog.py.  If the by is unknown, the
# inferred generation is used.  If the inferred generation is unknown, the
# age is set to -999.
# @param pedobj A PyPedal pedigree object.
# @return 0 for failure and 1 for success.
# @defreturn integer
def set_age(pedobj):
    try:
        if pedobj.kw['messages'] == 'debug':
            print '[NOTE]: pyp_utils/set_age() assigning inferred ages in pedigree %s.' % (pedobj.kw['pedname'])
        l = len(pedobj.pedigree)
        for i in range(l):
            if pedobj.pedigree[i].by == -999 and pedobj.pedigree[i].igen == -999:
                pedobj.pedigree[i].age = -999
            elif pedobj.pedigree[i].by == -999 and pedobj.pedigree[i].igen != -999:
                pedobj.pedigree[i].age = pedobj.pedigree[i].igen
            else:
                pedobj.pedigree[i].age = pedobj.pedigree[i].by - pyp_demog.BASE_DEMOGRAPHIC_YEAR
        logging.info('pyp_utils/set_age() assigned ages in pedigree %s' % (pedobj.kw['pedname']))
        return 1
    except:
        logging.error('pyp_utils/set_age() was unable to assign ages in pedigree %s' % (pedobj.kw['pedname']))
        return 0

##
# set_species() assigns a specie to every animal in the pedigree.
# @param pedobj A PyPedal pedigree object.
# @param species A PyPedal string.
# @return 0 for failure and 1 for success.
# @defreturn integer
def set_species(pedobj,species='u'):
    try:
        if pedobj.kw['messages'] == 'debug':
            print '[NOTE]: pyp_utils/set_species() assigning specie %s to all animals in pedigree %s.' % (species, pedobj.kw['pedname'])
        l = len(pedobj.pedigree)
        for i in range(l):
            if len(species) > 0:
                pedobj.pedigree[i].species = species
            else:
                pedobj.pedigree[i].species = 'u'
        logging.info('pyp_utils/set_species() assigned a specie in pedigree %s' % (pedobj.kw['pedname']))
        return 1
    except:
        logging.error('pyp_utils/set_age() was unable to assign ages in pedigree %s' % (pedobj.kw['pedname']))
        return 0

##
# assign_sexes() assigns a sex to every animal in the pedigree using sire and daughter lists for improved accuracy.
# @param pedobj A renumbered and reordered PyPedal pedigree object.
# @return 0 for failure and 1 for success.
# @defreturn integer
def assign_sexes(pedobj):
    try:
        if pedobj.kw['messages'] == 'verbose':
            print '[NOTE]: pyp_utils/assign_sexes() assigning a sex to all animals in pedigree %s.' % (pedobj.kw['pedname'])
        for _m in pedobj.pedigree:
            if int(_m.sireID) == 0 and int(_m.damID) == 0:
                pass
            elif int(_m.sireID) == 0:
                if pedobj.pedigree[int(_m.damID)-1].sex != 'f':
                    if pedobj.kw['debug_messages']:
                        print '\t\tAnimal %s has sex %s' % (_m.damID,pedobj.pedigree[int(_m.damID)-1].sex)
                        print '\t\tAnimal %s sex set to \'f\'' % (_m.damID)
                    pedobj.pedigree[int(_m.damID)-1].sex = 'f'
            elif int(_m.damID) == 0:
                if pedobj.pedigree[int(_m.sireID)-1].sex != 'm':
                    if pedobj.kw['debug_messages']:
                        print '\t\tAnimal %s sex set to \'m\'' % (_m.sireID)
                        print '\t\tAnimal %s has sex %s' % (_m.sireID,pedobj.pedigree[int(_m.sireID)-1].sex)
                    pedobj.pedigree[int(_m.sireID)-1].sex = 'm'
            else:
                if pedobj.pedigree[int(_m.damID)-1].sex != 'f':
                    if pedobj.kw['debug_messages']:
                        print '\t\tAnimal %s has sex %s' % (_m.damID,pedobj.pedigree[int(_m.damID)-1].sex)
                        print '\t\tAnimal %s sex set to \'f\'' % (_m.damID)
                    pedobj.pedigree[int(_m.damID)-1].sex = 'f'
                if pedobj.pedigree[int(_m.sireID)-1].sex != 'm':
                    if pedobj.kw['debug_messages']:
                        print '\t\tAnimal %s has sex %s' % (_m.sireID,pedobj.pedigree[int(_m.sireID)-1].sex)
                        print '\t\tAnimal %s sex set to \'m\'' % (_m.sireID)
                    pedobj.pedigree[int(_m.sireID)-1].sex = 'm'
        logging.info('pyp_utils/assign_sexes() assigned sexes in pedigree %s' % (pedobj.kw['pedname']))
        return 1
    except:
        logging.error('pyp_utils/assign_sexes() was unable to assign sexes in pedigree %s' % (pedobj.kw['pedname']))
        return 0

##
# assign_offspring() assigns offspring to their parent(s)'s unknown sex offspring list (well, dictionary).
# @param myped An instance of a NewPedigree object.
# @return 0 for failure and 1 for success.
# @defreturn integer
def assign_offspring(pedobj):
    try:
        if pedobj.kw['messages'] == 'debug':
            print '[NOTE]: pyp_utils/assign_offspring() assigning offspring to all parents in pedigree %s.' % (species, pedobj.kw['pedname'])
        for _m in pedobj.pedigree:
            pedobj.pedigree[int(_m.animalID)-1].sons = {}
            pedobj.pedigree[int(_m.animalID)-1].daus = {}
            pedobj.pedigree[int(_m.animalID)-1].unks = {}
        if 'x' not in pedobj.kw['pedformat']:
            for _m in pedobj.pedigree:
                if int(_m.sireID) == 0 and int(_m.damID) == 0:
                    pass
                elif int(_m.sireID) == 0:
                    pedobj.pedigree[int(_m.damID)-1].unks[_m.animalID] = _m.animalID
                elif int(_m.damID) == 0:
                    pedobj.pedigree[int(_m.sireID)-1].unks[_m.animalID] = _m.animalID
                else:
                    pedobj.pedigree[int(_m.damID)-1].unks[_m.animalID] = _m.animalID
                    pedobj.pedigree[int(_m.sireID)-1].unks[_m.animalID] = _m.animalID
        else:
            # We purportedly know animal sexes, so put the offspring in the correct
            # lists.
            for _m in pedobj.pedigree:
                if _m.sex == 'm' or _m.sex == 'M':
                    if int(_m.sireID) != 0:
                        #print 'Sire %s has son %s' % (_m.sireID, _m.animalID)
                        pedobj.pedigree[int(_m.sireID)-1].sons[_m.animalID] = _m.animalID
                    if int(_m.damID) != 0:
                        #print 'Dam %s has son %s' % (_m.damID, _m.animalID)
                        pedobj.pedigree[int(_m.damID)-1].sons[_m.animalID] = _m.animalID
                elif _m.sex == 'f' or _m.sex == 'F':
                    if int(_m.sireID) != 0:
                        #print 'Sire %s has daughter %s' % (_m.sireID, _m.animalID)
                        pedobj.pedigree[int(_m.sireID)-1].daus[_m.animalID] = _m.animalID
                    if int(_m.damID) != 0:
                        #print 'Dam %s has daughter %s' % (_m.sireID, _m.animalID)
                        pedobj.pedigree[int(_m.damID)-1].daus[_m.animalID] = _m.animalID
                else:
                    if int(_m.sireID) != 0:
                        #print 'Sire %s has unknown %s' % (_m.sireID, _m.animalID)
                        pedobj.pedigree[int(_m.sireID)-1].unks[_m.animalID] = _m.animalID
                    if int(_m.damID) != 0:
                        #print 'Dam %s has unknown %s' % (_m.sireID, _m.animalID)
                        pedobj.pedigree[int(_m.damID)-1].unks[_m.animalID] = _m.animalID
        logging.info('pyp_utils/assign_offspring() assigned offspring in pedigree %s' % (pedobj.kw['pedname']))
        return 1
    except:
        logging.error('pyp_utils/assign_offspring() was unable to assign offspring in pedigree %s' % (pedobj.kw['pedname']))
        return 0

##
# reorder() renumbers a pedigree such that parents precede their offspring in the
# pedigree.  In order to minimize overhead as much as is reasonably possible,
# a list of animal IDs that have already been seen is kept.  Whenever a parent
# that is not in the seen list is encountered, the offspring of that parent is
# moved to the end of the pedigree.  This should ensure that the pedigree is
# properly sorted such that all parents precede their offspring.  myped is
# reordered in place.  reorder() is VERY slow, but I am pretty sure that it works
# correctly.
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write the reordered pedigree to a file (yes|no).
# @return A reordered PyPedal pedigree.
# @defreturn list
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
#     print 'Pedigree contains %s animals.' % (l)
    pedordered = 0  # the pedigree is not known to be ordered
    passnum = 0     # we are going to count how many passes through the pedigree are needed
                    # to sort it

#     for i in range(l):
#         print '%s\t%s\t%s' % (myped[i].animalID, myped[i].sireID, myped[i].damID)
#     print '='*100

    while(1):
        #
        # Loop over the pedigree.  Whenever a parent follows their offspring in the
        # pedigree, move the child to the end of the pedigree.  Continue until all parents precede
        # their offspring.
        #
        #if ( passnum == 0 ) or ( passnum % 10 == 0 ):
        #print '-'*100
        #print '...%s' % (passnum)

        order = []
        _sorted_counter = 0
        _noparents_counter = 0

        for i in range(l):
            order.append(int(myped[i].animalID))
#         print order

        for i in range(l):
            if int(myped[i].sireID) > 0 and order.index(int(myped[i].sireID)) > order.index(int(myped[i].animalID)):
                _a = myped[i]
                # If the sire is after the animal in the index, insert the animal ahead of the sire.
                myped.insert(order.index(int(myped[i].sireID))+1, myped[i])
#                 print '\tMoving animal %s ahead of its sire (%s).' % ( myped[i].animalID, myped[i].sireID )
                # Add the animal's ID to the order list to update its location in the pedigree
                order.insert(order.index(int(myped[i].sireID))+1, int(myped[i].animalID))
                # Delete the animal's original (first) record in the pedigree file.
                del myped[i]
                # Delete the animal's original (first) record in the order list.
                del order[order.index(int(_a.animalID))]

            if int(myped[i].damID) > 0 and order.index(int(myped[i].damID)) > order.index(int(myped[i].animalID)):
                _a = myped[i]
                # If the dam is after the animal in the index, insert the animal ahead of the dam.
                myped.insert(order.index(int(myped[i].damID))+1, myped[i])
#                 print '\tMoving animal %s ahead of its dam (%s).' % ( myped[i].animalID, myped[i].damID )
                # Add the animal's ID to the order list to update its location in the pedigree
                order.insert(order.index(int(myped[i].damID))+1, int(myped[i].animalID))
                # Delete the animal's original (first) record in the pedigree file.
                del myped[i]
                # Delete the animal's original (first) record in the order list.
                del order[order.index(int(_a.animalID))]

#         print order
        for i in range(l):

            if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
                #pedordered = 0
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                _noparents_counter = _noparents_counter + 1
                pass
            elif int(myped[i].sireID) != 0 and order.index(int(myped[i].animalID)) < order.index(int(myped[i].sireID)):
                #pedordered = 0
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                pass
            elif int(myped[i].damID) != 0 and order.index(int(myped[i].animalID)) < order.index(int(myped[i].damID)):
                #pedordered = 0
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                pass
            else:
#                 print 'IDs\t%s\t%s\t%s\t' % ( int(myped[i].animalID), int(myped[i].sireID), int(myped[i].damID) ),
#                 if int(myped[i].sireID) == 0 and int(myped[i].damID) == 0:
#                     print 'Loc\t%s\t-\t-\t***' % ( order.index(int(myped[i].animalID)) )
#                 else:
#                     print 'Loc\t%s\t%s\t%s\t***' % ( order.index(int(myped[i].animalID)), order.index(int(myped[i].sireID)), order.index(int(myped[i].damID)) )
                _sorted_counter = _sorted_counter + 1

#         print 'Sorted: %s' % ( _sorted_counter )
#         print 'No parents: %s' % ( _noparents_counter )
#         print 'Length: %s' % ( l )

        if _sorted_counter == ( l - _noparents_counter ):
            break
        else:
            passnum = passnum + 1

#     print '='*100
#     for i in range(l):
#         print '%s\t%s\t%s' % (myped[i].animalID, myped[i].sireID, myped[i].damID)

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
            aout.write('%s,%s,%s\n' % myped[l].animalID,myped[l].sireID,myped[l].damID)
        aout.close()

        del order, seen, kill

    return myped

##
# fast_reorder() renumbers a pedigree such that parents precede their offspring in
# the pedigree.  In order to minimize overhead as much as is reasonably possible,
# a list of animal IDs that have already been seen is kept.  Whenever a parent
# that is not in the seen list is encountered, the offspring of that parent is
# moved to the end of the pedigree.  This should ensure that the pedigree is
# properly sorted such that all parents precede their offspring.  myped is
# reordered in place.  fast_reorder() uses dictionaries to renumber the pedigree
# based on paddedIDs.
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write the reordered pedigree to a file (yes|no).
# @param debug Flag to indicate whether or not debugging messages are written to STDOUT.
# @return A reordered PyPedal pedigree.
# @defreturn list
def fast_reorder(myped,filetag='_new_reordered_',io='no',debug=0):
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
    # <kludge>
    myped.reverse()
    # </kludge>
    if debug == 1:
        print '\tPedigree contains %s animals.' % (l)
        print '\tMaking a dictionary of animal objects'
        print '\tMaking a list of padded animal IDs'
    for i in range(l):
        if debug == 1:
            print '\tDEBUG\tID %s: %s = %s %s %s' % (i,myped[i].animalID,myped[i].paddedID,myped[i].sireID,myped[i].damID)
        animalmap[myped[i].paddedID] = myped[i]
        idlist.append(int(myped[i].paddedID))
#    if debug:
#   print '='*80
#   print 'Printing unsorted ID list...'
#   print '%s' % (idlist)
#   print '='*80

    #print '\tSorting padded animal IDs'
    idlist.sort()
#    if debug == 1:
#   print '='*80
#        print 'Printing sorted ID list...'
#        print '%s' % (idlist)
#        print '='*80
    myped = []
    #print '\tReforming myped...'
    l = len(idlist)
    if debug == 1:
        print '[DEBUG]: %s elements in idlist' % (l)
        print '[DEBUG]: Printing reordered pedigree...'
    #print animalmap
    for i in range(len(idlist)):
        #print i,  ' ', idlist[i]
        #print idlist[i], animalmap[str(idlist[i])]
        myped.append(animalmap[str(idlist[i])])
    if debug == 1:
        print '\t[DEBUG]:\tID %s: %s = %s' % (i,myped[i].animalID,myped[i].paddedID)
    if io == 'yes':
        # Write the reordered pedigree to a file and return the ordered pedigree.
        # Note that the reordered pedigree is currently only written in the 'asd'
        # format, regardless of the format of the original file.
        a_outputfile = '%s%s%s' % (filetag,'_reord','.ped')
        aout = open(a_outputfile,'w')
        aname = '# FILE: %s\n' % (a_outputfile)
        aout.write(aname)
        aout.write('# REORDERED pedigree produced by PyPedal using fast_reorder().\n')
        aout.write('% asd\n')
        for l in range(len(myped)):
            aout.write('%s,%s,%s\n' % myped[l].animalID,myped[l].sireID,myped[l].damID)
        aout.close()
    return myped

##
# renumber() takes a pedigree as input and renumbers it such that the oldest
# animal in the pedigree has an ID of '1' and the n-th animal has an ID of 'n'.  If the
# pedigree is not ordered from oldest to youngest such that all offspring precede their
# offspring, the pedigree will be reordered.  The renumbered pedigree is written to disc in
# 'asd' format and a map file that associates sequential IDs with original IDs is also
# written.
# @param myped A PyPedal pedigree object.
# @param filetag A descriptor prepended to output file names.
# @param io Indicates whether or not to write the renumbered pedigree to a file (yes|no).
# @param outformat Flag to indicate whether or not ro write an asd pedigree (0) or a full pedigree (1).
# @param debug Flag to indicate whether or not progress messages are written to stdout.
# @return A reordered PyPedal pedigree.
# @defreturn list
def renumber(myped,filetag='_renumbered_',io='no',outformat='0',debug=0):
    """renumber() takes a pedigree as input and renumbers it such that the oldest
    animal in the pedigree has an ID of '1' and the n-th animal has an ID of 'n'.  If the
    pedigree is not ordered from oldest to youngest such that all offspring precede their
    offspring, the pedigree will be reordered.  The renumbered pedigree is written to disc in
    'asd' format and a map file that associates sequential IDs with original IDs is also
    written."""

    if debug == 1:
        print '[DEBUG]: Pedigree of size %s passed to renumber()' % (len(myped))
    #for i in range(len(myped)):
    #   print myped[i].animalID,
    #print

    # In the dictionary id_map, the old IDs are the keys and the
    # new IDs are the values.
    id_map = {}
    idnum = 1       # starting ID number for renumbered IDs
    for l in range(len(myped)):
        if debug == 1:
            if l == 0:
                print '[DEBUG]: Renumbering the pedigree...'
            if numarray.fmod(l,10000) == 0:
                print'\t%s ' % (l)
            print '[DEBUG]: An:%s (%s)\tSire: %s\tDam: %s' % (myped[l].animalID,myped[l].paddedID,myped[l].sireID,myped[l].damID)
        id_map[myped[l].animalID] = idnum
        #myped[l].animalID = id_map[myped[l].animalID]
        if debug == 1:
            print '\t[DEBUG]: Renumbering animal from %s to %s (iter %s)' % (myped[l].animalID,idnum,l)
        myped[l].renumberedID = idnum
        myped[l].animalID = idnum
        # We cannot forget to renumber parents, too!
        s = myped[l].sireID
        if s != '0' and s != 0:
        # This is a hack to deal with offspring that have birthdates which precede their parents'.
            try:
                if debug == 1:
                    print '\t\t[DEBUG]: Renumbering sire from %s to %s' % (s,id_map[s])
                myped[l].sireID = id_map[s]
            except:
                myped[l].sireID = 0
        d = myped[l].damID
        if d != '0' and d != 0:
        # This is a hack to deal with offspring that have birthdates which precede their parents'.
            try:
                if debug == 1:
                    print '\t\t[DEBUG]: Renumbering dam from %s to %s' % (d,id_map[d])
                myped[l].damID = id_map[d]
            except:
                myped[l].damID = 0
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
            if outformat == '0' or outformat == 0:
                pout.write('%s,%s,%s\n' % myped[l].animalID,myped[l].sireID,myped[l].damID)
            else:
                pout.write('%s,%s,%s,%s,%s,%s,%s\n' % myped[l].animalID,myped[l].sireID,myped[l].damID,myped[l].by,myped[l].sex,myped[l].fa,myped[l].gen)
        pout.close()
    # Write the old ID -> new ID mapping to a file
    map_outputfile = '%s%s%s' % (filetag,'_id_map','.map')
    #print '[DEBUG]: ID map file name is %s' % (map_outputfile)
    mout = open(map_outputfile,'w')
    mname = '# FILE: %s\n' % (map_outputfile)
    mout.write(mname)
    mout.write('# Renumbered ID to Old ID mapping produced by PyPedal.\n')
    mout.write('# The lefthand column contains the original IDs.\n')
    mout.write('# The righthand column contains the renumbered IDs.\n')
    mout.write('# Old ID\tRenum ID\n')
    k = id_map.keys()
    v = id_map.values()
    for l in range(len(id_map)):
        mout.write('%s,%s\n' % (k[l],v[l]))
        #print 'Old ID = %s,  New ID = %s' % (k[l],v[l])
    mout.close()
    #print 'ID map in renumber():%s' % (id_map)
    return myped

##
# load_id_map() reads an ID map from the file generated by pyp_utils/renumber()
# into a dictionary.  There is a VERY similar function, pyp_io/id_map_from_file(), that
# is deprecated because it is much more fragile that this procedure.
# @param filetag A descriptor prepended to output file names that is used to determine the input file name.
# @return A dictionary whose keys are renumbered IDs and whose values are original IDs or an empty dictionary (on failure).
# @defreturn dictionary
def load_id_map(filetag='_renumbered_'):
    try:
        _infile = '%s%s%s' % (filetag,'_id_map','.map')
        mapin = open(_infile,'r')
        idmap = {}
        while 1:
            line = mapin.readline()
            if not line:
                break
            else:
                line = string.strip(line[:-1])
                if line[0] == '#':
                    pass
                else:
                    _line = string.split(line,',')
                    if len(_line) != 2:
                        print '[ERROR]: Invalid number of elements in line read from ID map file (%s)' % (_line)
                        break
                    else:
                        idmap[int(_line[1])] = int(_line[0])
        mapin.close()
        return idmap
    except:
        #print '[ERROR]: Could not open the ID map file %s in load_id_map()!' % (_infile)
        #sys.exit(0)
        return {}

##
# delete_id_map() checks to see if an ID map for the given filetag exists.  If the file exists, it is
# deleted.
# @param filetag A descriptor prepended to output file names that is used to determine name of the file to delete.
# @return A flag indicating whether or not the file was successfully deleted (0|1)
# @defreturn integer
def delete_id_map(filetag='_renumbered_'):
    try:
        _infile = '%s%s%s' % (filetag,'_id_map','.map')
        if _infile in os.listdir('.'):
            os.remove(_infile)
        return 1
    except:
        return 0

##
# trim_pedigree_to_year() takes pedigrees and removes all individuals who were not born
# in birthyear 'year'.
# @param myped A PyPedal pedigree object.
# @param year A birthyear.
# @return A pedigree containing only animals born in the given birthyear or an ampty list (on failure).
# @defreturn list
def trim_pedigree_to_year(pedobj,year):
    # trim_pedigree_to_year() takes pedigrees and removes all individuals
    # who were not born in birthyear 'year'.  The reduced (trimmed) pedigree
    # is returned.
    try:
        indices = []
        modped = pedobj.pedigree[:]
        for l in range(len(modped)):
            if int(modped[l].by) == int(year):
                pass
            else:
                indices.append(l)
        indices.reverse()
        for i in range(len(indices)):
            del modped[indices[i]]
        return modped
    except:
        return []

##
# pedigree_range() takes a renumbered pedigree and removes all individuals
# with a renumbered ID > n.  The reduced pedigree is returned.  Assumes that
# the input pedigree is sorted on animal key in ascending order.
# @param myped A PyPedal pedigree object.
# @param n A renumbered animalID.
# @return A pedigree containing only animals born in the given birthyear of an ampty list (on failure).
# @defreturn list
def pedigree_range(pedobj,n):
    # pedigree_range() takes a renumbered pedigree and removes all individuals
    # with a renumbered ID > n.  The reduced pedigree is returned.  Assumes that
    # the input pedigree is sorted on animal key in ascending order.
    try:
        modped = []
        for i in range(n):
            modped.append(pedobj.pedigree[i])
            return modped
    except:
        return []

##
# sort_dict_by_keys() returns a dictionary where the values in the dictionary
# in the order obtained by sorting the keys.  Taken from the routine sortedDictValues3
# in the "Python Cookbook", p. 39.
# @param mydict A non-empty Python dictionary.
# @return The input dictionary with keys sorted in ascending order or an empty dictionary (on failure).
# @defreturn dictionary
def sort_dict_by_keys(mydict):
    try:
        if len(mydict) == 0:
            return mydict
        else:
            keys = mydict.keys()
            keys.sort()
            return map(mydict.get, keys)
    except:
        return {}

##
# sort_dict_by_values() returns a dictionary where the keys in the dictionary
# are sorted ascending value, first on value and then on key within value.  The
# implementation was taken from John Hunter's contribution to a newsgroup thread:
# http://groups-beta.google.com/group/comp.lang.python/browse_thread/thread/bbc259f8454e4d3f/cc686f4cd795feb4?q=python+%22sorted+dictionary%22&rnum=1&hl=en#cc686f4cd795feb4
# @param mydict A non-empty Python dictionary.
# @return A list of tuples sorted in ascending order.
# @defreturn list
def sort_dict_by_values( first, second ):
    c1 = cmp(first[1], second[1])
    if c1!=0:
        return c1
    return cmp(first[0], second[0])
##
# simple_histogram_dictionary() returns a dictionary containing a simple, text histogram.
# The input dictionary is assumed to contain keys which are distinct levels and values
# that are counts.
# @param mydict A non-empty Python dictionary.
# @param histchar The character used to draw the histogram (default is '*').
# @param histstep Used to determine the number of bins (stars) in the diagram.
# @return A dictionary containing the histogram by level or an empty dictionary (on failure).
# @defreturn dictionary
def simple_histogram_dictionary(mydict,histchar='*',histstep=5):
    try:
        hist_dict = {}
        hist_sum = 0.
        if histstep < 0 or histstep > 100:
            histstep = 5
        for k in mydict.keys():
            hist_sum = hist_sum + mydict[k]
        #print '[DEBUG]: %s' % (hist_sum)
        for k in mydict.keys():
            _freq = ( float(mydict[k]) / float(hist_sum) ) * 100.
            _v = around(_freq,0)
            _n_stars = int( around( (_v / float(histstep)),0 ) )
            if _n_stars > 0:
                hist_dict[k] = '%s%s' % (histchar*_n_stars,' '*(20-_n_stars))
            else:
                hist_dict[k] = '%s' % (' '*20)
        return hist_dict
    except:
        return {}

##
# reverse_string() reverses the input string and returns the reversed version.
# @param mystring A non-empty Python string.
# @return The input string with the order of its characters reversed.
# @defreturn string
def reverse_string(mystring):
    try:
        if len(mystring) < 2:
            return mystring
        else:
            mystringreversed = []
            for l in range(len(mystring)):
                mystringreversed.append(mystring[l])
                mystringreversed.reverse().join()
            return mystringreversed
    except:
        return 0

##
# pyp_nice_time() returns the current date and time formatted as, e.g.,
# Wed Mar 30 10:26:31 2005.
# @param None
# @return A string containing the formatted date and time.
# @defreturn string
def pyp_nice_time():
    try:
        return time.asctime(time.localtime(time.time()))
    except:
        return 0

##
# string_to_table_name() takes an arbitrary string and returns a string that
# is safe to use as an SQLite table name.
# @param instring A string that will be converted to an SQLite-safe table name.
# @return A string that is safe to use as an SQLite table name.
# @defreturn string
def string_to_table_name(instring):
    try:
        # This list comprehension idea is taken from the Python Cookbook:
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/59857
        allowed_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
        outstring = ''.join([c for c in instring if c in allowed_chars])
        return outstring
    except:
        return instring

##
# pyp_datestamp() returns a datestamp, as a string, of the format
# YYYYMMDDHHMMSS.
# @param None
# @return A 14-character string containing the datestamp.
# @defreturn string
def pyp_datestamp():
    try:
        #return time.asctime(time.localtime(time.time()))
        return time.strftime('%Y%m%d%H%M%S', (time.localtime(time.time())))
    except:
        return '00000000000000'