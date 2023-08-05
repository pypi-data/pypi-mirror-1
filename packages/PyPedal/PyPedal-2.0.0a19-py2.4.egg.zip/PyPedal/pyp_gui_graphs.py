#!/usr/bin/python

###############################################################################
# NAME: pyp_gui_graphs.py
# VERSION: 2.0.0a19 (20SEPT2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# PyPedalGraphDialogInbreeding()
###############################################################################

##
# I am not smart enough to properly subclass Wax's DIalog class in the manner that
# I would like.  As a result, pyp_gui_graphs contains a subclass of Dialog for each
# type of graph that pyp_gui can draw.
##

import wx
import pyp_gui, pyp_gui_metrics, pyp_gui_utils
import pyp_demog, pyp_graphics, pyp_io, pyp_newclasses, pyp_nrm, pyp_metrics, pyp_utils
import pyp_db, pyp_reports

##
# The PyPedalGraphDialogInbreeding() class provides the dialogue box used
# to display the "inbreeding by birthyear" graph.
class PyPedalGraphDialogInbreeding(wx.Dialog):
    def Body(self):
        wx.InitAllImageHandlers()
        _i = wx.Image('_coi_by_year.png', wx.BITMAP_TYPE_PNG)
        _b = wx.BitmapFromImage(_i)
        _sb = wx.StaticBitmap(self, -1, _b, (10, 10), (_b.GetWidth(), _b.GetHeight()))
        #wx.StaticBitmap(panel, -1, bmp, (10, pos), (bmp.GetWidth(), bmp.GetHeight()))
        #self.AddComponent(_sb)
        #self.Pack()