# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import os
import wx

from dialogs import *
from PromtingChoice import *
from editor_model import *
from semantics import *

class DescribeDialog(wx.Dialog):
    def __init__(self, parent, ID, title, 
        description,
        processingState,
        processingStateTags,
        size=wx.DefaultSize, 
        pos=wx.DefaultPosition, 
        style=wx.DEFAULT_FRAME_STYLE):
        
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)
        
        self.processingStateChoice = PromptingChoice(self, -1, size=(600,-1), choices=processingStateTags)
        self.processingStateChoice.SetStringSelection(processingState)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        self.descriptionTextCtrl = wx.TextCtrl(self, -1, "", size=(600,200), style=wx.TE_MULTILINE)
        self.descriptionTextCtrl.SetValue(description)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1,"Processing state"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        sizer.Add(self.processingStateChoice, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,5)               
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)     
        sizer.Add(self.descriptionTextCtrl, 1, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        
        # buttons
        ok = wx.Button(self, wx.ID_OK)
        ok.SetDefault()
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
    
    description = "2"
    processingState = "unannotated"
    processingStateTags = ["a", "b", "c", "v"]
    
    dlg = DescribeDialog(None, -1, "Description", description, processingState, processingStateTags)
    dlg.ShowModal()
    
    app.MainLoop()
    
    
   
