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
import os, wx, re
import wx.lib.dialogs, wx.lib.layoutf, wx.lib.scrolledpanel

def MyMsgBox(message, param = False):
    return wx.MessageBox(message, "DAE Info", param)    
        
class SplitUtterance2DADialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, text_to_split, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
    
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)
        sizer = wx.BoxSizer(wx.VERTICAL)
    
        label = wx.StaticText(self, -1, "Split utterance to dialogue acts.\nSeparate by newline, one act per line, please.")
        sizer.Add(label, 0, wx.ALIGN_LEFT|wx.ALL, 5)
    
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
    
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.t5 = wx.TextCtrl(self, -1, text_to_split, size=(600, 300),
                style = wx.TE_MULTILINE
                | wx.TE_RICH2
                )                           
        
        self.Bind(wx.EVT_TEXT, self.onCRLF, self.t5)
        box.Add(self.t5, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)       
        self.RenderOutput(self.GetText())
        self.t5.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_OK, " &OK ")
        btn.SetDefault()
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
        btn = wx.Button(self, wx.ID_CANCEL, " &Cancel ")
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
    
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)     
        

    def OnSetFocus(self, event):        
        self.t5.SetInsertionPointEnd()
        return
        
    def GetText(self):
        return self.t5.GetValue().strip()

    def RenderOutput(self, text):
        dstyl = self.t5.GetDefaultStyle()
        styl = list()
        styl.append(wx.TextAttr())
        styl.append(wx.TextAttr())
        styl[0].SetBackgroundColour(wx.Colour(196,255,196))
        styl[1].SetBackgroundColour(wx.Colour(196,196,255))
        stylnum = 0;
        
        old_pos = self.t5.GetSelection()
        s = text
        s.replace("\r","")
        out = ""
        lines = list()
        start = 0
        for line in s.split("\n"):
            if (line.strip()==""):
                # prázdný řádek
                continue
            out += line+"\n"
            end = start+len(line)
            lines.append((start,end))
            # jsem na konci, přičtu newline
            start = end+1
        self.t5.SetValue(out)
        for inds in lines:
            self.t5.SetStyle(inds[0],inds[1],styl[stylnum])
            stylnum = 1-stylnum
        self.t5.SetSelection(old_pos[0],old_pos[1])
        #self.t5.SetSelection(1,1)

    def onCRLF(self, event):
        if (vars(self).has_key("semaforeCRLF")):
            # tato funkce není reentrantní!
            return
        self.semaforeCRLF = True
            
        # voláno při každé změně,       
        self.RenderOutput(event.GetString())
        del self.semaforeCRLF


