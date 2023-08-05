#!/usr/bin/python

###############################################################################
# NAME: pyp_graphics.py
# VERSION: 2.0.0a20 (07NOVEMBER2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# FUNCTIONS:
#   rmuller_spy_matrix_pil() [1]
#   rmuller_pcolor_matrix_pil() [1]
#   rmuller_get_color() [1]
#   draw_pedigree()
#   plot_founders_by_year()
#   plot_founders_pct_by_year()
#   plot_line_xy()
#   pcolor_matrix_pylab()
#   spy_matrix_pylab()
###############################################################################
# [1] These routines were taken from the ASPN Python Cookbook
#     (http://aspn.activestate.com/ASPN/Cookbook/Python/) and are used under
#     terms of the license, "Python Cookbook code is freely available for use
#     and review" as I understand it.  I did not write them; Rick Muller
#     properly deserves credit for that.  I THINK Rick's homepage's is:
#     http://www.cs.sandia.gov/~rmuller/.
# Python Cookbook notes:
#     Title: Matlab-like 'spy' and 'pcolor' functions
#     Submitter: Rick Muller (other recipes)
#     Last Updated: 2005/03/02
#     Version no: 1.0
#     Category: Image
#     Description:
#         I really like the 'spy' and 'pcolor' functions, which are useful in viewing
#         matrices. 'spy' prints colored blocks for values that are above a threshold,
#         and 'pcolor' prints out each element in a continuous range of colors.  The
#         attached is a little Python/PIL script that does these functions for Numpy
#         arrays.
#     URL: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/390208
###############################################################################

##
# pyp_graphics contains routines for working with graphics in PyPedal, such as
# creating directed graphs from pedigrees using PyDot and visualizing relationship
# matrices using Rick Muller's spy and pcolor routines
# (http://aspn.activestate.com/ASPN/Cookbook/Python/).
#
# The Python Imaging Library (http://www.pythonware.com/products/pil/),
# matplotlib (http://matplotlib.sourceforge.net/), Graphviz (http://www.graphviz.org/),
# and pydot (http://dkbza.org/pydot.html) are required by one or more routines in this
# module.  They ARE NOT distributed with PyPedal and must be installed by the end-user!
# Note that the matplotlib functionality in PyPedal requires only the Agg backend, which
# means that you do not have to install GTK/PyGTK or WxWidgets/PyWxWidgets just to use
# PyPedal.  Please consult the sites above for licensing and installation information.
##

import logging
import math, string
import pyp_demog

##
# rmuller_spy_matrix_pil() implements a matlab-like 'spy' function to display the
# sparsity of a matrix using the Python Imaging Library.
# @param A Input Numpy matrix (such as a numerator relationship matrix).
# @param fname Output filename to which to dump the graphics (default 'tmp.png')
# @param cutoff Threshold value for printing an element (default 0.1)
# @param do_outline Whether or not to print an outline around the block (default 0)
# @param height The height of the image (default 300)
# @param width The width of the image (default 300)
# @return A list of Animal() objects; a pedigree metadata object.
# @defreturn lists
def rmuller_spy_matrix_pil(A,fname='tmp.png',cutoff=0.1,do_outline=0,
                   height=300,width=300):
    try:
        import Image, ImageDraw
    except:
        return 0
    img = Image.new("RGB",(width,height),(255,255,255))
    draw = ImageDraw.Draw(img)
    n,m = A.shape
    if n > width or m > height:
        raise "Rectangle too big %d %d %d %d" % (n,m,width,height)
    for i in range(n):
        xmin = width*i/float(n)
        xmax = width*(i+1)/float(n)
        for j in range(m):
            ymin = height*j/float(m)
            ymax = height*(j+1)/float(m)
            if abs(A[i,j]) > cutoff:
                if do_outline:
                    draw.rectangle((xmin,ymin,xmax,ymax),fill=(0,0,255),
                        outline=(0,0,0))
                else:
                    draw.rectangle((xmin,ymin,xmax,ymax),fill=(0,0,255))
    img.save(fname)
    return

