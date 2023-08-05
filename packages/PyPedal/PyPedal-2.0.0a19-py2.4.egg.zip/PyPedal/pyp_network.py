#!/usr/bin/python

###############################################################################
# NAME: pyp_network.py
# VERSION: 2.0.0a19 (26OCTOBER2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   ped_to_graph()
#   find_ancestors()
#   find_descendants()
#   immediate_family()
#   count_offspring()
#   offspring_influence()
#   most_influential_offspring()
###############################################################################

##
# pyp_network contains a set of procedures for working with pedigrees as directed
# graphs.
##

import logging

try:
    import networkx
except ImportError:
    logging.error('The networkx module could not be imported in pyp_network.  Routines using networkx functionality are not available.')

##
# ped_to_graph() Takes a PyPedal pedigree object and returns a networkx XDiGraph
# object.
# @param pedobj A PyPedal pedigree object.
# @param oid Flag indicating if original (1) or renumbered (0) IDs should be used.
# @return DiGraph object
# @defreturn graph
def ped_to_graph(pedobj,oid = 0):
    #print 'Entered ped_to_graph()'
    l = len(pedobj.pedigree)
    G = networkx.DiGraph(name=pedobj.kw['pedname'], selfloops=False, multiedges=True)
    for i in range(l):
        # The order in which we pass arguments to add_edge() is important -- the
        # parent has to be the first argument and the offspring the second if the
        # graph is to be ordered in the correct direction.
        if int(pedobj.pedigree[i].sireID) != 0:
            if oid:
                G.add_edge(pedobj.pedigree[int(pedobj.pedigree[i].sireID)].originalID, int(pedobj.pedigree[i].originalID))
            else:
                G.add_edge(int(pedobj.pedigree[i].sireID), int(pedobj.pedigree[i].animalID))
        if int(pedobj.pedigree[i].damID) != 0:
            if oid:
                G.add_edge(pedobj.pedigree[int(pedobj.pedigree[i].damID)].originalID, int(pedobj.pedigree[i].originalID))
            else:
                G.add_edge(int(pedobj.pedigree[i].damID), int(pedobj.pedigree[i].animalID))
    return G

##
# find_ancestors() identifies the ancestors of an animal and returns them in a list.
# @param pedgraph An instance of a networkx DiGraph.
# @param anid The animal for whom ancestors are to be found.
# @param _ancestors The list of ancestors already found.
# @return List of ancestors of anid.
# @defreturn list
def find_ancestors(pedgraph,anid,_ancestors=[]):
    try:
        _pred = pedgraph.predecessors(anid)
        for _p in _pred:
            if _p not in _ancestors:
                _ancestors.append(_p)
                find_ancestors(pedgraph,_p,_ancestors)
    except:
        pass
    return _ancestors

##
# find_descendants() identifies the descendants of an animal and returns them in a list.
# @param pedgraph An instance of a networkx DiGraph.
# @param anid The animal for whom descendants are to be found.
# @param _descendants The list of descendants already found.
# @return List of descendants of anid.
# @defreturn list
def find_descendants(pedgraph,anid,_descendants=[]):
    try:
        #print '\t%s\t%s' % ( anid, _descendants )
        _desc = pedgraph.successors(anid)
        for _d in _desc:
            if _d not in _descendants:
                _descendants.append(_d)
                find_descendants(pedgraph,_d,_descendants)
    except:
        pass
    return _descendants

##
# immediate_family() returns parents and offspring of an animal.
# @param pedgraph An instance of a networkx DiGraph.
# @param anid The animal for whom immediate family are to be found.
# @return List of immediate family members of anid.
# @defreturn list
def immediate_family(pedgraph,anid):
    try:
        _family = networkx.neighbors(pedgraph,anid)
    except:
        pass
    return _family

##
# immediate_family() returns the number of offspring of an animal.
# @param pedgraph An instance of a networkx DiGraph.
# @param anid The animal for whom offspring are to be counted.
# @return Count of offspring.
# @defreturn integer
def count_offspring(pedgraph,anid):
    try:
      _count = len(networkx.neighbors(pedgraph,anid)) - len(pedgraph.predecessors(anid))
    except:
        _count = 0
    return _count

##
# offspring_influence() returns the number of grand-children by each child of a given animal.
# @param pedgraph An instance of a networkx DiGraph.
# @param anid The animal for whom grand-progreny are to be counted.
# @return A dictionary of counts of progeny per child.
# @defreturn dictionary
def offspring_influence(pedgraph,anid):
    try:
      _offspring = pedgraph.successors(anid)
      _degrees = networkx.degree(pedgraph, nbunch=_offspring, with_labels=True)
      # Correct for edges contributed by parents
      for _d in _degrees:
          _degrees[_d] = _degrees[_d] - len(pedgraph.predecessors(_d))
    except:
        pass
    return _degrees

##
# most_influential_offspring() returns the most influential offspring of an animal as measured by their number of offspring.
# @param pedgraph An instance of a networkx DiGraph.
# @param anid The animal for whom the most influential offspring is to be found.
# @param resolve Indicates how ties should be handled ('first'|'last'|'all').
# @return The most influential offspring of anid.
# @defreturn dictionary
def most_influential_offspring(pedgraph,anid,resolve='all'):
    try:
        _max_off = -999
        _offid = -999
        _offdict = {}
        if resolve == 'all':
            _tempoffdict = {}
        _offspring = offspring_influence(pedgraph,anid)
        #print _offspring
        for _o in _offspring:
            # If there are ties, return the ID for the first offspring
            # seen with that number of progeny.
            if resolve == 'first':
                if _offspring[_o] > _max_off:
                    _max_off = _offspring[_o]
                    _offid = _o
            # If there are ties, return the ID for the last offspring
            # seen with that number of progeny.
            elif resolve == 'last':
                if _offspring[_o] >= _max_off:
                    _max_off = _offspring[_o]
                    _offid = _o
            # If there are ties, return the IDs for all offspring
            # with the highest number of progeny.
            else:
                if  _offspring[_o] > _max_off:
                    _tempoffdict = {}
                    _tempoffdict[_o] = _offspring[_o]
                    _max_off = _offspring[_o]
                    _offid = _o
                elif _offspring[_o] == _max_off:
                    _tempoffdict[_o] = _offspring[_o]
                    _offid = _o
        if resolve == 'all':
            _offdict = _tempoffdict
        else:
            _offdict[_offid] = _max_off
    except:
        pass
    return _offdict