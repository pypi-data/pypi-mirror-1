###############################################################################
# NAME: pyp_jbc.py
# VERSION: 1.0a1 (22NOVEMBER2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL`
###############################################################################
# FUNCTIONS:
#     get_color_32()
#     color_pedigree()
#     draw_colored_pedigree()
###############################################################################

##
# pyp_template provides a skeleton on which user-defined modules may be built.
##

import logging
import math
import pyp_graphics
import pyp_network
import pyp_utils

##
# get_color_32() Converts a float value to one of a continuous range of colors
# using recipe 9.10 from the Python Cookbook.
# @param a Float value to convert to a color.
# @param cmin Minimum value in array (?).
# @param cmax Maximum value in array (?).
# @return An RGB triplet.
# @defreturn integer
def get_color_32(a,cmin,cmax):
    """\
    Convert a float value to one of a continuous range of colors.
    Rewritten to use recipe 9.10 from the O'Reilly Python Cookbook.
    """
    try:
        a = float(a-cmin)/(cmax-cmin)
    except ZeroDivisionError:
        a=0.5 # cmax == cmin
    blue = min((max((4*(0.75-a),0.)),1.))
    red = min((max((4*(a-0.25),0.)),1.))
    green = min((max((4*math.fabs(a-0.5)-1.,0)),1.))
    _r = '%2x' % int(255*red)
    if _r[0] == ' ':
        _r = '0%s' % _r[1]
    _g = '%2x' % int(255*green)
    if _g[0] == ' ':
        _g = '0%s' % _g[1]
    _b = '%2x' % int(255*blue)
    if _b[0] == ' ':
        _b = '0%s' % _b[1]
    _triple = '#%s%s%s' % (_r,_g,_b)
    return _triple

##
# color_pedigree() forms a graph object from a pedigree object and determines the
# proportion of animals in a pedigree that are descendants of each animal in the
# pedigree.  The results will be used to feed draw_colored_pedigree().
# @param pedobj A PyPedal pedigree object.
# @return A 1 for success and a 0 for failure.
# @defreturn integer
def color_pedigree(pedobj):
    _pedgraph = pyp_network.ped_to_graph(pedobj)
    _dprop = {}
    # Walk the pedigree and compute proportion of animals in the pedigree that are
    # descended from each animal.
    for _p in pedobj.pedigree:
        _dcount = pyp_network.find_descendants(_pedgraph,_p.animalID,[])
        if len(_dcount) < 1:
            _dprop[_p.animalID] = 0.0
        else:
            _dprop[_p.animalID] = float(len(_dcount)) / float(pedobj.metadata.num_records)
    #print '_dprop\t%s' % (_dprop)
    del(_pedgraph)
    _gfilename = '%s_colored' % (pyp_utils.string_to_table_name(pedobj.metadata.name))
    draw_colored_pedigree(pedobj, _dprop, gfilename=_gfilename,
        gtitle='Colored Pedigree', gorient='p', gname=1, gdirec='',
        gfontsize=12, garrow=0, gtitloc='b')

##
# draw_colored_pedigree() uses the pydot bindings to the graphviz library to produce a
# directed graph of your pedigree with paths of inheritance as edges and animals as
# nodes.  If there is more than one generation in the pedigree as determind by the "gen"
# attributes of the animals in the pedigree, draw_pedigree() will use subgraphs to try
# and group animals in the same generation together in the drawing.  Nodes will be colored
# based on the number of outgoing connections (number of offspring).
# @param pedobj A PyPedal pedigree object.
# @param shading A dictionary mapping animal IDs to levels that will be used to color nodes.
# @param gfilename The name of the file to which the pedigree should be drawn.
# @param gtitle The title of the graph.
# @param gsize The size of the graph: 'f': full-size, 'l': letter-sized page.
# @param gdot Whether or not to write the dot code for the pedigree graph to a file (can produce large files).
# @param gorient The orientation of the graph: 'p': portrait, 'l': landscape.
# @param gdirec Direction of flow from parents to offspring: 'TB': top-bottom, 'LR': left-right, 'RL': right-left.
# @param gname Flag indicating whether ID numbers (0) or names (1) should be used to label nodes.
# @param gfontsize Integer indicating the typeface size to be used in labelling nodes.
# @param garrow Flag indicating whether or not arrowheads should be drawn.
# @param gtitloc Indicates if the title be drawn or above ('t') or below ('b') the graph.
# @param gtitjust Indicates if the title should be center- ('c'), left- ('l'), or right-justified ('r').
# @return A 1 for success and a 0 for failure.
# @defreturn integer
def draw_colored_pedigree(pedobj, shading, gfilename='pedigree', gtitle='My_Pedigree', gformat='jpg', gsize='f', gdot='1', gorient='l', gdirec='', gname=0, gfontsize=10, garrow=1, gtitloc='b', gtitjust='c'):
    from pyp_utils import string_to_table_name
    _gtitle = string_to_table_name(gtitle)

    if gtitloc not in ['t','b']:
        gtitloc = 'b'
    if gtitjust not in ['c','l','r']:
        gtitjust = 'c'

