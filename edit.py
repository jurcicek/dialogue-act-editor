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
import codecs, platform
import webbrowser
import datetime
import os, wx, re, glob, wx.lib.layoutf
import wx.lib.dialogs, wx.lib.layoutf, wx.lib.scrolledpanel

from editor_model import *
from dialogs import *
from TriListCtrl import *
from DescribeDialog import *
from ScrolledMessageEditDialog import *
from SingleDAEditDialog import *
from DAEditDialog import *
from DAEHtmlListBox import *
from TranslateDialog import *
from ConfigDialog import *

class DEAFrame(wx.Frame):

    def MakeButton(self, label, func, button_id = -1):
        button = wx.Button(self.panel, button_id, label, size=self.button_size)        
        button.Bind(wx.EVT_BUTTON, func)
        self.buttons.Add(button, 0)
        return button    
        
    def MakeSpacer(self):
        self.buttons.Add(wx.StaticLine(self.panel,-1,style=wx.LI_VERTICAL,size=(0,10)))     

    def __init__(
        self, parent, ID, title, datovy_model, filename=None,
            pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):

        # FRAME
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)        
        self.SetAutoLayout(False)
        self.defaultLabel = self.GetLabel()+" "
        # self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.panel = wx.Panel(self, -1)

        # DATAMODEL        
        self.dm = datovy_model
        self.window_title = "DAE"

        # TLACITKA  
        self.button_size = (120,-1)
        self.buttons = wx.BoxSizer(wx.VERTICAL)
        
        self.MakeButton("", self.OnClose, wx.ID_CLOSE)  
        
        self.MakeSpacer()
        
        self.MakeButton("", self.OnOpenXML, wx.ID_OPEN)
        self.MakeButton("", self.OnSaveXML, wx.ID_SAVE)

        self.MakeSpacer()
        self.MakeButton("S&how XML", self.OnSource)
        # self.MakeButton("&Edit turn XML", self.OnEditRAWTurn)
        self.MakeButton("&Describe", self.OnDescribe)
        self.MakeButton("&Annotate", self.OnAnnotate)
        self.MakeButton("&Translate", self.OnTranslate)

        self.MakeSpacer()
        
        self.MakeButton("", self.OnPrint, wx.ID_PRINT)   
        self.MakeButton("Confi&guration", self.OnConfigEdit)
        
        # self.MakeSpacer()
        # self.MakeButton("Change a &view", self.OnChangeView)             

        # CHOOSE A VIEW:
        choices = [ 
          (0, "text","Only TXT"),
          (1, "da", "Only DAs"),
          (2, "text_da","Both TXT+DAs"),
          (3, "translation", "Translation"),
          (4, "da_with_states", "DAs with states")]
            
        self.radioBox = wx.RadioBox(self.panel,-1, 
            label="Choose a view",
            choices = map(lambda x: x[2], choices),
            style=wx.VERTICAL,
            size=(120,-1))
        self.radioBox.SetSelection(2)
        self.radioBox.choices = choices
        self.radioBox.Bind(wx.EVT_RADIOBOX, self.OnChangeViewRB)
        self.buttons.Add(self.radioBox,0)

        self.MakeSpacer()
        button = wx.Button(self.panel, wx.ID_REFRESH, size=self.button_size)        
        button.Bind(wx.EVT_BUTTON, self.RefreshDir)
        self.buttons.Add(button, 0)     
        
        self.MakeSpacer()
        
        self.btns_stavy = []
        self.btns_stavy.append(self.MakeButton("Stav &1", lambda e: self.OnStav(1,e)))
        self.btns_stavy.append(self.MakeButton("Stav &2", lambda e: self.OnStav(2,e)))
        self.btns_stavy.append(self.MakeButton("Stav &3", lambda e: self.OnStav(3,e)))
        self.btns_stavy.append(self.MakeButton("Stav &4", lambda e: self.OnStav(4,e)))
        self.btns_stavy.append(self.MakeButton("Stav &5", lambda e: self.OnStav(5,e)))
        self.btns_stavy.append(self.MakeButton("Stavy - napoveda", self.HelpOnStav))
        
        
        # TURNS LISTBOX        
        self.lstTurn = DAEHtmlListBox(self.panel, -1, size=(-1,-1), style=wx.BORDER_SUNKEN | wx.EXPAND)
        self.dm.turns = list()
        self.dm.dom = False
        self.lstTurn.dm = self.dm
        self.lstTurn.SetItemCount(0)
        self.lstTurn.Bind(wx.EVT_LISTBOX_DCLICK, self.OnAnnotate)
        self.lstTurn.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.lstTurn.Bind(wx.EVT_LISTBOX, self.UpdateBtns)
        
        
        #if self.dm.editor_mode == "signed":
        #    # editor prekladu do znakove reci
        #    self.radioBox.SetSelection(3)
        #    self.lstTurn.Bind(wx.EVT_LISTBOX_DCLICK, self.OnTranslate)
        #    self.OnChangeViewRB(None)
        
        self.radioBox.SetSelection(2)
        for (key,val,text) in self.radioBox.choices:            
            if val == self.dm.editor_mode:
                self.radioBox.SetSelection(key)
                print "Setting mode: %s (%d)" % (val, key)
                break              
         
        self.OnChangeViewRB(None)
    
        # search text and butons
        sizerSelectDir = wx.BoxSizer(wx.HORIZONTAL)
        self.textSearch = wx.TextCtrl(self.panel, -1, "", size=(-1,-1))
        self.textSearch.Bind(wx.EVT_KEY_DOWN, self.OnTextSearchKey)
        srchDir = wx.Button(self.panel, -1, "Search in the direc(&z)tory")
        srchDir.Bind(wx.EVT_BUTTON, self.OnSearchInDir)
        srchDlg = wx.Button(self.panel, -1, "Search in the dialog(&x)ue")
        srchDlg.Bind(wx.EVT_BUTTON, self.OnSearchInDlg)

        sizerSelectDir.Add(self.textSearch, 1, wx.ALL | wx.EXPAND, 5)
        sizerSelectDir.Add(srchDir)
        sizerSelectDir.Add(srchDlg)

        # DIALOGS LISTBOX
        self.lstDialog = TriListCtrl(self.panel,-1,["File name", "Processing state", "Description"], size=(-1, -1))        
        self.lstDialog.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnOpenXML)
        
        
        # MAIN LAYOUT               
        sizerTB = wx.BoxSizer(wx.HORIZONTAL)          
        sizerTB.Add(self.lstTurn, 1, wx.EXPAND)
        sizerTB.Add(self.buttons, 0, wx.EXPAND)       
        
        sizerTBD = wx.BoxSizer(wx.VERTICAL)
        sizerTBD.Add(sizerTB, 9, wx.EXPAND)               
        sizerTBD.Add(sizerSelectDir, 0, wx.EXPAND)
        sizerTBD.Add(self.lstDialog, 2, wx.EXPAND)               
        
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
        # status bar can be used for DEBUG purposes
        self.CreateStatusBar()
        self.SetStatusText("OK")
                   
        self.panel.SetSizer(sizerTBD)      
        self.lstDialog.SetFocus()
        
        self.RefreshDir(None)
        self.ShowStavyBtns(False)
        
        if filename != None:
            self.OnOpenXML(None, filename)



    def UpdateBtns(self, evt):
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return
        spk = self.dm.turns[n].getAttribute("speaker")
        self.ShowStavyBtns(spk == "user")                                              
        
    def ShowStavyBtns(self, show = False):
        for b in self.btns_stavy:
            b.Enable(show)             
      
    def HelpOnStav(self, evt):
        print "Help On Stav"
        
        
    def RefreshWindow(self):        
        if self.dm.GetModified():
            self.SetLabel(self.window_title + " (modified)")
        else:
            self.SetLabel(self.window_title)
        self.lstTurn.RefreshAll()
        
    def OnStav(self, cislo_stavu, evt):
        n = self.lstTurn.GetSelection()
        # t = self.dm.turns[n]
        das = self.dm.RetrieveDA_DOM(n)
        for i in range(len(das)-1,0,-1):
          das[i].setAttribute("state5",das[i-1].getAttribute("state5"))
        das[0].setAttribute("state5", str(cislo_stavu))
        self.dm.SetModified()        
        self.RefreshWindow()
        
        # self.dm.ReplaceTurn(n, t)
        # print "We are here %d" % cislo_stavu
        
    def OnTextSearchKey(self, event):
        kc = event.GetKeyCode() 
        if kc == wx.WXK_RETURN:
            self.OnSearchInDir(event)
        else:
            event.Skip()
            
    def OnSearchInDir(self, event):
        self.SetStatusText("Searching in current directory.")
        
        self.lstDialog.data = glob.glob(self.dm.datadir + "/*.xml")
        self.lstDialog.StoreSelected()
        self.lstDialog.DeleteAllItems()
        
        searchRequest = self.textSearch.GetValue().split(' ')

        for filename in self.lstDialog.data:
            try:
                dom = xml.dom.minidom.parse(filename)
            except xml.parsers.expat.ExpatError:
                
                # MOD by JZ @ 5.8.2005
                # continue with other files                
                print "XML parsing error in file %s" % filename
                continue
        
            if self.SearchInString(dom, searchRequest):
                self.InsertDialogue(dom, filename)
        
        self.lstDialog.SortListItems()
        self.lstDialog.SetFocus()
        self.Refresh()
        
        self.SetStatusText("OK")

    def OnSearchInDlg(self, event):
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return                      
        
        searchRequest = self.textSearch.GetValue().split(' ')
        
        for turn in range(n + 1, self.dm.GetTurnNum()):
            if self.SearchInString(self.dm.turns[turn], searchRequest):
                self.lstTurn.SetSelection(turn)
                break
        else:
            for turn in range(0, n):
                if self.SearchInString(self.dm.turns[turn], searchRequest):
                    self.lstTurn.SetSelection(turn)
                    break
        
        self.lstTurn.SetFocus()

    def SearchInString(self, turn, searchRequest):
        msg = myPrettyXml(turn, "unicode").strip()
        
        fnd = True
        for each in searchRequest:
            result = msg.find(each)
            
            if result == -1:
                fnd = False
                break
        
        return fnd
    
    def RefreshDir(self, event):
        self.SetStatusText("Refreshing the list of dialogues.")
        
        self.lstDialog.data = glob.glob(self.dm.datadir + "/*.xml")
        self.lstDialog.StoreSelected()
        self.lstDialog.DeleteAllItems()
        for filename in self.lstDialog.data:
            try:
                dom = xml.dom.minidom.parse(filename)
            except xml.parsers.expat.ExpatError:
                
                # MOD by JZ @ 5.8.2005
                # continue with other files                
                print "XML parsing error in file %s" % filename
                continue
                # sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
                # return False
                
            self.InsertDialogue(dom, filename)
        
        self.lstDialog.SortListItems()
        self.Refresh()
        
        self.SetStatusText("OK")

    def InsertDialogue(self, dom, filename):
        elem = dom.getElementsByTagName("task")[0] #root element
        
        try:
            description = elem.getAttribute("description")
        except:
            description = ""
            
        try:
            processingState = elem.getAttribute("processing-state")
        except:
            processingState = ""
            
        if processingState == "":
            try:
                processingState = elem.getAttribute("processig-state")
                elem.removeAttribute("processig-state")
            except:
                processingState = ""
                
            if processingState == "":
                processingState = "unannotated"
        
        self.lstDialog.InsertItem((filename, processingState, description))
        
    def OnClose(self, event):
        if self.dm.GetModified():           
            ret = MyMsgBox("The dialogue XML was modified. \n \n"
                "Do you want to save the modified dialogue?\n", wx.YES | wx.NO | wx.CANCEL)
            if ret == wx.YES:
                try:
                    self.dm.Save()
                except AttributeError:
                    pass
            if ret == wx.CANCEL:
                return
            # if ret == wx.NO:
            #    continue 
            
        self.Destroy()

    def OnEditRAWTurn(self, event):     
        turn_num = self.lstTurn.GetSelection()
        if turn_num < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return
            
        t = self.dm.turns[turn_num]
        msg = myPrettyXml(t, "unicode")
        dlg = ScrolledMessageEditDialog(self, msg, "Editable source XML of turn %d" % (turn_num+1))
        dlg.ShowModal()
        msg = dlg.GetResult()
        if msg:
            # text není stejný, při stornu vrací False
            # upravit text
            dom = xml.dom.minidom.parseString(msg)
            new_turns = dom.getElementsByTagName("turn")
            # new_turns by milo být pole délky 1
            if (len(new_turns) <1):
                #chyba není to tam!
                MyMsgBox("The element TURN was not found.")
                return
            MyMsgBox("I modified the array of turns.")
            self.dm.ReplaceTurn(turn_num, new_turns[0])
            self.RefreshWindow()           

    def OnKey(self, event):
        kc = event.GetKeyCode() 
        if kc == wx.WXK_RETURN or kc == wx.WXK_SPACE:
            if self.dm.editor_mode == "signed":
                self.OnTranslate(None)
            else:
                self.OnAnnotate(None)
