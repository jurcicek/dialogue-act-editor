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

class PromptingChoice(wx.Choice):
    def __init__(self, parent, id, size, choices = [], style = 0):
        self.choices = choices
        self.phrase = ''
        self.circle = 0
        self.oldSelection = -1
        wx.Choice.__init__(self, parent, id, size, choices = choices, style = style)
        self.Bind(wx.EVT_CHAR, self.EvtChar, self)

    def EvtChar(self, event):
        keycode = event.GetKeyCode()
        if keycode == 32:
            # Do the default action for space keycodes
            event.Skip()
            return 0
        elif keycode not in range(28,256):
            # Do the default action for nonascii keycodes
            event.Skip()
            return 0
        else:
            self.phrase = chr(keycode).lower()
        
        if self.phrase == '':
            # Don't select 1st item if phrase is blank
            return 0
        for choice in self.choices:
            choice = choice.lower()
            if choice.startswith(self.phrase):
                self.SetStringSelection(choice)
                newSelection = self.GetSelection()
                if self.oldSelection == newSelection:
                    self.circle += 1
                    self.SetSelection(self.oldSelection + self.circle)
                    if self.GetStringSelection()[0] != self.phrase[0]:
                        self.circle = 0
                        self.SetSelection(self.oldSelection + self.circle)
                self.oldSelection = newSelection

                break

        return 0
    
    def Select(self, arg):
        wx.Choice.Select(self, arg)
        self.oldSelection = self.GetSelection()
        
    def Set(self, choices):
        self.choices = choices
        self.phrase = ''
        wx.Choice.Set(self, choices)
        return 0