##
# rmuller_pcolor_matrix_pil() implements a matlab-like 'pcolor' function to
# display the large elements of a matrix in pseudocolor using the Python Imaging
# Library.
# @param A Input Numpy matrix (such as a numerator relationship matrix).
# @param fname Output filename to which to dump the graphics (default 'tmp.png')
# @param do_outline Whether or not to print an outline around the block (default 0)
# @param height The height of the image (default 300)
# @param width The width of the image (default 300)
# @return A list of Animal() objects; a pedigree metadata object.
# @defreturn lists
def rmuller_pcolor_matrix_pil(A,fname='tmp.png',do_outline=0,height=300,width=300):
    try:
        import Image, ImageDraw
    except:
        return 0
    key_dict = {}
    color_cache = {}

    img = Image.new("RGB",(width,height),(255,255,255))
    draw = ImageDraw.Draw(img)

    # For Numeric
    #mina = min(min(A))
    #maxa = max(max(A))

    # For Numarray
    mina = A.min()
    maxa = A.max()

    n,m = A.shape
    if n > width or m > height:
        raise "Rectangle too big %d %d %d %d" % (n,m,width,height)
    for i in range(n):
        xmin = width*i/float(n)
        xmax = width*(i+1)/float(n)
        for j in range(m):
            ymin = height*j/float(m)
            ymax = height*(j+1)/float(m)
            # JBC added a dictionary to cache colors to reduce the number of calls
            # to rmuller_get_color().  This may lead to a dramatic improvement in the
            # performance of rmuller_pcolor_matrix_pil(), which currently makes a call
            # to rmuller_get_color() for each of the n**2 elements of A.  The cache will
            # reduce that to the number of unique values in A, which should ne much
            # smaller.
            _cache_key = '%s_%s_%s' % (A[i,j],mina,maxa)
            try:
                color = color_cache[_cache_key]
            except KeyError:
                color = rmuller_get_color(A[i,j],mina,maxa)
                color_cache[_cache_key] = color
            # JBC added this to generate a color key.
            try:
                _v = key_dict[color]
            except KeyError:
                #_key = round( (A[i,j] * 1000), 0 )
                key_dict[A[i,j]] = color
            if do_outline:
                draw.rectangle((xmin,ymin,xmax,ymax),fill=color,outline=(0,0,0))
            else:
                draw.rectangle((xmin,ymin,xmax,ymax),fill=color)

    #print key_dict
    img.save(fname)
    return

##
# rmuller_get_color() Converts a float value to one of a continuous range of colors
# using recipe 9.10 from the Python Cookbook.
# @param a Float value to convert to a color.
# @param cmin Minimum value in array (?).
# @param cmax Maximum value in array (?).
# @return An RGB triplet.
# @defreturn integer
def rmuller_get_color(a,cmin,cmax):
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
    return '#%1x%1x%1x' % (int(15*red),int(15*green),int(15*blue))

##
# draw_pedigree() uses the pydot bindings to the graphviz library -- if they
# are available on your system -- to produce a directed graph of your pedigree
# with paths of inheritance as edges and animals as nodes.  If there is more than
# one generation in the pedigree as determind by the "gen" attributes of the animals
# in the pedigree, draw_pedigree() will use subgraphs to try and group animals in the
# same generation together in the drawing.
# @param pedobj A PyPedal pedigree object.
# @param gfilename The name of the file to which the pedigree should be drawn
# @param gtitle The title of the graph.
# @param gformat The format in which the output file should be written  (JPG|PNG|PS).
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
def draw_pedigree(pedobj, gfilename='pedigree', gtitle='', gformat='jpg', gsize='f', gdot='1', gorient='p', gdirec='', gname=0, gfontsize=10, garrow=1, gtitloc='b', gtitjust='c'):
    from pyp_utils import string_to_table_name
    _gtitle = string_to_table_name(gtitle)
