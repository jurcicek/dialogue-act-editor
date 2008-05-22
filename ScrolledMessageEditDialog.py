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

class ScrolledMessageEditDialog(wx.Dialog):
    def __init__(self, parent, msg, caption,
        pos=wx.DefaultPosition, size=(700,400),
        style=wx.DEFAULT_DIALOG_STYLE):
    
        wx.Dialog.__init__(self, parent, -1, caption, pos, size, style)
        x, y = pos
        if x == -1 and y == -1:
            self.CenterOnScreen(wx.BOTH)
            
        text = wx.TextCtrl(self, -1, msg, style=wx.TE_MULTILINE)
        self.orig_msg = msg
        self.text_control = text
        ok = wx.Button(self, wx.ID_OK, "OK")
        # self.Bind(wx.EVT_BUTTON, self.OnOK, ok)
        ok.SetDefault()
        lc = wx.lib.layoutf.Layoutf('t=t5#1;b=t5#2;l=l5#1;r=r5#1', (self,ok)) 
        text.SetConstraints(lc)
    
        lc = wx.lib.layoutf.Layoutf('b=b5#1;x%w50#1;w!80;h*', (self,))
        ok.SetConstraints(lc)
        self.SetAutoLayout(1)
        self.Layout()
    
    def GetResult(self):
        # default action, save value 
        msg = self.text_control.GetValue()
        if (msg == self.orig_msg):
            return False
        return msg      
        

    
