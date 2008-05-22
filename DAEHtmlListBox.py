# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import os, wx, re, glob, wx.lib.layoutf
import wx.lib.dialogs, wx.lib.layoutf, wx.lib.scrolledpanel

from editor_model import *

class DAEHtmlListBox(wx.HtmlListBox):
    # var style = "text", "da"    

    def OnGetItem(self, n):     
        # print "OnGetItem da+stat "+ self.style        
        if (n>=self.dm.GetTurnNum()):
            return "Error: index <b>%d</b>" % n            
        if (not vars(self).has_key("style")):
            self.style = "text_da"            
        if (self.style == "text"):
            return self.RenderText(n)
        if (self.style == "da"):
            return self.RenderDA(n)
        if self.style == "translation":
            return self.RenderTranslation(n)
        if self.style == "translation_da":
            return self.RenderTranslationDA(n)
        if self.style == "da_with_states":            
            return self.RenderTextDAwithStates(n)
        
        return self.RenderTextDA(n)                

    def RenderText(self, n):
        speaker = self.dm.turns[n].getAttribute("speaker")
        number = self.dm.turns[n].getAttribute("number")
        color = self.dm.getSpeakerColor(speaker)        
        text = self.dm.GetTurnText(n)
            
        return "<table cellspacing='0' cellpadding='0'><tr> \
            <td align='right' valign='top' width='30'> %(num)s:</td> \
            <td valign='top' width='75'><b><font color=%(col)s>%(spk)s</font>:</b></td> \
            <td><font color=%(col)s>%(da)s</font></td></tr></table>" % \
            {'col':color, 'spk':speaker, 'num':number, 'da':text} 
            
        return "%d: <b><font color=%s>%s</font></b>: %s" % (n+1, color, speaker, text)
            
    def RenderDA(self, n):
        t = self.dm.turns[n]
        speaker = t.getAttribute("speaker")
        number = self.dm.turns[n].getAttribute("number")
        color = self.dm.getSpeakerColor(speaker)        
        das = t.getElementsByTagName("dialogue_act")
        
        s=""
        for da in das:
            a1 = da.getAttribute("conversational_domain")
            a2 = da.getAttribute("speech_act")
            a3 = da.getAttribute("semantics")
            if len(a3)==0:
                a3 = da.getAttribute("task_subtask")                

            (a1, a2, a3) = self.FillAs(a1, a2, a3)

            a = "<br><code>%-17s %-24s " % (a1,a2)
            a = a.replace(' ','&nbsp;')
            a += a3 + "</code>"
            s += a

        if (len(s) == 0):
            s = "* <b>%s</b>: no dialogue acts specified *" % speaker
        else:
            if (s[0:4] == "<br>"):
                s = s[4:]
        
        return "<table cellspacing='0' cellpadding='0' class='custom'><tr> \
            <td align='right' valign='top' width='30'> %(num)s:</td> \
            <td valign='top' width='75'><b><font color=%(col)s>%(spk)s</font>:</b></td> \
            <td><font color=%(col)s>%(da)s</font></td></tr></table>" % \
            {'col':color, 'num':number, 'spk':speaker, 'da':s} 
            
            

    def RenderTextDAwithStates(self, n):          
        t = self.dm.turns[n]
        speaker = t.getAttribute("speaker")
        number = self.dm.turns[n].getAttribute("number")
        color = self.dm.getSpeakerColor(speaker)        
        text = self.dm.GetTurnText(n)
        das = t.getElementsByTagName("dialogue_act")
        
        s = ""
        for da in das:
            a1 = da.getAttribute("conversational_domain")
            a2 = da.getAttribute("speech_act")
            a3 = da.getAttribute("semantics")
            s5 = da.getAttribute("state5")
            if len(a3) == 0:
                a3 = da.getAttribute("task_subtask")  
                
            if len(s5) > 0:
                s5 = "stav %s" % s5             
                        
            (a1, a2, a3) = self.FillAs(a1, a2, a3)
            
            s += "<br><b>%s</b>" % da.toxml()
            a = "<br><code><font color=#009900>%-10s</font><font color=%s>%-17s %-24s " % (s5,color,a1,a2)
            a = a.replace(' ','&nbsp;')
            a = a.replace('t&nbsp;c', 't c')
            a += a3 + "</code></font>"
            s += a
        
        if (len(s) == 0):
            s = "<b>%s</b>" % text
        else:
            if (s[0:4] == "<br>"):
                s = s[4:]

        return "<table cellspacing='0' cellpadding='0' class='custom'><tr> \
            <td align='right' valign='top' width='30'> %(num)s:</td> \
            <td valign='top' width='75'><b><font color=%(col)s>%(spk)s</font>:\
            </b></td> \
            <td>%(da)s</td></tr></table>" % \
            {'col':color, 'spk':speaker,  'num':number, 'da':s, 'state': s5}
            
    def RenderTextDA(self, n):    
        t = self.dm.turns[n]
        speaker = t.getAttribute("speaker")
        number = self.dm.turns[n].getAttribute("number")
        color = self.dm.getSpeakerColor(speaker)        
        text = self.dm.GetTurnText(n)
        das = t.getElementsByTagName("dialogue_act")
        
        s = ""
        for da in das:
            a1 = da.getAttribute("conversational_domain")
            a2 = da.getAttribute("speech_act")
            a3 = da.getAttribute("semantics")
            if len(a3) == 0:
                a3 = da.getAttribute("task_subtask")  
                
                        
            (a1, a2, a3) = self.FillAs(a1, a2, a3)
            
            s += "<br><b>%s</b>" % da.toxml()
            a = "<br><code><font color=%s>%-17s %-24s " % (color,a1,a2)
            a = a.replace(' ','&nbsp;')
            a = a.replace('t&nbsp;c', 't c')
            a += a3 + "</font></code>"
            s += a
        
        if (len(s) == 0):
            s = "<b>%s</b>" % text
        else:
            if (s[0:4] == "<br>"):
                s = s[4:]

        return "<table cellspacing='0' cellpadding='0' class='custom'><tr> \
            <td align='right' valign='top' width='30'> %(num)s:</td> \
            <td valign='top' width='75'><b><font color=%(col)s>%(spk)s</font>:\
            </b></td> \
            <td>%(da)s</td></tr></table>" % \
            {'col':color, 'spk':speaker,  'num':number, 'da':s}
                
    
    def RenderTranslation(self, n):
        speaker = self.dm.turns[n].getAttribute("speaker")
        number = self.dm.turns[n].getAttribute("number")
        color = self.dm.getSpeakerColor(speaker)        
        turn = DialogueTurn(self.dm.turns[n])
        aligs = self.dm.turns[n].getElementsByTagName("alignment")
        
        words = dict()
        signs = dict()
        for alig in aligs:
            indexes = (alig.getAttribute("order_text")).split(',') 

            words[int(indexes[0])] = "%s" % (alig.getAttribute("source_text"))
            signs[int(indexes[0])] = "%s" % (alig.getAttribute("trans_text"))
            for i in xrange(1,len(indexes)):
                words[int(indexes[i])] = ""
                signs[int(indexes[i])] = ""       

        signed = ""
        change_color = 1    
        source_text = ""
        trans_text = ""
        for i in xrange(1,len(words) + 1):
            word = words.get(i,"")
            sign = signs.get(i,"")
            if word != "":
                if (change_color % 2) == 0:
                   source_text += "<font color=#cc3300><code>%s " % (word)
                   trans_text += "<font color=#cc3300><code>%s " % (sign)
                else:
                   source_text += "<font color=#000099><code>%s " % (word)
                   trans_text += "<font color=#000099><code>%s " % (sign)
                    
                change_color += 1

                word_len = len(word)
                sign_len = len(sign)
                if word_len > sign_len:
                    trans_text += (word_len - sign_len) * "&nbsp;"
                else:
                    source_text += (sign_len - word_len) * "&nbsp;"
                    
                source_text += "</code></font>"
                trans_text += "</code></font>"
        if source_text == "":
            signed += "%s" % (turn.GetText().strip())
        else:
            signed += "<br>%s" % source_text
            signed += "<br>%s" % trans_text
        
            
        return "<table cellspacing='0' cellpadding='0'><tr> \
            <td align='right' valign='top' width='30'> %(num)s:</td> \
            <td valign='top' width='75'><b><font color=%(col)s>%(spk)s</font>:</b></td> \
            <td> %(signed)s</td></tr></table>" \
            % {'col':color, 'spk':speaker, \
            'num': number,'signed': signed}

    def RenderTranslationDA(self, n):
        speaker = self.dm.turns[n].getAttribute("speaker")
        number = self.dm.turns[n].getAttribute("number")
        color = self.dm.getSpeakerColor(speaker)        
        text = self.dm.GetTurnText(n)
        das = self.dm.turns[n].getElementsByTagName("dialogue_act")
        aligs = self.dm.turns[n].getElementsByTagName("alignment")
        turn = DialogueTurn(self.dm.turns[n])
        
        words = dict()
        signs = dict()
        for alig in aligs:
            indexes = (alig.getAttribute("order_text")).split(',') 

            words[int(indexes[0])] = "%s" % (alig.getAttribute("source_text"))
            signs[int(indexes[0])] = "%s" % (alig.getAttribute("trans_text"))
            for i in xrange(1,len(indexes)):
                words[int(indexes[i])] = ""
                signs[int(indexes[i])] = ""       

        s = ""
        word_index = 1
        for da in das:
            a1 = da.getAttribute("conversational_domain")
            a2 = da.getAttribute("speech_act")
            a3 = da.getAttribute("semantics")
            if len(a3) == 0:
                a3 = da.getAttribute("task_subtask")   
   
            (a1, a2, a3) = self.FillAs(a1, a2, a3)

            sem_text = xmlAllChildren(da)
            len_sem = len((sem_text.strip()).split(' '))
            
            change_color = 1    
            source_text = ""
            trans_text = ""
            if ((len(words) != 0) and (len(signs) != 0)):
                for i in xrange(word_index,word_index + len_sem):
                    word = words.get(i,"")
                    sign = signs.get(i,"")
                    if word != "":
                        if (change_color % 2) == 0:
                            source_text += "<font color=#cc3300><code><b>%s </b>" % (word)
                            trans_text += "<font color=#cc3300><code>%s " % (sign)
                        else:
                            source_text += "<font color=#000099><code><b>%s </b>" % (word)
                            trans_text += "<font color=#000099><code>%s " % (sign)
                    
                        change_color += 1

                        word_len = len(word)
                        sign_len = len(sign)
                        if word_len > sign_len:
                            trans_text += (word_len - sign_len) * "&nbsp;"
                        else:
                            source_text += (sign_len - word_len) * "&nbsp;"
                    
                    source_text += "</code></font>"
                    trans_text += "</code></font>"

                word_index += len_sem
            
            if source_text == "":
                s += "<br>* <b>%s</b>: no translation specified *" % speaker
            else:
                s += "<br>%s" % source_text
                s += "<br>%s" % trans_text

            s += "<br><b>%s</b>" % da.toxml()
            a = "<br><font color=%s><code>%-17s %-24s " % (color,a1,a2)
            a = a.replace(' ','&nbsp;')
            a = a.replace('t&nbsp;c', 't c')
            a += a3 + "</code></font>"
            s += a
        
        if (len(s) == 0):
            change_color = 1    
            source_text = ""
            trans_text = ""
            if ((len(words) != 0) & (len(signs) != 0)):
                for i in xrange(1,len(words) + 1):
                    word = words.get(i,"")
                    sign = signs.get(i,"")
                    if word != "":
                        if (change_color % 2) == 0:
                            source_text += "<font color=#cc3300><code><b>%s </b>" % (word)
                            trans_text += "<font color=#cc3300><code>%s " % (sign)
                        else:
                            source_text += "<font color=#000099><code><b>%s </b>" % (word)
                            trans_text += "<font color=#000099><code>%s " % (sign)
                    
                        change_color += 1

                        word_len = len(word)
                        sign_len = len(sign)
                        if word_len > sign_len:
                            trans_text += (word_len - sign_len) * "&nbsp;"
                        else:
                            source_text += (sign_len - word_len) * "&nbsp;"
                    
                        source_text += "</code></font>"
                        trans_text += "</code></font>"
            
            if source_text == "":
                s += "<b>%s</b>" % (turn.GetText().strip())
            else:
                s += "<br>%s" % source_text
                s += "<br>%s" % trans_text        
        else:
            if (s[0:4] == "<br>"):
                s = s[4:]
            
        return "<table cellspacing='0' cellpadding='0'><tr> \
            <td align='right' valign='top' width='30'> %(num)s:</td> \
            <td valign='top' width='75'><b><font color=%(col)s>%(spk)s</font>:</b></td> \
            <td>%(da)s</td></tr></table>" \
            % {'col':color, 'spk':speaker, \
            'num': number, \
            'da': s}                    

    def FillAs(self, a1, a2, a3):
        if len(a1) == 0:
            a1 = "---"
        if len(a2) == 0:
            a2 = "---"
        if len(a3) == 0:
            a3 = "---"
            
        return (a1, a2, a3)
