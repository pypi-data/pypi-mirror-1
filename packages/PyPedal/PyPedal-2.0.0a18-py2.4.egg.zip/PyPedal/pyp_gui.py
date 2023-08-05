#!/usr/bin/python

###############################################################################
# NAME: pyp_gui.py
# VERSION: 2.0.0a7 (11JUNE2004)
# AUTHOR: John B. Cole, PhD (jcole@aipl.arsusda.gov)
# LICENSE: LGPL
###############################################################################

import os
import PIL.Image
from pyp_classes import *
from pyp_io import *
from pyp_metrics import *
from pyp_nrm import *
from pyp_utils import *
from wxPython.wx import *

if __name__ == '__main__':
    # File menu items
    ID_OPEN=101
    ID_SAVE=102
    ID_SAVEAS=103
    ID_CLOSE=104
    ID_EXIT=110
    # Pedigree menu items
    ID_PED_META = 201
    ID_PED_LIST = 202
    ID_PED_VIEW = 203
    # Help menu items
    ID_HELP=501
    ID_ABOUT=502
    # Text box items
    ID_MAIN_TB=601
    # Window sizes
    size_x = 640
    size_y = 480
    class MainWindow(wxFrame):
        def __init__(self,parent,id,title):
            wxFrame.__init__(self,parent,wxID_ANY, title,
                size = ( size_x, size_y ),
                style = wxDEFAULT_FRAME_STYLE | wxNO_FULL_REPAINT_ON_RESIZE)
            self.control = wxTextCtrl(self, 1, style=wxTE_MULTILINE)
            self.CreateStatusBar()  # A Statusbar in the bottom of the window
            # Setting up the menu.
            # This is the "File" menu
            filemenu= wxMenu()
            filemenu.Append(ID_OPEN, "&Open", " Open a pedigree file")
            filemenu.Append(ID_SAVE, "&Save", " Save a pedigree file")
            filemenu.Append(ID_SAVEAS, "Save &As", " Save a pedigree file as...")
            filemenu.Append(ID_CLOSE, "&Close", " Close a pedigree file")
            filemenu.AppendSeparator()
            filemenu.Append(ID_EXIT,"E&xit", " Exit PyPedal")
            # This is the "Pedigree" menu
            pedmenu= wxMenu()
            pedmenu.Append(ID_PED_META, "&Metadata", " View pedigree metadata")
            pedmenu.Append(ID_PED_LIST, "&List Animals", " View a list of animal records")
            pedmenu.Append(ID_PED_VIEW, "&View", " View a diagram of the pedigree")
            # This is the "Help" menu
            helpmenu= wxMenu()
            helpmenu.Append(ID_HELP, "&Help", " Help with PyPedal")
            helpmenu.AppendSeparator()
            helpmenu.Append(ID_ABOUT,"&About", " About PyPedal")
            ###
            ### Application constants -- will change later to store in a configuration file
            ###
            self.pedigreedirty = false
            self.filetag='_test_gui_'
            self.sepchar=' '
            self.debug=0
            self.io='no'
            self.renum=1
            self.outformat='0'
            self.name='GUI Test Pedigree'
            self.alleles=0
            
            # Creating the menubar.
            menuBar = wxMenuBar()
            menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
            menuBar.Append(pedmenu,"&Pedigree") # Adding the "pedmenu" to the MenuBar
            menuBar.Append(helpmenu,"&Help") # Adding the "helpmenu" to the MenuBar
            self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
            # Attach handlers to events
            ## "File" menu events
            EVT_MENU(self, ID_OPEN, self.OnOpen)
            EVT_MENU(self, ID_SAVE, self.ToDo)
            EVT_MENU(self, ID_SAVEAS, self.ToDo)
            EVT_MENU(self, ID_CLOSE, self.ToDo)
            EVT_MENU(self, ID_EXIT, self.OnExit)    # attach the menu-event ID_EXIT to the method self.OnExit
            ## "Pedigree" menu events
            EVT_MENU(self, ID_PED_META, self.OnPedMeta)
            EVT_MENU(self, ID_PED_LIST, self.OnPedList)
            EVT_MENU(self, ID_PED_VIEW, self.OnPedView)
            ## "Help" menu events
            EVT_MENU(self, ID_HELP, self.ToDo)
            EVT_MENU(self, ID_ABOUT, self.OnAbout)
            # Show the window
            self.Show(true)
        ##
        ## event handlers
        ##
        def pedigree_open(self, pedigree_file):
            try:
                self.pedigree, self.pedmeta = load_pedigree(pedigree_file,filetag='_load_pedigree_',sepchar=' ',debug=0,io='no',renum=1,outformat='0',name='Pedigree Metadata',alleles=0)
                self.pedigreedirty = false
            except IOError:
                d_m = wxMessageDialog (self, 'There was an error loadinging the pedigree %s.'%(self.pedigree_file),
                    'Error!', wxOK)
                d_m.ShowModal()
                d_m.Destroy()
        def pedigree_save(self):
            #try:
            #    load_pedigree(self.pedigree_file,filetag='_load_pedigree_',sepchar=',',debug=0,io='no',renum=1,outformat='0',name='Pedigree Metadata',alleles=0)
            #    self.pedigreedirty = false
            #except:
            #    d_m = wxMessageDialog (self, 'There was an error saving the pedigree.',
            #        'Error!', wxOK)
            #    d_m.ShowModal()
            #    d_m.Destroy()
            pass
        ##
        ## menu-event handlers
        ##
        ####
        #### File menu handlers
        ####
        def OnOpen(self,e):
            open_it = true
            if self.pedigreedirty:
                d=wxMessageDialog(self, 'The pedigree has been changed.  Save?',
                    'PyPedal',
                    wxYES_NO | wxCANCEL)
                result = d.ShowModal()
                if result == wxID_YES:
                    self.pedigree_save()
                if result == wxID_CANCEL:
                    open_it = false
                d.Destroy()
            if open_it:
                d = wxFileDialog(self, "Choose a pedigree to open", ".", "", "*.ped", wxOPEN)
                if d.ShowModal() == wxID_OK:
                    self.pedigree_open(d.GetPath())
                d.Destroy()
        ####
        #### Pedigree menu handlers
        ####
        def OnPedMeta(self,e):
            try:
                self.rtb = wxTextCtrl(self, ID_MAIN_TB, size=wxSize(size_x, size_y-40),
                    style = wxTE_MULTILINE | wxTE_READONLY )
                self.sizer = wxBoxSizer(wxVERTICAL)
                self.sizer.Add(self.rtb, 1, wxEXPAND)
                self.SetSizer(self.sizer)
                self.SetAutoLayout(True)
                self.sizer.SetSizeHints(self)
                self.rtb.SetValue(self.pedmeta.stringme())
            finally:
                pass
        def OnPedList(self,e):
            try:
                self.rtb = wxTextCtrl(self, ID_MAIN_TB, size=wxSize(size_x, size_y-40),
                    style = wxTE_MULTILINE | wxTE_READONLY )
                self.sizer = wxBoxSizer(wxVERTICAL)
                self.sizer.Add(self.rtb, 1, wxEXPAND)
                self.SetSizer(self.sizer)
                self.SetAutoLayout(True)
                self.sizer.SetSizeHints(self)
                _me = ''
                _p_counter = 0
                for p in self.pedigree:
                    _me = '%s%s' % (_me, p.stringme())
                    _me = '%s%s\n' % (_me,'-'*size_x)
                    _p_counter = _p_counter + 1
                _me = '%s\n\n%s' % ('There are %s animals in the pedigree:'%(_p_counter), _me)
                self.rtb.SetValue(_me)
            finally:
                pass
        def OnPedView(self,e):
            _drawn = draw_pedigree(self.pedigree,gfilename='pedigree',gtitle='My_Pedigree',gformat='jpg')
            if _drawn:
                try:
                    infile = 'pedigree.jpg'
		    #### This is a bad hack to deal with some unresolved segfaults caused by calls
		    #### to wxImage.ConvertToBitmap().
		    im = PIL.Image.open(infile)
		    im.save("pedigree.bmp", "BMP")
		    #### End of bad hack.
		    wxInitAllImageHandlers()
                    _me = wxImage('pedigree.bmp')
		    _me = _me.ConvertToBitmap()
		    _width = _me.GetWidth()
	            _height = _me.GetHeight()
		    wxStaticBitmap(self, -1, _me, wxPoint(0,0),wxSize(_me.GetWidth(),_me.GetHeight()))
                finally:
                    pass
            else:
                d = wxMessageDialog( self, " Unable to draw the pedigree!",
                    "PyPedal - Cannot draw pedigree",
                    wxOK | wxICON_INFORMATION)
                d.ShowModal()
                d.Destroy()
        ####
        #### Help menu handlers
        ####
        def OnAbout(self,e):
            d = wxMessageDialog( self, " PyPedal 2.0.0a8\n"
                " A software package for pedigree analysis.\n"
                " (c) 2002-2004 John B. Cole\n"
                " http://pypedal.sourceforge.net/\n"
                " jcole@aipl.arsusda.gov",
                "About PyPedal",
                wxOK | wxICON_INFORMATION)
            # Create a message dialog box
            d.ShowModal() # Shows it
            d.Destroy() # finally destroy it when finished.
        def OnExit(self,e):
            d = wxMessageDialog(self, 'Are you sure you want to exit PyPedal?',
                'PyPedal - Exit',
                wxYES_NO | wxICON_QUESTION) 
            if d.ShowModal() == wxID_YES:
                d.Destroy()
                self.Close(true)
            else: 
                d.Destroy() 
        def ToDo(self,e):
            d = wxMessageDialog( self, " This feature has not yet been implemented!",
                "PyPedal - Unknown Feature",
                wxOK | wxICON_INFORMATION)
            d.ShowModal()
            d.Destroy()

    class MyApp(wxApp):
        def OnInit(self):
            frame = MainWindow(None, -1, "PyPedal")
            frame.Show(true)
            self.SetTopWindow(frame)
            return true

if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
