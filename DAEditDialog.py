# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import xml.dom.minidom
import xml.parsers.expat
import os, wx, re, glob, wx.lib.layoutf
import wx.lib.dialogs, wx.lib.layoutf, wx.lib.scrolledpanel

from dialogs import *
from editor_model import *
from SingleDAEditDialog import *

class DAListBox(wx.HtmlListBox):
    # mám dialog ve kterém to je jako "parent" dialog - self.parent
    def OnGetItem(self, n):
        return self.parent.OnGetItem(n)     

class DAEditDialog(wx.Dialog):
    def __init__(
        self, parent, ID, title, 
        dialog_acts, utterance_text, datovy_model,
        size=wx.DefaultSize, pos=wx.DefaultPosition, 
        style=wx.DEFAULT_FRAME_STYLE
        ):
    
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)
        sizer = wx.BoxSizer(wx.VERTICAL)
    
        label = wx.StaticText(self, -1, "Choose dialog act")
        sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
    
        buttons = wx.BoxSizer(wx.HORIZONTAL)

        self.lbDA = DAListBox(self, -1, size=(700,400), style=wx.BORDER_SUNKEN)      
        self.lbDA.parent = self
        self.lbDA.Bind(wx.EVT_LISTBOX_DCLICK, self.OnEdit)
        self.lbDA.Bind(wx.EVT_KEY_DOWN, self.OnKey)             
        buttons.Add(self.lbDA, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        sizer.Add(buttons, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5)
    
        # buttons
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_OK, " &OK ")
        btn.SetDefault()        
        buttons.Add(btn, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        
        btn = wx.Button(self, -1, " &Segmentation ")
        btn.Bind(wx.EVT_BUTTON, self.OnSegmentation)
        buttons.Add(btn, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        
        btn = wx.Button(self, -1, " &Edit ")
        btn.Bind(wx.EVT_BUTTON, self.OnEdit)
        buttons.Add(btn, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        
        btn = wx.Button(self, -1, " &Reset all ")
        btn.Bind(wx.EVT_BUTTON, self.OnReset)
        buttons.Add(btn, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
    
        btn = wx.Button(self, wx.ID_CANCEL)
        buttons.Add(btn, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(buttons, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5)
    
        # inicializace dat
        self.dm = datovy_model
        self.dialog_acts = dialog_acts      
        self.utterance_text = utterance_text    
        
        self.Refresh()
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)
        self.Centre()
        
    def OnKey(self, e):
        if e.GetKeyCode() == 32:
            self.OnEdit(None)
        elif e.GetKeyCode() == 13:
             self.EndModal(wx.ID_OK)
        else:
            e.Skip()
            
    def OnReset(self, event):
        dlg = wx.MessageDialog(self, "Do you really want to erase all dialogue acts and create the first one with whole utterance as content?", "Warning", wx.YES_NO)
        if (dlg.ShowModal() == wx.ID_YES):
            self.dialog_acts = list()
            self.Refresh()
        
    def OnEdit(self, event):
        i = self.lbDA.GetSelection()
        dlg = SingleDAEditDialog(self, -1, "Dialog act editor",
            self.dialog_acts[i], self.dm.domainTags, self.dm.speechActTags, self.dm.conceptTags)

        if dlg.ShowModal() == wx.ID_OK:
            tuple = dlg.GetDA()
            try:
                self.dialog_acts[i].domain = tuple[0]
                self.dialog_acts[i].speechAct = tuple[1]
                self.dialog_acts[i].semantics = tuple[2]
            except AttributeError:
                pass
            
        self.Refresh()

    def SplitUtterance2DA(self, par_dialog_acts):
        text = ""
        acts = par_dialog_acts
        for da in acts:
            text += da.text+"\n"
        dlg = SplitUtterance2DADialog(self,-1,"Dialogue act segmenting", text)
        dlg.ShowModal()
        lines = dlg.GetText().split("\n")
        i = 0
        for line in lines:
            while len(acts) <= i:
                # máme jich málo
                acts.append(DialogueAct())
            da = acts[i]
            da.text = line          
            i += 1
        del acts[i:len(acts)]
        return acts
    
    def Refresh(self):
        if len(self.dialog_acts)==0:
            self.dialog_acts.append(DialogueAct()) 
            self.dialog_acts[0].text = self.utterance_text
        self.lbDA.SetItemCount(len(self.dialog_acts))
        self.lbDA.RefreshAll()
        
    def OnSegmentation(self,event):
        self.dialog_acts = self.SplitUtterance2DA(self.dialog_acts)
        self.Refresh()
        
    def GetDialogActs(self):
        return self.dialog_acts
        
    def OnGetItem(self, n):
        ## o = self.dialog_acts[n].get_html()
        
        (a1, a2, a3) =(self.dialog_acts[n].domain,
            self.dialog_acts[n].speechAct,
            self.dialog_acts[n].semantics)

        if len(a1) == 0:
            a1 = "---"
        if len(a2) == 0:
            a2 = "---"
        if len(a3) == 0:
            a3 = "---"

        s = "<b>%s</b>" % self.dialog_acts[n].text
        a = "<br><font color=#900090><code>%-17s %-24s " % (a1, a2)
            
        # &nbsp; is not posible break
        a = a.replace(' ','&nbsp;')
        a = a.replace('t&nbsp;c', 't c')

        s += a + a3 + "</code></font></br><br></br>"
        
        return s
        
        
