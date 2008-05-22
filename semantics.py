# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details


import re
import sys

class Semantics:
    """  
    This class implements basic processing for abstract semantic annotation acording to Young.
    """
    
    def __init__(self, id, semantics, text):
        self.tokenizeText(text)
        self.id = id
        self.normalizeSemantics(semantics)
        self.createSemanticsTree()

    def __str__(self):
        return (self.semantics+":"+self.text)

    def tokenizeText(self, text):
        self.text = ""
        if not len(text) == 0:
            self.text = text.strip()
            self.text = re.sub(r' +', ' ', self.text)
            self.wordList = self.text.split(' ')
            
            wl = []
            for word in self.wordList:
                if not word[0] == "<":
                    wl.append(word)
                else:
                    print word
            
            self.wordList = wl
        else:
            self.text = ""
            self.wordList = []
            
    def normalizeSemantics(self, semantics):
        self.semantics = semantics.strip()
        self.semantics = re.sub(r' ?\( ', '(', self.semantics)
        self.semantics = re.sub(r' ?\) ', ')', self.semantics)
        self.semantics = re.sub(r' ?, ', ',', self.semantics)
        self.semantics = re.sub(r' +', ' ', self.semantics)
        
    def isEmpty(self):
        if len(self.semantics) == 0:
            return True
        
        return self.semantics.isspace()
        
    def isValid(self):
        return True

    def splitByComma(self, text):
        parentheses = 0
        splitList = []
        
        oldI=0
        for i in range(len(text)):
            if text[i] == '(':
                parentheses +=1
            elif text[i] == ')':
                parentheses -=1
                if parentheses < 0:
                    raise ValueError("Missing a left parenthesis.") 
            elif text[i] == ',':
                if parentheses == 0:
                    if oldI == i:
                        raise ValueError("Splited segment do not have to start with a comma.") 
                    else:
                        splitList.append(text[oldI:i].strip())
                        oldI = i+1
        else:
            splitList.append(text[oldI:].strip())
            
        return splitList

    def parseRoot(self, semantics):
##      print "R:"+smntcs
        smntcs = semantics.strip()
        
        try:
            l = smntcs.index('(')
        except ValueError:
            return [smntcs, []]
        
        try:
            r = smntcs.rindex(')')
        except ValueError:
            raise ValueError("Missing a right parenthesis.") 
            
        return [smntcs[:l], self.parseLeaves(smntcs[l+1:r])]
        
    def parseLeaves(self, semantics):
##      print "L:"+semantics
        smntcsList = self.splitByComma(semantics.strip())
      
        list = []
        for item in smntcsList:
            list.append(self.parseRoot(item))
        
        return list
        
    def createSemanticsTree(self):
        try:
            self.semanticsTree = self.parseLeaves(self.semantics)
        except ValueError:
            x = str(sys.exc_value) + " : " + self.semantics + " : " + self.text
            raise ValueError(x.encode("ascii", "backslashreplace"))
        
