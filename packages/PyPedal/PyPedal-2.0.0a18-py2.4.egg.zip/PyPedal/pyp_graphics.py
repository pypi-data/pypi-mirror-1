#!/usr/bin/python

###############################################################################
# NAME: pyp_graphics.py
# VERSION: 2.0.0a17 (19MAY2005)
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
# pyp_graphics contains for working with graphics in PyPedal, such as creating
# directed graphs from pedigrees using PyDot and visualizing relationship matrices
# using Rick Muller's spy and pcolor routines
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
            color = rmuller_get_color(A[i,j],mina,maxa)
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
# one generation in the pedigree as determind by the "gen" attributes of the anumals
# in the pedigree, draw_pedigree() will use subgraphs to try and group animals in the
# same generation together in the drawing.
# @param pedobj A PyPedal pedigree object.
# @param gfilename The name of the file to which the pedigree should be drawn
# @param gtitle The title of the graph.
# @param gsize The size of the graph: 'f': full-size, 'l': letter-sized page.
# @param gdot Whether or not to write the dot code for the pedigree graph to a file (can produce large files).
# @return A 1 for success and a 0 for failure.
# @defreturn integer
def draw_pedigree(pedobj,gfilename='pedigree',gtitle='My_Pedigree',gformat='jpg',gsize='f',gdot='1'):
    # Spaces in the graph name will break things, so convert them to underscores.
    if ' ' in gtitle:
        gname = string.replace(gtitle,' ','_')
    else:
        gname = gtitle
    
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
        # Set some properties for the graph.
        g = pydot.Dot(label=gtitle, graph_name=gname, type='graph', strict=False, suppress_disconnected=True, simplify=True)
        if gsize == 'l':
            g.set_page("8.5,11")
            g.set_size("7.5,10")
            g.set_orientation("landscape")
        else:
            g.set_page("8.5,11")
            g.set_size("7.5,10")
            g.set_orientation("landscape")
            g.set_ratio("auto")
        #g.set_rankdir('LR')
        g.set_center('true')
        g.set_concentrate('true')
        g.set_ordering('out')
        if gformat not in g.formats:
            gformat = 'jpg'
        # If we do not have any generations, we have to draw a less-nice graph.
        if len(gens) <= 1:
            for _m in pedobj.pedigree:
                # Add a node for the current animal and set some properties.
    #                 if int(_m.originalID) == -999:
    #                     _m.printme()
    #                 if int(pedobj.pedigree[int(_m.sireID)-1].originalID) == -999:
    #                     _m.printme()
    #                 if int(pedobj.pedigree[int(_m.damID)-1].originalID) == -999:
    #                     _m.printme()
                _node_name = _m.animalID
                _an_node = pydot.Node(_node_name)
                _an_node.set_fontname('Helvetica')
                _an_node.set_fontsize('10')
                _an_node.set_height('0.35')
                g.add_node(_an_node)
                # Add the edges to the parent nodes, if any.
                if int(_m.sireID) != 0:
                    g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].originalID,_m.originalID))
                if int(_m.damID) != 0:
                    g.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].originalID,_m.originalID))
        # Otherwise we can draw a nice graph.
        else:
            for _g in gens:
                _sg_anims = []
                _sg_name = 'sg%s' % (_g)
                sg = pydot.Subgraph(graph_name=_sg_name, suppress_disconnected=True, simplify=True)
                sg.set_simplify(True)
                for _m in pedobj.pedigree:
    #                     if int(_m.originalID) == -999:
    #                         _m.printme()
    #                     if int(pedobj.pedigree[int(_m.sireID)-1].originalID) == -999:
    #                         _m.printme()
    #                     if int(pedobj.pedigree[int(_m.damID)-1].originalID) == -999:
    #                         _m.printme()
                    if int(_m.gen) == int(_g):
                        _sg_anims.append(_m.animalID)
                    # Add a node for the current animal and set some properties.
                    _node_name = _m.animalID
    #                     if _node_name == '-999' or _node_name == -999:
    #                         _m.printme()
                    _an_node = pydot.Node(_node_name)
                    _an_node.set_fontname('Helvetica')
                    _an_node.set_fontsize('10')
                    _an_node.set_height('0.35')
                    sg.add_node(_an_node)
                    # Add the edges to the parent nodes, if any.
                    if int(_m.sireID) != 0:
                        sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.sireID)-1].originalID,_m.originalID))
                    if int(_m.damID) != 0:
                        sg.add_edge(pydot.Edge(pedobj.pedigree[int(_m.damID)-1].originalID,_m.originalID))
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