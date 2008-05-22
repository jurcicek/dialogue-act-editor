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

class dialogue:
    pass

def load_comm(filename):
    dom = xml.dom.minidom.parse(filename)    

def start_print(name, attrs):
    o = "<"+name
    for a in attrs:
        o += " %s=\"%s\"" % (a,attrs[a])
    o = o+">"
    return o

def end_print(name):
    return "</%s>" % name

class dapart:
    # 3 handler functions
    def __init__(self):
        self.out = ""
        self.saved = 0
        
    def start_element(self, name, attrs):
        if (name == "task"):
            self.out = start_print(name,attrs)
            self.filename = "%s-%s%s%s-%s" % (attrs["system"],
                                              attrs["year"],
                                              attrs["month"],
                                              attrs["day"],
                                              attrs["pin"])
        else:
            self.out += start_print(name,attrs)           
        
    def end_element(self, name):
        self.out += end_print(name)
        if (name == "task"):
            #uložit out
            self.saved += 1
            print "%d. %s" % (self.saved,self.filename)
            fp = open("data/"+self.filename,"w")
            fp.write(self.out)
            fp.close()
            # raise xml.parsers.expat.ExpatError()
        
    def char_data(self, data):
        self.out += data

d = dapart()

p = xml.parsers.expat.ParserCreate()
p.StartElementHandler = d.start_element
p.EndElementHandler = d.end_element
p.CharacterDataHandler = d.char_data
filename = "X:/Data/2000_comm_dialog_act/data/da_tagged_communicator_2000.xml"
fp = open(filename,"r")
p.ParseFile(fp)


