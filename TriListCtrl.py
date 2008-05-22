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
import wx.lib.mixins.listctrl  as  listmix

import sys

class TriListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, id, triColumn, triDict = {}, 
        size = wx.DefaultSize, sizeC = (400, 150, 10)):
        wx.ListCtrl.__init__( self, parent, id, size = size, 
            style=wx.EXPAND
                |wx.LC_REPORT
                |wx.LC_VIRTUAL
                |wx.LC_HRULES
                |wx.LC_VRULES
                |wx.LC_SINGLE_SEL
                )
        self.currentItem = 0
        self.currentItemStr = ""

        #adding some art
        self.il = wx.ImageList(16, 16)
        a={"sm_up":"GO_UP","sm_dn":"GO_DOWN","w_idx":"WARNING","e_idx":"ERROR","i_idx":"QUESTION"}
        for k,v in a.items():
            s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
            exec(s)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #building the columns
        self.InsertColumn(0, triColumn[0])
        self.InsertColumn(1, triColumn[1])
        self.InsertColumn(2, triColumn[2])
        self.SetColumnWidth(0, sizeC[0])
        self.SetColumnWidth(1, sizeC[1])
        self.SetColumnWidth(2, sizeC[2])

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = triDict
        self.itemIndexMap = triDict.keys()
        self.SetItemCount(len(triDict))
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 3)

        #sort by genre (column 1), A->Z ascending order (1)
        self.SortListItems(0, 1)
        
        self.Select(self.currentItem)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        
    
    def __setitem__(self, key, value):
        self.itemDataMap[self.itemIndexMap[key]] = value
        
    def __getitem__(self, key):
        return self.itemDataMap[self.itemIndexMap[key]]
        
    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        self.StoreSelected()
        
    def InsertItem(self, value):
        self.itemDataMap[len(self.itemDataMap)] = value
        self.itemIndexMap = self.itemDataMap.keys()
        self.SetItemCount(len(self.itemDataMap))
    
    def DeleteAllItems(self):
        tri = {}
        self.itemDataMap = tri
        self.itemIndexMap = tri.keys()
        self.SetItemCount(len(tri))
        
    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index][col]
        return s

    def OnGetItemImage(self, item):
        return -1

    def OnGetItemAttr(self, item):
        return None

    #---------------------------------------------------
    # These methods are Used by the ColumnSorterMixin,
    # see wx/lib/mixins/listctrl.py

    def SortItems(self,sorter=None):
        r"""\brief a SortItem which works with virtual lists
        The sorter is not actually used (should it?)
        """

        #These are actually defined in ColumnSorterMixin
        #col is the column which was clicked on and
        #sf, the sort flag is False for descending (Z->A)
        #and True for ascending (A->Z).

        col=self._col
        sf=self._colSortFlag[col]

        #creating pairs [column item defined by col, key]
        items=[]
        for k,v in self.itemDataMap.items():
            items.append([v[col],k])
            
        #sort the pairs by value (first element), then by key (second element).
        #Multiple same values are okay, because the keys are unique.
        items.sort()
        
        #getting the keys associated with each sorted item in a list
        k=[key for value, key in items]

        #False is descending (starting from last)
        if sf==False:
            k.reverse()
            
        #storing the keys as self.itemIndexMap (is used in OnGetItemText,Image,ItemAttr).
        self.itemIndexMap=k

        # move the selected item
        self.RestoreSelected()

        #redrawing the list
        self.Refresh()

    def RestoreSelected(self,):
        for i in range(len(self.itemDataMap)):
            if self.currentItemStr == self.itemDataMap[self.itemIndexMap[i]][0]:
                self.Select(i)
                self.Focus(i)
                break

    def StoreSelected(self):
        if len(self.itemDataMap) > 0:
            self.currentItemStr = self.itemDataMap[self.itemIndexMap[self.currentItem]][0]
        else:
            self.currentItemStr = ""

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

#############################################################################
## test of virtual list
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
    musicdata = {
        1 : ("Bad English", "The Price Of Love", "Rock"),
        6 : ("Michael Bolton", "How Am I Supposed To Live Without You", "Blues"),
        7 : ("Paul Young", "Oh Girl", "Rock"),
        9 : ("Richard Marx", "Should've Known Better", "Rock"),
        10: ("Rod Stewart", "Forever Young", "Rock"),
        11: ("Roxette", "Dangerous", "Rock"),
        12: ("Sheena Easton", "The Lover In Me", "Rock"),
        13: ("Sinead O'Connor", "Nothing Compares 2 U", "Rock"),
        14: ("Stevie B.", "Because I Love You", "Rock"),
        15: ("Taylor Dayne", "Love Will Lead You Back", "Rock"),
        }

    triColumn = ["File name", "Processing state", "Description"]
        
    class TestFrame(wx.Frame):
        def __init__(self, parent, id, title, size, style = wx.DEFAULT_FRAME_STYLE ):
            wx.Frame.__init__(self, parent, id, title, size=size, style=style)
    
            self.CreateStatusBar(1)
    
            self.win = TriListCtrl(self, -1, triColumn, musicdata)

    app = wx.PySimpleApp()
    f = TestFrame(None, -1, "ColumnSorterMixin used with a Virtual ListCtrl",wx.Size(500,300))
    f.Center()
    f.Show()
    app.MainLoop()
