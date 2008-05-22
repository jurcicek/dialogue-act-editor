# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2006 Jakub Kanis
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import xml.dom.minidom
import xml.parsers.expat
import os, wx, re, glob, wx.lib.layoutf
import wx.lib.dialogs, wx.lib.layoutf, wx.lib.scrolledpanel
import codecs
import re, math

from dialogs import *
from editor_model import *
from semantics import *

class TranslateDialog(wx.Dialog):
    def __init__(self, parent, ID, title, 
        turn,
        dm,
        size=wx.DefaultSize, 
        pos=wx.DefaultPosition, 
        style=wx.DEFAULT_FRAME_STYLE):
        
        wx.Dialog.__init__(self, parent, ID, title, pos, size, style)

        lines = list()
        for line in codecs.open("signed-vocab.txt","r","cp1250"):
            lines.append(line.strip())
        lines.sort();
            
        self.dm = dm
        self.text = re.sub(" +"," ",turn.GetText().strip())
        self.editorcmd = self.dm.editorcmd
        self.translated1 = TranslateTextCtrl(self,-1,"")
        #self.translated1 = wx.TextCtrl(self,-1,"")
        #self.translated2 = wx.TextCtrl(self,-1,"")
        self.listbox1 = TranslateListBox(self,-1,"")
        #self.listbox1 = wx.ListBox(self,-1)
        self.translated1.Dictionary = lines
        self.translated1.Listbox = self.listbox1
        self.translated1.DataModel = self.dm
        self.listbox1.TextCtrl = self.translated1 
        #self.listbox1.InsertItems(lines,0)
        self.InitData(turn)
        label = wx.ListBox(self, -1,size=(400,200))
        texty = self.text.split(' ')
        i = 1
        newtexty = list()
        format = "%%0%dd | %%s" % (int(math.log10(len(texty)) + 1))
        for elem in texty:
            newelem = format % (i, elem)
            newtexty.append(newelem)
            i += 1 	
        label.InsertItems(newtexty,0)
        #label = wx.TextCtrl(self, -1, "", size=(300,100), style=wx.TE_MULTILINE)
        #label.SetValue(turn.GetText().strip())
        MaxIndex = i
        if turn.GetSigned() == "":
            Aligment = "" 
            for i in xrange(1,MaxIndex):
                Aligment += '/' + str(i) + ' '
            
            self.translated1.SetValue(Aligment.strip())
        else:
            self.translated1.SetValue(turn.GetSigned().strip())
        #self.translated2.SetValue(turn.GetSign().strip())
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label, 1, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)     
        sizer.Add(wx.StaticText(self, -1,"Translated signed text"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        sizer.Add(self.translated1, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND,5)                
        #sizer.Add(wx.StaticText(self, -1,"Translated sign text"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        #sizer.Add(self.translated2, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.listbox1, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)       
        # sizer.Add(wx.StaticText(self, -1,"Semantics"),0, wx.ALIGN_LEFT|wx.TOP|wx.LEFT, 5)
        #sizer.Add(self.semanticsTextCtrl, 0, wx.ALIGN_LEFT|wx.ALL|wx.EXPAND, 5)
    
        # buttons
        #ok = wx.Button(self, wx.ID_OK)
        ok = wx.Button(self, -1, "&OK")                
        ok.SetDefault()
        ok.Bind(wx.EVT_BUTTON, self.OnOK)   
        #rel = wx.Button(self, -1, "OK+&Reload voc.")
        #rel.Bind(wx.EVT_BUTTON, self.OnReload)
        #edt = wx.Button(self, -1, "Vocabulary editor")
        #edt.Bind(wx.EVT_BUTTON, self.OnEditor)
        cancel  = wx.Button(self, wx.ID_CANCEL)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(ok, 1, wx.ALIGN_CENTER|wx.ALL, 1)
        #buttons.Add(rel, 1, wx.ALIGN_CENTER|wx.ALL, 1)
        #buttons.Add(edt, 1, wx.ALIGN_CENTER|wx.ALL, 1)
        buttons.Add(cancel, 1 , wx.ALIGN_CENTER|wx.ALL, 1)
        
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
        event.Skip();    

    def OnOK(self, event):
        errors_word = list()
        errors_alig = list()
        s1 = self.translated1.GetValue()
        #s2 = self.translated2.GetValue()
        #for word in self.dm.translation_vocab.iteritems():
        #    print word
        
        if len(s1) > 0:
            errors_tran = list()
            Words = self.text.split(' ')
            NumberOfWords = len(Words)
            format = "%%0%dd | %%s" % (int(math.log10(NumberOfWords)) + 1)
            for i in xrange(1,NumberOfWords + 1):
                pattern = r"[_0-9a-záèïéìíòóøšúùýž]+[/,]%d(,|\s|$)" % (i)
                pattern = pattern.decode("cp1250")
                if re.search(pattern,s1) == None:
                    errors_tran.append(format % (i, Words[i - 1]))
            
            errors_word = list()
            errors_alig = list()
            errors_overrun = list()
            errors_alig_transcription = list()
            tokens = s1.split(' ')
            for token in tokens:        
                word_alig = token.split('/')
                if not self.dm.translation_vocab.has_key(word_alig[0]):
                    errors_word.append(word_alig[0])
                if (len(word_alig) == 1) or (word_alig[1] == ""):
                    errors_alig.append(word_alig[0])
                else:
                    numbers = word_alig[1].split(',')
                    for number in numbers:
                        try:
                            if int(number) > NumberOfWords or int(number) < 1:
                                errors_overrun.append(word_alig[0])
                        except ValueError:
                            errors_alig_transcription.append(word_alig[0])
        
            if (len(errors_tran) > 0) or (len(errors_word) > 0) or (len(errors_alig) > 0) or (len(errors_overrun) > 0) or (len(errors_alig_transcription) > 0):
                translations = ""
                words = ""
                alignments = ""
                overruns = ""
                alig_transcriptions = ""
            
                if len(errors_tran) > 0:
                    for e in errors_tran:
                        translations += "%s\n" % e
                    translations = translations.strip()

                if len(errors_word) > 0:
                    for e in errors_word:
                        words += "%s\n" % e
                    words = words.strip()
            
                if len(errors_alig) > 0:
                    for e in errors_alig:
                        alignments += "%s\n" % e
                    alignments = alignments.strip()

                if len(errors_overrun) > 0:
                    for e in errors_overrun:
                        overruns += "%s\n" % e
                    overruns = overruns.strip()

                if len(errors_alig_transcription) > 0:
                    for e in errors_alig_transcription:
                        alig_transcriptions += "%s\n" % e
                    alig_transcriptions = alig_transcriptions.strip()
            
                message = ""
                
                if len(translations) > 0:
                    message += "Unknown translations:\n%s\n\n" % (translations)                           
                if len(words) > 0:
                    message += "Unknown words:\n%s\n\n" % (words)
                if len(alignments) > 0:
                    message += "Unknown alignment:\n%s\n\n" % (alignments)
                if len(overruns) > 0:
                    message += "Maximal or minimal index of alignment excceds:\n%s\n\n" % (overruns)
                if len(alig_transcriptions) > 0:
                    message += "Error in alignment transcription:\n%s\n\n" % (alig_transcriptions)
                if message == "" > 0:
                    message += "Error in translation!"

                wx.MessageBox(message,"Bad translation",style=wx.ICON_HAND)
            
                return False
        
        #self.vysledek.SetTranslation(s1,s2)
        self.vysledek.SetTranslation(self.text,s1)
        self.EndModal(wx.ID_OK)
        return True
        
    def OnReload(self, event):
         self.dm.LoadTranslationVocab()
         self.OnOK(event)
         
    def OnEditor(self, event):
        os.system("cmd /c start "+self.editorcmd)               

    def InitData(self,turn):	
		    self.vysledek = turn
        
    def GetResult(self):        
        return self.vysledek

class TranslateTextCtrl(wx.TextCtrl):
    def __init__(self, parent, id, concepts, 
        size = wx.DefaultSize, sizeC = (400, 150, 10)):
        wx.TextCtrl.__init__( self, parent, id, size = size, 
            style=wx.EXPAND)
            
        self.Dictionary = list()
        self.Listbox = None
        self.DataModel = None
        
        #self.Bind(wx.EVT_CHAR, self.OnKey)
        self.Bind(wx.EVT_TEXT, self.OnTextChange)
        #self.Bind(wx.EVT_KEY_DOWN, self.OnKey)
    
    def OnTextChange(self, event):
        self.DataModel.SetModified()
        #print "***OnTextChange***"
        Word = ""
        String = ""
        InsPoint = self.GetInsertionPoint()
                        
        String = self.GetValue()
        
        if String != "":
            #print "%d %s" %(InsPoint, String)
        
            Counter = InsPoint    
            while (Counter > 0) and (String[Counter - 1] != ' '):
                Counter -= 1
       
            while (Counter < len(String)) and (String[Counter] != ' ') and (String[Counter] != '/'):
                Word += String[Counter]
                Counter += 1
        		
            #print Word
        		
            if Word != "":
                Words = list()
                for Record in self.Dictionary:
                    if Record.find(Word) == 0:
                        Words.append(Record)
            
                if Words != []:
                    self.Listbox.Set("")
                    self.Listbox.InsertItems(Words,0)
        else:
            self.Listbox.Set("")
        
        #print "---OnTextChange---"
        
        event.Skip()                                     

class TranslateListBox(wx.ListBox):
    def __init__(self, parent, id, concepts, 
        size = wx.DefaultSize, sizeC = (400, 150, 10)):
        wx.ListBox.__init__( self, parent, id, size = size, 
            style=wx.EXPAND)
            
        self.TextCtrl = None
        
        self.Bind(wx.EVT_CHAR, self.OnSpace)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDbClick)
    
    def OnSpace (self, event):
        #print "***OnSpace***"
        if event.GetKeyCode() == wx.WXK_SPACE:
            Line = (self.GetString(self.GetSelection())).strip()
            Words = Line.split(" ")
            InsPoint = self.TextCtrl.GetInsertionPoint()
            if InsPoint != 0:
                InsPoint -= 1
            
            Translation = self.TextCtrl.GetValue()
            LengthOfTran = len(Translation)
            
            SpaceIndexPred = Translation[0:InsPoint + 1].rfind(" ")
            
            Counter = InsPoint    
            while (Counter < LengthOfTran) and (Translation[Counter] != ' ') and (Translation[Counter] != '/'):
                Counter += 1
        
            if (Counter == (LengthOfTran - 1)) and (Translation[Counter] != ' ') and (Translation[Counter] != '/'):
                SpaceIndexSuc = -1
            else:
                SpaceIndexSuc = Counter
            
            if SpaceIndexPred == -1 and SpaceIndexSuc == -1:
                self.TextCtrl.Replace(0, LengthOfTran, Words[0])
                NewInsPoint = len(Words[0])
            elif SpaceIndexPred == -1 and SpaceIndexSuc != -1:
                self.TextCtrl.Replace(0, SpaceIndexSuc, Words[0])
                NewInsPoint = len(Words[0])
            elif SpaceIndexPred != -1 and SpaceIndexSuc == -1:
                self.TextCtrl.Replace(SpaceIndexPred + 1, LengthOfTran, Words[0])
                NewInsPoint = LengthOfTran + len(Words[0])
            else:
                self.TextCtrl.Replace(SpaceIndexPred + 1, SpaceIndexSuc, Words[0])
                NewInsPoint = SpaceIndexPred + 1 + len(Words[0])
            
            #print "%d %c %s %d %d" %(InsPoint, Translation[InsPoint], Translation, SpaceIndexPred, SpaceIndexSuc)
        
            self.TextCtrl.SetInsertionPoint(NewInsPoint)
        
        #print "---OnSpace---"
            
        event.Skip()
        
    def OnDbClick (self, event):
        #print "***OnDbClick***"
        if self.GetSelection() != -1:
            Line = (self.GetString(self.GetSelection())).strip()
            Words = Line.split(" ")
            InsPoint = self.TextCtrl.GetInsertionPoint()
            if InsPoint != 0:
                InsPoint -= 1
            
            Translation = self.TextCtrl.GetValue()
            LengthOfTran = len(Translation)
            
            SpaceIndexPred = Translation[0:InsPoint + 1].rfind(" ")
        
            Counter = InsPoint    
            while (Counter < LengthOfTran) and (Translation[Counter] != ' ') and (Translation[Counter] != '/'):
                 Counter += 1
        
            if (Counter == (LengthOfTran - 1)) and (Translation[Counter] != ' ') and (Translation[Counter] != '/'):
                 SpaceIndexSuc = -1
            else:
                 SpaceIndexSuc = Counter
            
            if SpaceIndexPred == -1 and SpaceIndexSuc == -1:
                 self.TextCtrl.Replace(0, LengthOfTran, Words[0])
                 NewInsPoint = len(Words[0])
            elif SpaceIndexPred == -1 and SpaceIndexSuc != -1:
                 self.TextCtrl.Replace(0, SpaceIndexSuc, Words[0])
                 NewInsPoint = len(Words[0])
            elif SpaceIndexPred != -1 and SpaceIndexSuc == -1:
                 self.TextCtrl.Replace(SpaceIndexPred + 1, LengthOfTran, Words[0])
                 NewInsPoint = LengthOfTran + len(Words[0])
            else:
                 self.TextCtrl.Replace(SpaceIndexPred + 1, SpaceIndexSuc, Words[0])
                 NewInsPoint = SpaceIndexPred + 1 + len(Words[0])
            
            #print "%d %c %s %d %d" %(InsPoint, Translation[InsPoint], Translation, SpaceIndexPred, SpaceIndexSuc)
        
            self.TextCtrl.SetInsertionPoint(NewInsPoint)
        
            #print "---OnDbClick---"
            
            event.Skip()
            
#############################################################################
## test of dialogue
#############################################################################

if __name__ == "__main__":
    app = wx.PySimpleApp()
    dialog_act = DialogueAct()
    
    dialog_act.domain = "2"
    dialog_act.speechAct = "3"
    dialog_act.semantics = "TXT"
    dialog_act.text = "qwer qwert zxcv zxcv"
    
    dlg = TranslateDialog(None, -1, "Dialog act editor",
        DialogueTurn(1))
    dlg.ShowModal() 
    
