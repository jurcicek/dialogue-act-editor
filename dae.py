#!//usr/bin/python
# -*-  coding: UTF-8 -*-
#   
#   DAE (Dialogue Act Editor) is program for doing semantic and dialogue act annotation
#   for dialogs stored in XML format, compatible with DATE format.
#   
#   Copyright (c) 2005 by Filip Jurcicek and Jiri Zahradil, Department of Cybernetics,
#   University of West Bohemia, Czech Republic
#   
#   See LICENSE.TXT for license details


##################################################################################################
# WXVER = '2.6'
##################################################################################################

# Kvuli deploymentu pomoci PY2EXE je toto nutne zakomentovat.
# Po kompilaci do exe uz neni wxPython nainstalovan (ale tridy
# lze normalne pouzivat)

"""
import wxversion
if wxversion.checkInstalled(WXVER):
    wxversion.select(WXVER)
else:
    import sys, wx, webbrowser
    app = wx.PySimpleApp()
    wx.MessageBox("The requested version of wxPython is not installed.\n\n"
                  "Please install version %s" % WXVER,
                  "wxPython Version Error")
    app.MainLoop()
    webbrowser.open("http://wxPython.org/")
    sys.exit()
"""
    
import os.path
import wx, sys, optparse
import xml.dom.minidom

from edit import *
from editor_model import *

class DAEApp(wx.App):
    def OnInit(self):
    
        program_dir = os.path.dirname(sys.argv[0])

        print program_dir       
    
        #find config
        config_filename = 'settings.xml'
        if not os.path.exists(config_filename):
            config_filename = os.path.normpath(program_dir + "/settings.xml")
        
        #parse options          
    
        usage = "usage: %prog [options] [dialog filename to open]"
        parser = optparse.OptionParser(usage=usage)
        parser.add_option("-c", "--cfg", dest="config", help="specify configuration filename with path", metavar="FILE")
        (options, args) = parser.parse_args()
        if len(args) == 0:
            filename = ""
        else:
            filename = args[0]
    
        if options.config != None:
            config_filename = options.config
            
        #load config        
        try:      
            print "Loading config file: %s" % (config_filename)
            dm = DataModel(config_filename)
        except:
            wx.MessageBox("There is an error in parsing of the setting.xml file.\n\n"
                          "Please, update your settings.",
                          "DAE Error")
            return False
           
        if os.path.exists(filename):
            # soubor existuje
            print "Setting data dir: "+os.path.dirname(filename)
            print "Opening file: "+os.path.basename(filename)
            dm.SetDataDir(os.path.dirname(filename))
            frame = DEAFrame(None, -1, "Dialogue Act Editor", dm, filename)
        else:
            frame = DEAFrame(None, -1, "Dialogue Act Editor", dm)
            
        frame.Center()
        frame.Maximize()
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = DAEApp(0)    # Create an instance of the application class
app.MainLoop()     # Tell it to start processing events