#     try:
    import pydot

    # Build a list of generations -- if we have more than on, we can use the
    # "rank=same" option in dot to get nicer output.
    gens = []
    for i in range(len(pedobj.pedigree)):
        g = pedobj.pedigree[i].gen
        if g in gens:
            pass
        else:
            gens.append(g)
    # Set some properties for the graph.
    g = pydot.Dot(label=gtitle, labelloc=gtitloc, labeljust=gtitjust, graph_name=_gtitle, type='graph', strict=False, suppress_disconnected=True, simplify=True)

    # Make sure that gfontsize has a valid value.
    try:
        gfontsize = int(gfontsize)
    except:
        gfontsize = 10
    if gfontsize < 10:
        gfontsize = 10
    gfontsize = str(gfontsize)
#     print 'gfontsize = %s' % (gfontsize)
    g.set_page("8.5,11")
    g.set_size("7.5,10")
    if gorient == 'l':
        g.set_orientation("landscape")
    else:
        g.set_orientation("portrait")
    if gsize != 'l':
        g.set_ratio("auto")
    if gdirec == 'RL':
        g.set_rankdir('RL')
    elif gdirec == 'LR':
        g.set_rankdir('LR')
    else:
        pass
    g.set_center('true')
    g.set_concentrate('true')
    g.set_ordering('out')
    if gformat not in g.formats:
        gformat = 'jpg'
    # If we do not have any generations, we have to draw a less-nice graph.
    if len(gens) <= 1:
        for _m in pedobj.pedigree:
            # Add a node for the current animal and set some properties.
            if gname:
                _node_name = _m.name
            else:
                _node_name = _m.animalID
            _an_node = pydot.Node(_node_name)
            _an_node.set_fontname('Helvetica')
            # _an_node.set_fontsize('10')
            _an_node.set_fontsize(gfontsize)
            _an_node.set_height('0.35')
            if _m.sex == 'M' or _m.sex == 'm':
                _an_node.set_shape('box')
            elif _m.sex == 'F' or _m.sex == 'f':
                _an_node.set_shape('ellipse')
            else:
                pass
#             try:
            _color = get_color_32(shading[_m.animalID],0.0,1.0)
#             print _color
#             except:
#                 _color = pyp_graphics.rmuller_get_color(0.0,0.0,1.0)
            _an_node.set_style('filled')
            _an_node.set_color(_color)
            g.add_node(_an_node)
            # Add the edges to the parent nodes, if any.
            if int(_m.sireID) != 0:
                if gname:
                    if garrow:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].name, _m.name))
                    else:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].name, _m.name, dir='none'))
                else:
                    if garrow:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].originalID,_m.originalID))
                    else:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].originalID,_m.originalID, dir='none'))
            if int(_m.damID) != 0:
                if gname:
                    if garrow:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].name, _m.name))
                    else:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].name, _m.name, dir='none'))
                else:
                    if garrow:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].originalID,_m.originalID))
                    else:
                        g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].originalID,_m.originalID, dir='none'))
    # Otherwise we can draw a nice graph.
    else:
        for _g in gens:
            _sg_anims = []
            _sg_name = 'sg%s' % (_g)
            sg = pydot.Subgraph(graph_name=_sg_name, suppress_disconnected=True, simplify=True)
            sg.set_simplify(True)
            for _m in pedobj.pedigree:
                if int(_m.gen) == int(_g):
                    _sg_anims.append(_m.animalID)
                # Add a node for the current animal and set some properties.
                if gname:
                    _node_name = _m.name
                else:
                    _node_name = _m.animalID
                _an_node = pydot.Node(_node_name)
                _an_node.set_fontname('Helvetica')
                # _an_node.set_fontsize('10')
                _an_node.set_fontsize(gfontsize)
                _an_node.set_height('0.35')
                if _m.sex == 'M' or _m.sex == 'm':
                    _an_node.set_shape('box')
                elif _m.sex == 'F' or _m.sex == 'f':
                    _an_node.set_shape('ellipse')
                else:
                    pass
#                 try:
                _color = get_color_32(shading[_m.animalID],0.0,1.0)
#                 print _color
#                 except:
#                     _color = pyp_graphics.rmuller_get_color(0.0,0.0,1.0)
                _an_node.set_style('filled')
                _an_node.set_color(_color)
                sg.add_node(_an_node)
                # Add the edges to the parent nodes, if any.
                if int(_m.sireID) != 0:
                    if gname:
                        if garrow:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].name,_m.name))
                        else:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].name,_m.name, dir='none'))
                    else:
                        if garrow:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].originalID,_m.originalID))
                        else:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].originalID,_m.originalID, dir='none'))
                if int(_m.damID) != 0:
                    if gname:
                        if garrow:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].name,_m.name))
                        else:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].name,_m.name, dir='none'))
                    else:
                        if garrow:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].originalID,_m.originalID))
                        else:
                            sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].originalID,_m.originalID, dir='none'))
            if len(_sg_anims) > 0:
                _sg_list = ''
                for _a in _sg_anims:
                    if len(_sg_list) == 0:
                        _sg_list = 'same,%s' % (_a)
                    else:
                        _sg_list = '%s,%s' % (_sg_list,_a)
            sg.set_rank(_sg_list)
            g.add_subgraph(sg)
    # For large graphs it is nice to write out the .dot file so that it does not have to be recreated
    # whenever draw_pedigree is called.  Especially when I am debugging.  :-)
    if gdot:
        dfn = '%s.dot' % (gfilename)
#             try:
        g.write(dfn)
#             except:
#                 pass
    # Write the graph to an output file.
    outfile = '%s.%s' % (gfilename,gformat)
    print outfile
    #g.write_jpeg(outfile, prog='dot')
    g.write(outfile,prog='dot',format=gformat)
    return 1
#     except:
#         return 0
