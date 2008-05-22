# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import wx
import sys, platform

from semantics import *

class SmntcTextCtrl(wx.TextCtrl):
    def __init__(self, parent, id, concepts, 
        size = wx.DefaultSize, sizeC = (400, 150, 10)):
        wx.TextCtrl.__init__( self, parent, id, size = size, style = wx.EXPAND or wx.WANTS_CHARS)
        # style=wx.EXPAND
        # self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS)
		
        self.concepts = concepts
        self.oldAlt = False
        self.oldChar = ""
        self.circle = 0
        
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKey)

    def ProcessEvent(self, e):
        print "Process"
        
    def IsConcept(self, char):
        # each concept can consists of UPPER LETTERS and "_"
        if char == "_":
            return True
        elif char.isalpha() and char.isupper():
            return True
        else:
            return False
    
    def DeletePreviousConcept(self):
        strng = self.GetValue()
        insPoint = self.GetInsertionPoint()
        
        if insPoint == 0:
            # I am at the begining of string; there is nothing to delete.
            return
            
        delConcept = self.IsConcept(strng[insPoint - 1])

        strngA = strng[:insPoint]
        strngB = strng[insPoint:]
        for i in range(len(strngA)-1,-1, -1):
            if delConcept:
                # stop when you encounter non-concept char
                if not self.IsConcept(strngA[i]):
                    strngA = strngA[:i+1]
                    break
                elif i == 0:
                    strngA = ""
                    break
            else:
                # stop when you encounter concept char
                if self.IsConcept(strngA[i]):
                    strngA = strngA[:i+1]
                    break
                elif i == 0:
                    strngA = ""
                    break
                
        self.SetValue(strngA + strngB)
        self.SetInsertionPoint(len(strngA))

    def DeleteFollowingConcept(self):
        strng = self.GetValue()
        insPoint = self.GetInsertionPoint()
        
        if insPoint == len(strng):
            # I am at the end of the string; there is nothing to delete.
            return
            
        delConcept = self.IsConcept(strng[insPoint])

        strngA = strng[:insPoint]
        strngB = strng[insPoint:]
        for i in range(len(strngB)):
            if delConcept:
                # stop when you encounter non-concept char
                if not self.IsConcept(strngB[i]):
                    strngB = strngB[i:]
                    break
                elif i == len(strngB)-1:
                    strngB = ""
                    break
            else:
                # stop when you encounter concept char
                if self.IsConcept(strngB[i]):
                    strngB = strngB[i:]
                    break
                elif i == len(strngB)-1:
                    strngB = ""
                    break
                
        self.SetValue(strngA + strngB)
        self.SetInsertionPoint(len(strngA))

    def MoveOnLeftConcept(self):
        strng = self.GetValue()
        insPoint = self.GetInsertionPoint()
        
        i = -1
        for i in range(insPoint-1,-1, -1):
            if not self.IsConcept(strng[i]) or i == 0:
                break
                
        if i >= 0:
            self.SetInsertionPoint(i)

    def MoveOnRightConcept(self):
        strng = self.GetValue()
        insPoint = self.GetInsertionPoint()
        
        i = -1
        for i in range(insPoint, len(strng)):
            if not self.IsConcept(strng[i]):
                break
        
        if i >= 0:
            self.SetInsertionPoint(i+1)

    
    def OnChar(self, event):
        print "SMNTC: OnChar(event) %d" % event.GetKeyCode() 
        if event.AltDown() or event.GetKeyCode()<32:
            print "AltKey"
            return

        event.Skip()
        return
        
    def OnKey(self, event):
        """ Implements shortcuts for concepts.
        """               
        print "SMNTC: OnKey(event) %d" % event.GetKeyCode() 
        kc = event.GetKeyCode() 
        # event.Skip()
        # return
        
        delLastConcept = False  

        
        # DEBUG print
        # print "Key = %d, mods: %d,%d,%d" % (event.GetKeyCode(),event.ControlDown(),event.AltDown(),event.ShiftDown())             
		
        #skip short cuts select all, copy, paste, cut
        if event.ControlDown() and kc >= 32 and kc<128:
            kcc = chr(kc).upper()
            if kcc == "A"or kcc == "C" or kcc == "V" or kcc == "X":
                event.Skip()
                return
                
        shrtCut = event.ControlDown() or event.AltDown()
        #shrtCut = event.AltDown()
        
        #if platform.system() == "Windows" and kc>=ord('A') and kc<=ord('Z'):            
		#	shrtCut = True            
        
        if kc == wx.WXK_BACK and shrtCut:
            self.DeletePreviousConcept()
            return
        if kc == wx.WXK_DELETE and shrtCut:
            self.DeleteFollowingConcept()
            return
        if kc == wx.WXK_LEFT and shrtCut:
            self.MoveOnLeftConcept()            
            return
        if kc == wx.WXK_RIGHT and shrtCut:
            self.MoveOnRightConcept()
            return
            
        if shrtCut and kc>=48 and kc<128:      
            add = ""
            kc = chr(kc).upper()
            for i in range(len(self.concepts)):
                if self.concepts[i][0] == kc:
                    # I found at least one concept starting with kc char
                    
                    # may I use the first choice?
                    if self.oldAlt and self.oldChar == kc:
                        # no
                        self.circle += 1
                        
                        try:
                            if self.concepts[self.circle][0] == kc:
                                add = self.concepts[self.circle]
                            else:
                                self.circle = i
                                add = self.concepts[self.circle]
                        except IndexError:
                            self.circle = i 
                            add = self.concepts[self.circle]

                        delLastConcept = True
                    else:
                        # yes
                        self.circle = i
                        add = self.concepts[self.circle]
                
                    break
                    
                if kc == " ":
                    add = ", "
                
            if delLastConcept:                
                self.DeletePreviousConcept()
            
            strng = self.GetValue()
            
            # MOD by JZ: smazani selection pred vkladanim
            (iFrom,iTo) = self.GetSelection()            
            if (iFrom != iTo):
                # smazat selection before operation
                strng = strng[:iFrom] + strng[iTo:]
                insPoint = iFrom
            else:            
                insPoint = self.GetInsertionPoint()      
            # END MOD
                      
            strngA = strng[:insPoint]
            strngB = strng[insPoint:]
            if not len(strngA) == 0 and not add == ", " and not add == "":
                if strngA[-1].isalpha() and strngA[-1].isupper():
                    strngA += "("
            # fix insertation point pak to bude dobre, pozor na mazani konceptu
            
            self.SetValue(strngA + add + strngB)
            self.SetInsertionPoint(len(strngA) + len(add))
            event.Skip()
        else:
            event.Skip()
            
        self.oldAlt = shrtCut
        self.oldChar = kc
                                           
        

    def Validate(self):
        try:
            smntcs = Semantics("", self.GetValue(), "")
            smntcs.semantics = smntcs.semantics.replace(',', ', ')
            self.SetValue(smntcs.semantics)
        except ValueError:
            wx.MessageBox("Semantics has to contain valid annotation!\n" + str(sys.exc_value), 
                "Error", wx.OK | wx.ICON_ERROR)
            self.SetBackgroundColour(wx.Colour(255, 210, 150))
            self.SetFocus()
            self.Refresh()
            
            return False
        
        return True
            
    def ResetValidation(self):
        self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        self.Refresh()