#     if pedobj.kw['messages'] == 'verbose':
#         print 'gtitle: %s' % ( gtitle )
#         print '_gtitle: %s' % ( _gtitle )

    if gtitloc not in ['t','b']:
        gtitloc = 'b'
    if gtitjust not in ['c','l','r']:
        gtitjust = 'c'

    try:
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
        # Set some properties for the graph.  The label attribute is based on the gtitle.
        # In cases where an empty string, e.g. '', is provided as the gtitle dot engine
        # processing breaks.  In such cases, don't add a label.
        if gtitle == '':
            g = pydot.Dot(graph_name=_gtitle, type='graph', strict=False, suppress_disconnected=True, simplify=True)
        else:
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
        #g.write_jpeg(outfile, prog='dot')
        g.write(outfile,prog='dot',format=gformat)
        return 1
    except:
        return 0

##
# founders_by_year() uses matplotlib -- if available on your system -- to produce a
# bar graph of the number (count) of founders in each birthyear.
# @param pedobj A PyPedal pedigree object.
# @param gfilename The name of the file to which the pedigree should be drawn
# @param gtitle The title of the graph.
# @return A 1 for success and a 0 for failure.
# @defreturn integer
def plot_founders_by_year(pedobj,gfilename='founders_by_year',gtitle='Founders by Birthyear'):
    fby = pyp_demog.founders_by_year(pedobj)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import pylab
        pylab.clf()
        pylab.bar(fby.keys(),fby.values())
        pylab.title(gtitle)
        pylab.xlabel('Year')
        pylab.ylabel('Number of founders')
        plotfile = '%s.png' % (gfilename)
        myplotfile = open(plotfile,'w')
        pylab.savefig(myplotfile)
        myplotfile.close()
    except:
        if pedobj.kw['messages'] == 'verbose':
            print 'ERROR: pyp_graphics/plot_founders_by_year() was unable to create the plot \'%s\' (%s.png).' % (gtitle,gfilename)
        logging.error('ERROR: pyp_graphics/plot_founders_by_year() was unable to create the plot \'%s\' (%s.png).' % (gtitle,gfilename))
        return 0

##
# founders_pct_by_year() uses matplotlib -- if available on your system -- to produce a
# line graph of the frequency (percentage) of founders in each birthyear.
# @param pedobj A PyPedal pedigree object.
# @param gfilename The name of the file to which the pedigree should be drawn
# @param gtitle The title of the graph.
# @return A 1 for success and a 0 for failure.
# @defreturn integer
def plot_founders_pct_by_year(pedobj,gfilename='founders_pct_by_year',gtitle='Founders by Birthyear'):
    fby = pyp_demog.founders_by_year(pedobj)
    _freqdict = {}
    for _k in fby.keys():
        _freqdict[_k] = float(fby[_k]) / float(pedobj.metadata.num_unique_founders)
    try:
        import matplotlib
        matplotlib.use('Agg')
        import pylab
        pylab.clf()
        pylab.plot(fby.keys(),_freqdict.values())
        pylab.title(gtitle)
        pylab.xlabel('Year')
        pylab.ylabel('% founders')
        plotfile = '%s.png' % (gfilename)
        myplotfile = open(plotfile,'w')
        pylab.savefig(myplotfile)
        myplotfile.close()
    except:
        if pedobj.kw['messages'] == 'verbose':
            print 'ERROR: pyp_graphics/plot_pct_founders_by_year() was unable to create the plot \'%s\' (%s.png).' % (gtitle,gfilename)
        logging.error('ERROR: pyp_graphics/plot_pct_founders_by_year() was unable to create the plot \'%s\' (%s.png).' % (gtitle,gfilename))
        return 0

