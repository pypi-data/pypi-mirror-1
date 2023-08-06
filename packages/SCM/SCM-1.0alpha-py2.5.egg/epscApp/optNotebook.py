#! /usr/bin/env python
#
###############################################################################
#                            Iowa State University
#                        Ersan Ustundag Research Group
#                 DANSE Project Engineering Diffraction Subgroup
#                    Copyright (c) 2007 All rights reserved.
#                      Coded by: Seung-Yub Lee, Youngshin Kim
###############################################################################
#

import wx
from SCMPanel import SCMPanel
from optAlgorithmPanel import OptAlgorithm
from optBCCDataPanel import OptBCCDataPanel
from optFCCDataPanel import OptFCCDataPanel
from optHCPDataPanel import OptHCPDataPanel

class OptNotebook(wx.Panel, SCMPanel):
    """ panel with the notebook having algorithm and optimization data panes
    """
    def __init__(self, *args, **kwds):

        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.deleteFlag = False
        self.nb = wx.aui.AuiNotebook(self,style=wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_SCROLL_BUTTONS)
        self.nb.optAlgorithm = OptAlgorithm(self.nb)
        self.nb.AddPage(self.nb.optAlgorithm, "Algorithm")
        self.nb.optBCC = OptBCCDataPanel(self.nb)
        self.nb.AddPage(self.nb.optBCC, "Parameters - Phase1")

        self.nb.optFCC = OptFCCDataPanel(self.nb)
        self.nb.AddPage(self.nb.optFCC, "Parameters - Phase1")
        self.nb.optHCP = OptHCPDataPanel(self.nb)
        self.nb.AddPage(self.nb.optHCP, "Parameters - Phase1")

        self.setProperties()
        self.__do_layout()

    def setProperties(self):
        self.nb.optAlgorithm.controller = self.controller
        self.nb.optBCC.controller = self.controller
        self.nb.optFCC.controller = self.controller
        self.nb.optHCP.controller = self.controller
        self.nb.optAlgorithm.treePanel = self.treePanel
        self.nb.optBCC.treePanel = self.treePanel
        self.nb.optFCC.treePanel = self.treePanel
        self.nb.optHCP.treePanel = self.treePanel

    def createPages(self, type="default"):
        if self.deleteFlag:
            self.nb.optAlgorithm = OptAlgorithm(self.nb)
            self.nb.AddPage(self.nb.optAlgorithm, "Algorithm")
            self.nb.optAlgorithm.controller = self.controller
            self.nb.optAlgorithm.treePanel = self.treePanel

            self.nb.optBCC = OptBCCDataPanel(self.nb)
            self.nb.AddPage(self.nb.optBCC, "Parameters - Phase1")
            self.nb.optBCC.controller = self.controller
            self.nb.optBCC.treePanel = self.treePanel

            self.nb.optFCC = OptFCCDataPanel(self.nb)
            self.nb.optFCC.controller = self.controller
            self.nb.optFCC.treePanel = self.treePanel
            self.nb.AddPage(self.nb.optFCC, "Parameters - Phase1")

            self.nb.optHCP = OptHCPDataPanel(self.nb)
            self.nb.optHCP.controller = self.controller
            self.nb.optHCP.treePanel = self.treePanel
            self.nb.AddPage(self.nb.optHCP, "Parameters - Phase1")

    def removePages(self):
        self.nb.DeletePage(0)
        self.nb.DeletePage(0)
        self.deleteFlag = True

    def showPanels(self):
        if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
            self.nb.DeletePage(3)
            self.nb.DeletePage(2)
        elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
            self.nb.DeletePage(3)
            self.nb.DeletePage(1)
        elif self.controller.epscData.matParam["Phase1"].typeCrystal == 2 :
            self.nb.DeletePage(2)
            self.nb.DeletePage(1)

    def showVoce(self):
        if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
            self.nb.optBCC.showData()
        elif self.controller.epscData.matParam["Phase1"].typeCrystal== 1 :
            self.nb.optFCC.showData()
        elif self.controller.epscData.matParam["Phase1"].typeCrystal== 2 :
            self.nb.optHCP.showData()

    def updateParams(self,listParams):
        if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
            self.nb.optBCC.refreshOptimizedVoce(listParams)
        elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
            self.nb.optFCC.refreshOptimizedVoce(listParams)
        elif self.controller.epscData.matParam["Phase1"].typeCrystal == 2 :
            self.nb.optHCP.refreshOptimizedVoce(listParams)

    def __do_layout(self):
        # begin wxGlade: OptNotebook.__do_layout
        sizer_optNote = wx.BoxSizer(wx.HORIZONTAL)

        sizer_optNote.Add(self.nb, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_optNote)
        #sizer_optNote.Fit(self)
        sizer_optNote.SetSizeHints(self)
        # end wxGlade

# end of class OptNotebook


if __name__ == "__main__":
    from epscComp.epscData import EpscData
    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            wx.Frame.__init__(self, *args, **kwds)
            self.window = OptNotebook
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'OPT Panel')
    panel=OptNotebook(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
