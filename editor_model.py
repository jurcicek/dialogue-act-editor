# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details

import xml.dom.minidom, shutil
import re, sys, time, codecs, os.path

def htmlEnt(str):
    str = str.replace("<","&lt;");
    str = str.replace(">","&gt;");
    return str

def xmlAllChildren(node):
    s = ""
    for ch in node.childNodes:              
        s += ch.toxml()     
    return s

def removeNode(node):
    node.parentNode.removeChild(node)

def myPrettyXml(node, coding = "UTF-8"):     
    out = node.toprettyxml("  ")    
    out = out.replace('?>', ' encoding="%s" ?>' % coding)
    out = re.sub("\r\n","\n",out)
    out = re.sub("\r","",out)
    out = re.sub("\n\s*\n","\n",out)

    if coding == "unicode":
        return out
    else:
        return out.encode(coding)

class DialogueTurn:
    def __init__(self, xmlelement):
        self.xml = xmlelement 

    def GetXMLDOMTurn(self):
        return self.xml

    def SetTranslation(self, source, signed):
        # vyhodit nejprve staré <text ... >        
        s1 = None
        #s2 = None
        parent = self.xml.getElementsByTagName("utterance")[0]
        for node in self.xml.getElementsByTagName("translation"):
            if node.getAttribute("type") == "signed":
                s1 = node
            #if node.getAttribute("type") == "sign":
            #    s2 = node
        if s1:
            parent.removeChild(s1)
        #if s2:
        #    parent.removeChild(s2)

        # přidat nové
        
        if len(signed) > 0:
            words = source.split(' ')
            s1 = xml.dom.minidom.Element("translation")
            s1.setAttribute("type", "signed")
            
            '''if len(s1.getElementsByTagName("dialogue_act")) == 0:
                das = parent.getElementsByTagName("dialogue_act")
                if len(das) != 0:
                    for da in das:
                        s1.appendChild(da)'''

            tokens = signed.split(' ')
            i = 1
     
            for token in tokens:
                w = xml.dom.minidom.Element("alignment")
                word_alig = token.split('/')
                source_text = ""
                
                for alig in word_alig[1].split(','):
                    source_text += words[int(alig) - 1] + " "
                source_text = source_text.strip()
                
                alignments = s1.getElementsByTagName("alignment")
                alig_exists = False
                for alignment in alignments:
                    if alignment.getAttribute("order_text") == word_alig[1]:
                        alignment.setAttribute("trans_text",alignment.getAttribute("trans_text") + " " + word_alig[0])
                        alignment.setAttribute("order_trans_text",alignment.getAttribute("order_trans_text") + "," + "%d" % (i))
                        alig_exists = True
                
                if not alig_exists:
                    w.setAttribute("source_text", source_text)
                    w.setAttribute("trans_text", word_alig[0])
                    w.setAttribute("order_text", word_alig[1])
                    w.setAttribute("order_trans_text", "%d" % (i))
                    s1.appendChild(w)
                
                i += 1
            
            parent.appendChild(s1)
        
        #s2 = xml.dom.minidom.Element("text")
        #s2.setAttribute("type", "sign")        
        #node = xml.dom.minidom.Text()        
        #node.data = sign
        #s2.appendChild(node)     
        #parent.appendChild(s2)

        # hotovo
    
    def GetSpeaker(self):
        return self.xml.getAttribute("speaker")
        
    def GetText(self):
        notFound = True
        for node in self.xml.getElementsByTagName("text"):
            if node.getAttribute("type") == "normalized":
                notFound = False                
                break
        if notFound:
            text = ""
        else:
            text = xmlAllChildren(node)
            text = text.replace("<","[")
            text = text.replace(">","]")
        return text

    def GetSigned(self):
        Text = ""
        
        if self.xml.getElementsByTagName("translation"):
            Translation = self.xml.getElementsByTagName("translation")[0]
        
            for Node in Translation.getElementsByTagName("alignment"):
                Trans_text = Node.getAttribute("trans_text").split(' ')
                Alignment =  Node.getAttribute("order_text")    
                for Trans in Trans_text:
                    Text += Trans + '/' + Alignment + " "
            
        return Text.strip()     

    def GetSign(self):
        notFound = True
        for node in self.xml.getElementsByTagName("text"):
            if node.getAttribute("type") == "sign":
                notFound = False                
                break
        if notFound:
            text = ""
        else:
            text = xmlAllChildren(node)
            text = text.replace("<","[")
            text = text.replace(">","]")
            
        return text     