##
# pcolor_matrix_pylab() implements a matlab-like 'pcolor' function to
# display the large elements of a matrix in pseudocolor using the Python Imaging
# Library.
# @param A Input Numpy matrix (such as a numerator relationship matrix).
# @param fname Output filename to which to dump the graphics (default 'tmp.png')
# @param do_outline Whether or not to print an outline around the block (default 0)
# @param height The height of the image (default 300)
# @param width The width of the image (default 300)
# @return A list of Animal() objects; a pedigree metadata object.
# @defreturn lists
def pcolor_matrix_pylab(A,fname='pcolor_matrix_matplotlib'):
#     try:
    import numarray
    import matplotlib
    matplotlib.use('Agg')
    import pylab
    pylab.clf()
    x = pylab.arange(A.shape[0])
    X, Y = pylab.meshgrid(x,x)

    xmin = min(pylab.ravel(X))
    xmax = max(pylab.ravel(X))
    pylab.xlim(xmin, xmax)
    ymin = min(pylab.ravel(Y))
    ymax = max(pylab.ravel(Y))
    pylab.ylim(ymin, ymax)
    pylab.axis('off')

    pylab.pcolor(X, Y, pylab.transpose(A))#, shading='flat')
    pylab.clim(0.0, 1.0)
    plotfile = '%s.png' % (fname)
    myplotfile = open(plotfile,'w')
    pylab.savefig(myplotfile)
    myplotfile.close()
#        return 1
#     except:
#         return 0

##
# spy_matrix_pylab() implements a matlab-like 'pcolor' function to
# display the large elements of a matrix in pseudocolor using the Python Imaging
# Library.
# @param A Input Numpy matrix (such as a numerator relationship matrix).
# @param fname Output filename to which to dump the graphics (default 'tmp.png')
# @param do_outline Whether or not to print an outline around the block (default 0)
# @param height The height of the image (default 300)
# @param width The width of the image (default 300)
# @return A list of Animal() objects; a pedigree metadata object.
# @defreturn lists
def spy_matrix_pylab(A,fname='spy_matrix_matplotlib'):
#     try:
    import numarray
    import matplotlib
    matplotlib.use('Agg')
    import pylab
    pylab.clf()
    pylab.spy2(A)
    plotfile = '%s.png' % (fname)
    myplotfile = open(plotfile,'w')
    pylab.savefig(myplotfile)
    myplotfile.close()
#        return 1
#     except:
#         return 0

##
# plot_line_xy() uses matplotlib -- if available on your system -- to produce a
# line graph of the values in a dictionary for each level of key.
# @param dictionary A Python dictionary
# @param gfilename The name of the file to which the figure should be written
# @param gtitle The title of the graph.
# @param gxlabel The label for the x-axis.
# @param gylabel The label for the y-axis.
# @return A 1 for success and a 0 for failure.
# @defreturn integer
def plot_line_xy(xydict, gfilename='plot_line_xy', gtitle='Value by key', gxlabel='X', gylabel='Y', gformat='png'):
    if gformat not in ['png']:
        gformat = 'png'
    try:
        import matplotlib
        matplotlib.use('Agg')
        import pylab
        pylab.clf()
        pylab.plot(xydict.keys(),xydict.values())
        pylab.title(gtitle)
        pylab.xlabel(gxlabel)
        pylab.ylabel(gylabel)
        plotfile = '%s.%s' % (gfilename, gformat)
        myplotfile = open(plotfile,'w')
        pylab.savefig(myplotfile)
        myplotfile.close()
        _status = 1
    except:
        if pedobj.kw['messages'] == 'verbose':
            print 'ERROR: pyp_graphics/plot_line_xy() was unable to create the plot \'%s\' (%s.%s).' % (gtitle,gfilename,gformat)
        logging.error('pyp_graphics/plot_line_xy() was unable to create the plot \'%s\' (%s.%s).' % (gtitle,gfilename,gformat))
        _status = 0
    return _status
