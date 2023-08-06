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

import wx.aui
from SCMPanel import SCMPanel
from generalPanel import GeneralPanel
from phase1Panel import Phase1Panel
from deformationPanel import DeformationPanel
from texturePanel import TexturePanel
from diffractionPanel import DiffractionPanel
from processPanel import ProcessPanel
from experimentPanel import ExperimentPanel


class MaterialsNotebook(wx.Panel, SCMPanel):

    """ panel with notebook for inputting materials information
    """

    def __init__(self, *args, **kwds):

        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.nb = wx.aui.AuiNotebook(self,style=wx.aui.AUI_NB_WINDOWLIST_BUTTON|wx.aui.AUI_NB_TAB_SPLIT|wx.aui.AUI_NB_SCROLL_BUTTONS)

        self.__do_layout()
        self.__custom_properties()


    def __do_layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)

    def __custom_properties(self):
        self.nb.SetMinSize((731, 576))
        self.nb.general = GeneralPanel(self.nb)
        self.nb.AddPage(self.nb.general, "General")
        self.nb.deformation = None
        self.nb.processes = []
        self.flagMaterial = False
        self.deleteFlag = False

    def setProperties(self):
        self.nb.general.controller = self.controller
        self.nb.general.treePanel = self.treePanel
        self.nb.general.kind = self.kind

    def createPages(self, type):
        if self.deleteFlag == True :
            self.nb.general = GeneralPanel(self.nb)
            self.nb.general.controller = self.controller
            self.nb.general.treePanel = self.treePanel
            self.nb.general.kind = self.kind
            self.nb.AddPage(self.nb.general, "General")
            self.deleteFlag = False
        if type=="Open" :
            if self.controller.epscData.phaseName == "1Phase" :
                self.nb.general.setProperties()
#            self.nb.phase1 = Phase1Panel(self.nb)
#            self.nb.AddPage(self.nb.phase1, "Material Parameters")
#            self.createRemainingPages()

    def createRemainingPages(self):
        self.nb.deformation = DeformationPanel(self.nb)
        self.nb.deformPage = self.nb.AddPage(self.nb.deformation, "Deformation")
        self.nb.texture = TexturePanel(self.nb)
        self.nb.texturePage = self.nb.AddPage(self.nb.texture, "Texture")
        self.nb.diff = DiffractionPanel(self.nb)
        self.nb.diffPage = self.nb.AddPage(self.nb.diff, "Diffraction")
        self.nb.processPage = []
        self.nb.processes = []
        for i in range(int(self.controller.epscData.generalData.numProcessFiles)):
            process = ProcessPanel(self.nb, processNum=i+1)
            self.nb.processes.append(process)
            self.nb.processPage.append(self.nb.AddPage(process, "Process"+ "_" + str(i+1)))
        self.processNum = int(self.controller.epscData.generalData.numProcessFiles)

        self.nb.exp = ExperimentPanel(self.nb)
        self.nb.expPage = self.nb.AddPage(self.nb.exp, "Experimental Data")

    def removePages(self):

        self.nb.DeletePage(0)
        self.nb.DeletePage(0)
        if self.nb.deformation :
            for i in range(4):
                self.nb.DeletePage(0)
            for i in range(int(self.controller.epscData.generalData.numProcessFiles)):
                self.nb.DeletePage(0)
        self.deleteFlag = True
        self.flagMaterial = False

    def showData(self):
        self.nb.general.showData()
        if self.flagMaterial :
            self.nb.phase1.showData()
            self.nb.deformation.showData()
            self.nb.texture.showData()
            self.nb.diff.showData()
            for i in range(int(self.controller.epscData.generalData.numProcessFiles)):
                self.nb.processes[i].showData()
            self.nb.exp.showData()

    def addMaterialPanel(self):
        if self.flagMaterial == False :
            self.nb.phase1 = Phase1Panel(self.nb)
            self.nb.AddPage(self.nb.phase1, "Material -" + self.kind)
            self.flagMaterial = True

        self.nb.SetSelection(1)

if __name__ == "__main__":
    from epscComp.epscData import EpscData
    class MyFrame(wx.Frame):
        def __init__(self, *args, **kwds):
            wx.Frame.__init__(self, *args, **kwds)
            self.window = MaterialsNotebook(self,type="Test")
            self.window.epscData = EpscData()
            self.test()
        def test(self):
#            self.window.showData()
            pass

    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = MyFrame(None, -1, 'dynamic test', size=(800,600))

    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