##        elif kc == wx.WXK_ESCAPE:
##            # escape
##            self.Close()
        else:
            event.Skip()

#    def OnChangeView(self, event):
#        try:
#            if self.lstTurn.style == "text":
#                self.lstTurn.style = "da"
#                self.radioBox.SetSelection(1)
#            else:
#                if self.lstTurn.style == "da":
#                    self.lstTurn.style = "text_da"
#                    self.radioBox.SetSelection(2)
#                else:
#                    if self.lstTurn.style == "text_da":
#                        self.lstTurn.style = "translation"
#                        self.radioBox.SetSelection(3)
#                    else:                                             
#                        self.lstTurn.style = "text"
#                        self.radioBox.SetSelection(0)
#                    
#            self.lstTurn.RefreshAll()
#        except AttributeError:
#            pass
            
    def OnChangeViewRB(self, event):
        sel = self.radioBox.GetSelection()
        self.lstTurn.style = self.radioBox.choices[sel][1]        
        self.RefreshWindow()
        
        
    def OnDescribe(self, event):
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return                      
            
        dlg = DescribeDialog(self, -1, "Description", self.dm.getDescription(), 
            self.dm.getProcessingState(), self.dm.processingStateTags)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.dm.setDescription(dlg.getDescription())
            self.dm.setProcessingState(dlg.getProcessingState())
            self.dm.SetModified()
            
            # change attributes in self.lstDialog
            self.lstDialog[self.lstDialog.currentItem] = (self.lstDialog[self.lstDialog.currentItem][0], 
                dlg.getProcessingState(), dlg.getDescription())
            self.lstDialog.Refresh()

        self.RefreshWindow()
        self.lstTurn.SetFocus()

    def OnTranslate(self, event):
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return                      
        # das = self.dm.RetrieveDA(n)         
        dlg = TranslateDialog(self, -1, "Translation", \
                DialogueTurn(self.dm.turns[n]), self.dm)
        
        if dlg.ShowModal() == wx.ID_OK:
            turn = dlg.GetResult()
            # self.dm.StoreTurn(n, das)
            self.dm.turns[n] = turn.GetXMLDOMTurn()
            
        self.RefreshWindow()
        self.lstTurn.SetFocus()

        
    def OnAnnotate(self, event):
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return
            
        das = self.dm.RetrieveDA(n)         
        dlg = DAEditDialog(self, -1, "Editation of dialogue acts", das, self.dm.GetTurnText(n), self.dm)
        
        if dlg.ShowModal() == wx.ID_OK:
            das = dlg.GetDialogActs()
            self.dm.StoreDA(n, das)
            
        self.RefreshWindow()
        self.lstTurn.SetFocus()

    def OnSource(self,event):   
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return
        
        source = self.dm.GetSourceXML() 
        dlg = wx.lib.dialogs.ScrolledMessageDialog(self, source, "Source XML code from file: "+self.dm.filename, 
            size=(700,400))
        dlg.ShowModal()

    def OnOpenXML(self, event, filename = None):
        if self.dm.GetModified():           
            ret = MyMsgBox("The dialogue XML was modified. \n \n" 
                "Do you want to save the modified dialogue?\n", wx.YES | wx.NO | wx.CANCEL)
            if ret == wx.YES:
                try:
                    self.dm.Save()
                except AttributeError:
                    pass
            if ret == wx.CANCEL:
                return
            # if ret == wx.NO:
            #    continue with a new dialogue
        try:
            currentItem = event.m_itemIndex
        except AttributeError:
            currentItem = self.lstDialog.currentItem
   
        try:
            if filename == None:
                filename = self.lstDialog.GetItemText(currentItem)
        except AttributeError:
            ret = MyMsgBox("No dialogue XML is selected. \n \n" 
                "Please, select a dilogue XML that you want to open!\n", wx.OK)
            return
        
        if not self.dm.Load(filename):
            MyMsgBox("File %s cannot be loaded or parsed." % (filename))
            return
            
        loaded_count = self.dm.GetTurnNum()
        self.lstTurn.SetItemCount(loaded_count)
        
        self.dm.ImplicitState5()
        
        if loaded_count > 0:
            self.lstTurn.SetSelection(0)        
        
        self.window_title = self.defaultLabel + ": %s" % self.dm.dialog_id
        self.RefreshWindow()        
        self.lstTurn.SetFocus()                
        self.UpdateBtns(None)

    def OnSaveXML(self, event):
        try:
            self.dm.Save()
        except AttributeError:
            pass
            
    def OnConfigEdit(self, event):
        dlg = ConfigDialog(self, -1, "Configuration", self.dm)
        
        if dlg.ShowModal() == wx.ID_OK:
            self.dm.SaveToConfig()
            pass
            
    def OnPrint(self, event):
        n = self.lstTurn.GetSelection()
        if n < 0:
            MyMsgBox("First of all, open any dialogue XML.", wx.OK)
            return
        
        dh = codecs.open("printed-dialogue.html", "w", "UTF-8")
        
        dh.write('<head>\n')
        dh.write('<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">\n')
        dh.write('</head>\n')
        
        # style - print 
        dh.write('<style media=print>\n')
        dh.write('<!--\n')
        dh.write('H1\n'
            '{\n'
            'font-size:12pt;\n'
            'font-family: arial'
            '}\n')
        dh.write('H2\n'
            '{\n'
            'font-size:9pt;\n'
            'font-family: arial'
            '}\n')
        
        dh.write('.custom, .custom TD, .custom TH\n'
            '{\n'
            'font-size:8pt;\n'
            'font-family: arial'
            '}\n')
        dh.write('-->\n')
        dh.write('</style>\n')

        # style - screen
        dh.write('<style media=screen>\n')
        dh.write('<!--\n')
        dh.write('H1\n'
            '{\n'
            'font-size:15pt;\n'
            'font-family: arial'
            '}\n')
        dh.write('H2\n'
            '{\n'
            'font-size:12pt;\n'
            'font-family: arial'
            '}\n')
        
        dh.write('.custom, .custom TD, .custom TH\n'
            '{\n'
            'font-size:11pt;\n'
            'font-family: arial'
            '}\n')
        dh.write('-->\n')
        dh.write('</style>\n')

        # body 
        dh.write('<body>\n')
        
        dh.write('<h1>\n')
        dh.write(self.dm.filename)
        dh.write('</h1>\n')

        dh.write('<h2>\n')
        dh.write('Date: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        dh.write('</h2>\n')
        dh.write('<h2>\n')
        dh.write('Annotator: ' + self.dm.anotatorid)
        dh.write('</h2>\n')
        
        for n in range(self.dm.GetTurnNum()):
            dh.write(self.lstTurn.OnGetItem(n) + "\n")
            
        dh.write('</font>\n')
        dh.write('</body>\n')
        
        dh.close()
        
        file = os.path.abspath("printed-dialogue.html")
        if platform.system() == "Windows":
            file = os.path.normpath(file)
            file = file.replace("\\","/")
            print file
            os.system("cmd.exe /c start "+file)
        else:
            webbrowser.open(file, True, True)
        