class DialogueAct:
    def __init__(self):
        self.domain = ""
        self.speechAct = ""
        self.semantics = ""
        self.text = ""
        self.normalize()
        
    def create(self, dom_da):
        # vstup je dialogový akt - DOM element!
        dom_da.normalize()
        self.domain = dom_da.getAttribute("conversational_domain")
        self.speechAct = dom_da.getAttribute("speech_act")
        a3 = dom_da.getAttribute("semantics")
        if len(a3)==0:
            a3 = dom_da.getAttribute("task_subtask")
        self.semantics = a3
        self.text = xmlAllChildren(dom_da)       
        self.normalize()
        
    def normalize(self):
        self.domain = self.domain.strip()
        self.speechAct = self.speechAct.strip()
        self.semantics = self.semantics.strip()
        self.text = self.text.strip()
        self.text = re.sub("[\r\n]+"," ", self.text)
        
    def get_html(self):
        s = "(%s,%s,%s)<br><b>%s</b><br>" % (htmlEnt(self.domain),htmlEnt(self.speechAct),self.semantics,self.text)
        s = "<b>%s</b><br>(%s,%s,%s)<br>" % (self.text, htmlEnt(self.domain),htmlEnt(self.speechAct), self.semantics)
        return s
        
    def get_xmldom(self):
        e = xml.dom.minidom.Element("dialogue_act")
        e.setAttribute("conversational_domain", self.domain)
        e.setAttribute("speech_act",self.speechAct)
        e.setAttribute("semantics",self.semantics)
        node = xml.dom.minidom.Text()
        text = self.text.replace("<","[")
        text = text.replace(">","]")
        node.data = text
        e.appendChild(node)     
        return e
        
    def toString(self):
        return "[DA(%s,%s,%s): %s]" % (self.domain,self.speechAct,self.semantics,self.text)
        
        
