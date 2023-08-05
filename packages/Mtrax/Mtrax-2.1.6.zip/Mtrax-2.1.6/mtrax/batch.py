# mtrax_batch.py
# JAB 3/30/07

import os
import wx
from wx import xrc

import pkg_resources # part of setuptools
RSRC_FILE = pkg_resources.resource_filename( __name__, "batch.xrc" )

class BatchWindow:
    def __init__( self, parent, directory, file_list=None ):
        self.file_list = []
        if file_list is not None: self.file_list.append( file_list )
        self.dir = directory
        self.ShowWindow( parent )

    def ShowWindow( self, parent ):
        rsrc = xrc.XmlResource( RSRC_FILE )
        self.frame = rsrc.LoadFrame( parent, "frame_mtrax_batch" )

        # event bindings
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonAdd, id=xrc.XRCID("button_add") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonRemove, id=xrc.XRCID("button_remove") )
        self.frame.Bind( wx.EVT_BUTTON, self.OnButtonClose, id=xrc.XRCID("button_close") )
        self.frame.Bind( wx.EVT_CLOSE, self.OnButtonClose )

        # button handles
        self.add_button = xrc.XRCCTRL( self.frame, "button_add" )
        self.remove_button = xrc.XRCCTRL( self.frame, "button_remove" )
        self.execute_button = xrc.XRCCTRL( self.frame, "button_execute" )
        
        # textbox handle
        self.list_box = xrc.XRCCTRL( self.frame, "text_list" )
        self.list_box.Set( self.file_list )

        self.frame.Show()
        self.is_showing = True
        self.executing = False
 
    def OnButtonAdd( self, evt ):
        dlg = wx.FileDialog( self.frame, "Select movie", self.dir, "", "*.fmf", wx.OPEN ) # Linux only
        
        if dlg.ShowModal() == wx.ID_OK:
            self.dir = dlg.GetDirectory()
            newfile = os.path.join( self.dir, dlg.GetFilename() )

            # check for duplicates
            add_flag = True
            for filename in self.file_list:
                if filename == newfile:
                    wx.MessageBox( "File has already been added,\nnot duplicating", "Duplicate", wx.ICON_WARNING )
                    add_flag = False
                    break
                
            if add_flag:
                self.file_list.append( newfile )
                self.list_box.Set( self.file_list )

        dlg.Destroy()

    def OnButtonRemove( self, evt ):
        for ii in reversed( range( len(self.file_list) ) ):
            if self.list_box.IsSelected( ii ):
                # don't remove currently executing job
                if not self.executing or ii != 0:
                    self.file_list.pop( ii )
        self.list_box.Set( self.file_list )

    def OnButtonClose( self, evt ):
        self.frame.Destroy()
        self.is_showing = False
