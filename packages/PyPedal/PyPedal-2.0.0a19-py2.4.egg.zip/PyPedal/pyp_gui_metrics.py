#!/usr/bin/python

###############################################################################
# NAME: pyp_gui_metrics.py
# VERSION: 2.0.0a19 (21SEPT2005)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################
# MetricsInbreeding()
# MetricsEffectiveFounders()
###############################################################################

##
# pyp_gui_metrics contains convenience functions for entries in the Metrics
# menu to reduce repetitive code in pyp_gui.
##

import PIL.Image
import os
import wx
import pyp_demog, pyp_graphics, pyp_io, pyp_newclasses, pyp_nrm, pyp_metrics, pyp_utils
import pyp_db, pyp_reports
import pyp_gui, pyp_gui_graphs, pyp_gui_utils

def MetricsInbreeding(self):
    if hasattr(self,'_pedigree'):
        self._inbreeding = pyp_nrm.inbreeding(self._pedigree)
        self.textbox.Clear()
        #print pyp_io.summary_inbreeding(self._inbreeding['metadata'])
        self.textbox.AppendText(pyp_io.summary_inbreeding(self._inbreeding['metadata']))
    else:
        pyp_gui_graphs.PyPedalShowErrorDialog(self,sedTitle='Calculate inbreeding', sedMessage='This calculation cannot be displayed because you have not yet loaded a pedigree!')

def MetricsEffectiveFounders(self):
    if hasattr(self,'_pedigree'):
        self._inbreeding = pyp_nrm.inbreeding(self._pedigree)
        self.textbox.Clear()
        print pyp_io.summary_inbreeding(self._inbreeding['metadata'])
        self.textbox.AppendText(pyp_io.summary_inbreeding(self._inbreeding['metadata']))
    else:
        pyp_gui_graphs.PyPedalShowErrorDialog(self,sedTitle='Calculate effective founder', sedMessage='This calculation cannot be displayed because you have not yet loaded a pedigree!')