class DataModel:
    def __init__(self, config_filename):
        self.colors = ["#B00000","#0000B0","#00B000","#FF0000","#FF00FF","#00FFFF"]
        self.speakers = dict()
        self.modified = False
        self.dom = None
        self.config_filename = config_filename
                
        dom = xml.dom.minidom.parse(config_filename)
        # v dom máme načtený config.xml
        self.anotatorid = xmlAllChildren(dom.getElementsByTagName("annotator")[0])        
        self.datadir =  xmlAllChildren(dom.getElementsByTagName("datadir")[0])
        self.editor_mode =  xmlAllChildren(dom.getElementsByTagName("mode")[0])
        
        trn = dom.getElementsByTagName("translation")[0]
        self.vocabfile = xmlAllChildren(trn.getElementsByTagName("vocabfile")[0])        
        self.editorcmd = xmlAllChildren(trn.getElementsByTagName("editor_command")[0])        
        self.LoadTranslationVocab(self.vocabfile)
        
        section = dom.getElementsByTagName("domain")[0]
        tags = section.getElementsByTagName("tag")
        self.domainTags = list()
        for tag in tags:
            tag.normalize()
            self.domainTags.append(tag.firstChild.data.strip())
        
        section = dom.getElementsByTagName("speech-act")[0]
        tags = section.getElementsByTagName("tag")
        self.speechActTags = list()
        for tag in tags:
            tag.normalize()
            self.speechActTags.append(tag.firstChild.data.strip())
        self.configdom = dom
    
        section = dom.getElementsByTagName("processing-state")[0]
        tags = section.getElementsByTagName("tag")
        self.processingStateTags = list()
        for tag in tags:
            tag.normalize()
            self.processingStateTags.append(tag.firstChild.data.strip())
        
        section = dom.getElementsByTagName("concept")[0]
        tags = section.getElementsByTagName("tag")
        self.conceptTags = list()
        for tag in tags:
            tag.normalize()
            self.conceptTags.append(tag.firstChild.data.strip())

    def SetDataDir(self,dirn):
        self.datadir = dirn
        
    def GetConfigDir(self):
        config_dir = os.path.dirname(config_filename)
        if config_dir:
            return "./"
        else:
            return p+"/"
    
    def SaveToConfig(self):
        # config je v self.dom
        # vratit annotator + datadir
        e = self.configdom.getElementsByTagName("annotator")[0]
        for ch in e.childNodes:
            e.removeChild(ch)
            ch.unlink()
        node = xml.dom.minidom.Text()        
        node.data = self.anotatorid
        e.appendChild(node)
        e = self.configdom.getElementsByTagName("datadir")[0]
        for ch in e.childNodes:
            e.removeChild(ch)
            ch.unlink()
        node = xml.dom.minidom.Text()        
        node.data = self.datadir
        e.appendChild(node)
        
        shutil.copyfile(self.config_filename, self.config_filename+".bak")
        fp = open(self.config_filename,"w")
        fp.write(self.configdom.toxml().encode("utf-8"))
        fp.close()
    
    def getSpeakerColor(self, spk):
        if not self.speakers.has_key(spk):
            color_index = len(self.speakers)
            if (color_index>=len(self.colors)):
                self.speakers[spk] = "#000"
            else:
                self.speakers[spk] = self.colors[color_index]                
        return self.speakers[spk]

    def GetModified(self):
        return self.modified
    
    def SetModified(self):
        self.modified = True
    
    def RetrieveDA(self,turn_no):
        da_dom_list = self.turns[turn_no].getElementsByTagName("dialogue_act")
        da_class_list = list()
        for da_elem in da_dom_list:
            da = DialogueAct()
            da.create(da_elem)
            da_class_list.append(da)
        # a je to, máme to v da_class_list
        return da_class_list
        
    def RetrieveDA_DOM(self,turn_no):
        return self.turns[turn_no].getElementsByTagName("dialogue_act")        
    
    def StoreDA(self, turn_no, da_list):
        self.SetModified()
        # vyhodit všechny akty z XML
        # pozor v <turn> je také <utterance>!!
        da_dom_list = self.turns[turn_no].getElementsByTagName("dialogue_act")     
        # odstraní <dialogue_act> z <utterance>
        parent = self.turns[turn_no].getElementsByTagName("utterance")[0]
        for da_elem in da_dom_list:
            parent.removeChild(da_elem)
            
        # přidá do <utterance> nové <dialogue_act>
        for da in da_list:          
            newchild = da.get_xmldom()
            parent.appendChild(newchild)
            
        self.LoadCache()
    
    def GetTurnNum(self):
        return len(self.turns)
    
    def getDescription(self):
        return self.description
    
    def setDescription(self, description):
        self.description = description
    
    def getProcessingState(self):
        return self.processingState

    def setProcessingState(self, processingState):
        self.processingState = processingState
        
    def ImplicitState5(self):
        flag = False
        for t in self.turns:
          spk = t.getAttribute("speaker")
          das = t.getElementsByTagName("dialogue_act")
          for da in das:
            # test for state5 attribute
            s5 = da.getAttribute("state5")            
            if spk == "operator":
              if s5:
                flag = True
                da.removeAttribute("state5")
            else:              
              if not s5:
                flag = True
                da.setAttribute("state5", "3")
        if flag:
          self.SetModified()
          

    def LoadCache(self):
        items = list()
        for t in self.dom.getElementsByTagName("turn"):
            items.append(t)     
        self.turns = items
    
    def Load(self, filename):
        self.filename = filename
        try:
            dom = xml.dom.minidom.parse(self.filename)       
        except xml.parsers.expat.ExpatError:
            sys.excepthook(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
            return False
          
        if (self.dom):
            self.dom.unlink()
        self.dom = dom     
        self.LoadCache()
        # nový seznam řečníků
        self.speakers = dict()
        self.modified = False
    
        elem = self.dom.getElementsByTagName("task")[0] #root element
        try:
            self.description = elem.getAttribute("description")
        except:
            self.description = ""
            
        try:
            self.processingState = elem.getAttribute("processing-state")
        except:
            self.processingState = ""
            
        if self.processingState == "":
            try:
                self.processingState = elem.getAttribute("processig-state")
                elem.removeAttribute("processig-state")
            except:
                self.processingState = ""
            
            if self.processingState == "":
                self.processingState = "unannotated"
            
        # název dialogu:
        try:
            self.dialog_id = elem.getAttribute("dialog")
        except:
            self.dialog_id = os.path.basename(self.filename)
            
        return True
    
    def Save(self):
        print "Saving to file %s" % (self.filename)
        f = open(self.filename, "w")
        f.write("\xEF\xBB\xBF") 
        elem = self.dom.getElementsByTagName("task")[0] #root element
        elem.setAttribute("saved-by","Dialog Act Editor 1.5")
        elem.setAttribute("last-change",time.ctime())
        elem.setAttribute("modified-by",self.anotatorid)       
        elem.setAttribute("description", self.description)
        elem.setAttribute("processing-state", self.processingState)
        f.write(self.GetUTF8SourceXML())    
        f.close
        self.modified = False
    
    def GetOriginalXML(self):
        f = open(self.filename, "r")
        out = f.read()
        f.close()
        return out
    
    def GetSourceXML(self):
        return self.dom.toxml()
    
    def GetUTF8SourceXML(self):
        return myPrettyXml(self.dom)
    
    def GetTurnText(self, num):
        text = self.turns[num].getElementsByTagName("ne_typed_text")
        if len(text) == 0:
            # nenalezeno
            text = self.turns[num].getElementsByTagName("text")
            if len(text) == 0:
                return ""
        #v text je pole
        text = text[len(text)-1]
        text = xmlAllChildren(text)
        text = text.strip()
        text = text.replace("<","[")
        text = text.replace(">","]")
        return text
    
    def ReplaceTurn(self, num, new_turn):          
        parent = self.turns[num].parentNode
        parent.replaceChild(new_turn, self.turns[num])     
        self.SetModified()

    
    def LoadTranslationVocab(self, filename = None):
        if filename == None:
            filename = self.vocabfile
        self.translation_vocab = dict()
        
        if os.path.exists(filename):
            for line in codecs.open(filename,"r", "cp1250"):
                if len(line) > 0:
                    line = line.strip()
                    words = line.split(' ')
                    self.translation_vocab[words[0]] = 1    
        else:
            print "File " + filename + " does not exist!"