#############################################################################
## test 
#############################################################################

#----------------------------------------------------------------------
# The main window
#----------------------------------------------------------------------
# This is where you populate the frame with a panel from the demo.
#  original line in runTest (in the demo source):
#    win = TestPanel(nb, log)
#  this is changed to:
#    self.win=TestPanel(self,log)
#----------------------------------------------------------------------

if __name__ == '__main__':
    concepts = [
        "ACCEPT",
        "ARRIVAL",
        "ARRIVAL_CONF",
        "ARRIVAL_TIME",
        "BACK",
        "DEPARTURE",
        "DEPARTURE_CONF",
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
    
            
    class TestDialog(wx.Dialog):
        def __init__(self, parent, id, title, size, style = wx.CAPTION or wx.CLOSE_BOX or wx.SYSTEM_MENU  ):
            wx.Dialog.__init__(self, parent, id, title, size=size, style=style or wx.WANTS_CHARS)
    
            # self.CreateStatusBar(1)
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.win = SmntcTextCtrl(self, -1, concepts)
            sizer.Add(self.win)
            # sizer.Fit(self)
            self.SetSizer(sizer)
            #self.win.SetFocus()            

            
    class TestFrame(wx.Frame):
        def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
            wx.Frame.__init__(self, parent, id, title, size=size, style=style)
    
            self.CreateStatusBar(1)
    
            #self.win = SmntcTextCtrl(self, -1, concepts)
            #self.win.SetFocus()
            self.dlg = TestDialog(self,-1,title, size);
            self.dlg.ShowModal()
            
    app = wx.PySimpleApp()
    
    dlg = TestDialog(None,555,"pokus", wx.Size(500,100));
    dlg.ShowModal()
    """
    f = TestFrame(None, -1, "Semantics Text Ctrl", wx.Size(500,100))
    f.Center()
    f.Show()
    app.MainLoop()
    """
