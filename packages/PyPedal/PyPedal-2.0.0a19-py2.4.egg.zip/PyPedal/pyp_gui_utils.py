#!/usr/bin/python

###############################################################################
# NAME: pyp_gui_utils.py
# VERSION: 2.0.0a19 (21SEPT2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# PyPedalShowErrorDialog()
# PyPedalOptionsDialog() (I know, dialogue is spelled incorrectly.)
# UtilsViewLog()
###############################################################################

##
# pyp_gui_utils various bits and pieces for the PyPedal GUI, such as the class
# definition for the options dialogue.
##

import PIL.Image
import os, string
import wx
import pyp_gui, pyp_gui_graphs, pyp_gui_metrics, pyp_gui_utils
import pyp_demog, pyp_graphics, pyp_io, pyp_newclasses, pyp_nrm, pyp_metrics, pyp_utils
import pyp_db, pyp_reports

##
# The PyPedalOptionsDialog() class provides the dialogue box used for viewing and
# setting options.
class PyPedalOptionsDialog(wx.Dialog):
    def Body(self):
        self.AddComponent(wx.Bitmap(self,_b))
        self.Pack()

##
# PyPedalShowErrorDialog()
# @param sedTitle String used to construct the title of the dialogue box.
# @param sedMessage Message to be displayed in the dialogue box.
# @return None
# @defreturn None
def PyPedalShowErrorDialog(self,sedTitle="PyPedal - Unknown error", sedMessage="An unknown error occurred!"):
    sedTitle = 'PyPedal - %s' % (sedTitle)
    dlg = wx.MessageDialog(self,
        sedMessage,
        sedTitle,
        wx.OK |
        wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()

##
# UtilsViewLog() produces the file dialog used to select a log file to be
# opened.
# @param None
# @return None
# @defreturn None
def UtilsViewLog(self):
    if hasattr(self,'_pedigree'):
        self.SetFilename(self._pedigree.kw['logfile'])
        f = open(self._pedigree.kw['logfile'], 'r')
        data = f.read()
        f.close()
        shortfilename = string.split(self._pedigree.kw['logfile'],'/')[-1]
        _header = 'Viewing logfile %s\n' % (shortfilename)
        self.textbox.Clear()
        self.textbox.AppendText(_header)
        self.textbox.AppendText(pyp_io.LINE1)
        self.textbox.AppendText('\n')
        self.textbox.AppendText(data)
    else:
        pyp_gui_utils.PyPedalShowErrorDialog(self,sedTitle='View log', sedMessage='You cannot view a log file until you load a pedigree!')