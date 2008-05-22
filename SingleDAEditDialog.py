# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import os, wx
import wx.lib.dialogs

from dialogs import *
from PromtingChoice import *
from SmntcTextCtrl import *
from editor_model import *

class SingleDAEditDialog(wx.Dialog):
    def __init__(self, parent, ID, title, 
        dialogAct,
        domainData,
        speechActData,
        concepts,
        size=wx.DefaultSize, 
        pos=wx.DefaultPosition, 
        style=wx.CAPTION or wx.CLOSE_BOX or wx.SYSTEM_MENU or wx.WANTS_CHARS):
        
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style = style)
        
        self.domainData = domainData
        self.domainData.sort()
        self.speechActData = speechActData
        self.speechActData.sort()

        self.domainChoice = PromptingChoice(self, -1, size=(600,-1), choices=self.domainData)
        self.speechActChoice = PromptingChoice(self, -1, size=(600,-1), choices=self.speechActData)
        self.smntcTextCtrl = SmntcTextCtrl(self, -1, concepts)
        self.SetDA(dialogAct)
        label = wx.TextCtrl(self, -1, "", size=(600,100), style=wx.TE_MULTILINE)
        label.SetValue(dialogAct.text)
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 1, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)     
        sizer.Add(wx.StaticText(self, -1,"Domain"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        sizer.Add(self.domainChoice, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,5)                
        sizer.Add(wx.StaticText(self, -1,"Speech act"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        sizer.Add(self.speechActChoice, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)       
        sizer.Add(wx.StaticText(self, -1,"Semantics"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        sizer.Add(self.smntcTextCtrl, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
    
        # buttons
        ok = wx.Button(self, wx.ID_OK)
        ok.SetDefault()
        ok.Bind(wx.EVT_BUTTON, self.OnOK)   
        cancel  = wx.Button(self, wx.ID_CANCEL)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(ok, 1, wx.ALIGN_CENTER|wx.ALL, 5)
        buttons.Add(cancel, 1 , wx.ALIGN_CENTER|wx.ALL, 5)
        
        sizer.Add(buttons, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        
        self.Refresh()
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)
        self.Centre();
  
    def OnChar(self, event):
        print "SingleDAEditDialog: OnChar(event) %d" % event.GetKeyCode()
        event.Skip();

    def OnKey(self, event):
        print "SingleDAEditDialog: OnKey(event) %d" % event.GetKeyCode()
        if event.GetKeyCode() == 27:
            # escape
            self.Close()
            
        event.Skip();

    def OnOK(self, event):
        if not self.smntcTextCtrl.Validate():
            return False
        
        self.smntcTextCtrl.ResetValidation()

        # save results, triple
        self.vysledek = [self.domainChoice.GetStringSelection(), 
            self.speechActChoice.GetStringSelection(), 
            self.smntcTextCtrl.GetValue()]

        self.EndModal(wx.ID_OK)
        
        # event.Skip()
        return True

    def SetDA(self,da):
        self.vysledek = [da.domain, 
            da.speechAct, 
            da.semantics]

        if len(self.vysledek[0]) == 0:
            self.vysledek[0]="task"
        if len(self.vysledek[1]) == 0:
            self.vysledek[1] = "request_info"

        self.domainChoice.Select(self.domainChoice.FindString(unicode(self.vysledek[0])))
        self.speechActChoice.Select(self.speechActChoice.FindString(unicode(self.vysledek[1])))
        self.smntcTextCtrl.SetValue(da.semantics)

    def GetDA(self):        
        return self.vysledek

#############################################################################
## test of dialogue
#############################################################################
if __name__ == "__main__":
    concepts = [
        "ACCEPT",
        "ARRIVAL",
        "ARRIVAL_CONF",
        "ARRIVAL_TIME",
        "BACK",
        "DEPARTURE",
        "FROM",
        "GREETING",
        "MAYBE",
        "PERSON",
        "PREVIOUS",
        "REJECT",
        "STATION",
        "TIME",
        "TO",
        "TRAIN_TYPE",
        "VERIFY"
        ]

    app = wx.PySimpleApp()
    dialog_act = DialogueAct()
    
    dialog_act.domain = "2"
    dialog_act.speechAct = "3"
    dialog_act.semantics = "TXT"
    dialog_act.text = "qwer qwert zxcv zxcv"


    
    dlg = SingleDAEditDialog(None, -1, "Dialog act editor",
        dialog_act, ["1", "2", "3"], ["1", "2", "3"], concepts)
    dlg.Center()
    dlg.ShowModal()
    
    app.MainLoop()
    
    
   
