# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import os, os.path
import wx

from dialogs import *
from PromtingChoice import *
from editor_model import *
from semantics import *

class ConfigDialog(wx.Dialog):
    def __init__(self, parent, ID, title, dm,
        size=wx.DefaultSize, 
        pos=wx.DefaultPosition, 
        style=wx.DEFAULT_FRAME_STYLE):
        
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)
        
        # 2 polozky annotator, datadir
        
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        self.dm = dm
        self.textAnn = wx.TextCtrl(self, -1, "", size=(400,-1))
        self.textDir = wx.TextCtrl(self, -1, "", size=(400,-1))
        
        try:
            self.textAnn.SetValue(self.dm.anotatorid)
            self.textDir.SetValue(self.dm.datadir)
        except AttributeError:
            pass
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1,"Annotator name"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        sizer.Add(self.textAnn, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,5)                
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5) 
        sizer.Add(wx.StaticText(self, -1,"Data directory (root: %s)" % os.getcwd()),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)    

        # the select button
        select = wx.Button(self, -1, "&Select the directory")
        select.Bind(wx.EVT_BUTTON, self.OnSelectDir)

        sizerSelectDir = wx.BoxSizer(wx.HORIZONTAL)
        sizerSelectDir.Add(self.textDir, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND)
        sizerSelectDir.Add(select, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND)

        sizer.Add(sizerSelectDir, 1, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)

        # buttons
        
        ok = wx.Button(self, wx.ID_OK)
        ok.SetDefault()
        ok.Bind(wx.EVT_BUTTON, self.OnOK)
        cancel  = wx.Button(self, wx.ID_CANCEL)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(ok, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        buttons.Add(cancel, 1 , wx.ALIGN_CENTER|wx.ALL, 5)
        
        sizer.Add(buttons, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.Bind(wx.EVT_CHAR, self.OnKey)
        
        self.Refresh()
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)
  
    def OnOK(self, event):
        self.dm.anotatorid = self.textAnn.GetValue().strip()
        self.dm.datadir = self.textDir.GetValue().strip()
        self.EndModal(wx.ID_OK)
        event.Skip()

    def OnSelectDir(self, event):
        dir = os.path.abspath(self.textDir.GetValue().strip())
        
        dlg = wx.DirDialog(self, "Select a directory with XMLs", dir, size = (400, 600))
        if dlg.ShowModal() == wx.ID_OK:
            dir = dlg.GetPath()
            dir = dir.replace(os.getcwd(), ".")
            self.textDir.SetValue(dir)
        dlg.Destroy()
        
    def OnKey(self, event):
        if event.GetKeyCode() == 27:
            # escape
            self.Close()
        else:
            event.Skip();

    def getDescription(self):
        return self.descriptionTextCtrl.GetValue()
        
    def getProcessingState(self):
        return self.processingStateChoice.GetStringSelection()
        

#############################################################################
## test of dialogue
#############################################################################
if __name__ == "__main__":
    app = wx.PySimpleApp()
    
    dlg = ConfigDialog(None, -1, "Configuration", None)
    dlg.ShowModal()
    
    app.MainLoop()
    
    
   
