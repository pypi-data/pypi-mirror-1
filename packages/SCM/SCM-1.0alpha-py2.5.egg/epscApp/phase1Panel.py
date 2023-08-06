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
import wx.grid
import os,string
import epscComp.config
from SCMPanel import SCMPanel
from deformationPanel import DeformationPanel
from texturePanel import TexturePanel
from diffractionPanel import DiffractionPanel
from processPanel import ProcessPanel
from experimentPanel import ExperimentPanel
from epscComp.matParameters import MatParameters

class Phase1Panel(wx.Panel, SCMPanel):

    """ panel to get material parameters.
            Crystal structure
            Elastic stiffness
            Thermal coefficients
    """

    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.controller = self.Parent.Parent.controller
        self.treePanel = self.Parent.Parent.treePanel
        self.kind = self.Parent.Parent.kind
        self.materialLabel = wx.StaticText(self, -1, "Name of Material:")
        self.materialText = wx.TextCtrl(self, -1, "", size=(200,-1))

        self.crystalLabel = wx.StaticText(self, -1, "Crystal Structure:")
        self.crystalRadio = wx.RadioBox(self, -1, "", wx.DefaultPosition, \
                                        wx.DefaultSize, self.crystalData(),)
        self.elasticLabel = wx.StaticText(self, -1, "Elastic Stiffness (Single Crystal, in GPa)")
        self.elasticGrid = wx.grid.Grid(self)
        self.elasticGrid.CreateGrid(6, 6)

        for i in range(6):
            self.elasticGrid.SetColLabelValue(i,"Ci" + str(i+1))
        for i in range(6):
            self.elasticGrid.SetRowLabelValue(i,"C" + str(i+1) + "j")

#        if self.kind == "2Phase2" :
##            self.crystalRadio.Enable(False)
#            self.elasticGrid.SetCellBackgroundColour(0,0,wx.CYAN)
#            self.elasticGrid.SetCellBackgroundColour(0,1,wx.CYAN)
#            for i in range(6):
#                for j in range(6):
#                    if not (i==0 and j==0 or i==0 and j==1):
#                        self.elasticGrid.SetReadOnly(i,j,True)
#                    self.elasticGrid.SetCellValue(i, j, self.elasticData()[i][j])
#        else :
        self.elasticGrid.SetCellBackgroundColour(0,0,wx.CYAN)
        self.elasticGrid.SetCellBackgroundColour(0,1,wx.CYAN)
        self.elasticGrid.SetCellBackgroundColour(3,3,wx.CYAN)


        self.thermalLabel = wx.StaticText(self, -1, "Thermal Expansion Coefficients :")
        self.thermalGrid = wx.grid.Grid(self)
        self.thermalGrid.CreateGrid(1, 6)
        self.thermalGrid.SetColLabelSize(0)
        self.thermalGrid.SetRowLabelSize(0)


        self.okBtn = wx.Button(self, -1, "OK")
        self.cancelBtn = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        self.Bind(wx.EVT_RADIOBOX, self.OnCrystal, self.crystalRadio)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnElasticChange, self.elasticGrid)
        self.__do_layout()
        self.__custom_properties()

    def __custom_properties(self):
        self.showFlag = False
        self.flagOK = 0

        self.materialText.SetValue(self.Parent.Parent.controller.epscData.matParam[self.kind].nameMaterial)
        self.crystalRadio.SetSelection(self.controller.epscData.matParam[self.kind].typeCrystal)

        for i in range(6):
            self.thermalGrid.SetCellValue(0, i, str(self.Parent.Parent.controller.epscData.matParam[self.kind].thermal[i]))
        for i in range(6):
            for j in range(6):
                if not (i==0 and j==0 or i==0 and j==1 or i==3 and j==3):
                    self.elasticGrid.SetReadOnly(i,j,True)
                self.elasticGrid.SetCellValue(i, j, str(self.Parent.Parent.controller.epscData.matParam[self.kind].elastic[i][j]))

    def OnCrystal(self, event):
#        print event.GetInt()
        if event.GetInt() == 2:
            self.elasticGrid.SetCellBackgroundColour(0,2,wx.CYAN)
            self.elasticGrid.SetCellBackgroundColour(2,2,wx.CYAN)
            self.elasticGrid.SetCellBackgroundColour(3,3,wx.CYAN)
            self.Refresh()
            for i in range(6):
                for j in range(6):
                    if not (i==0 and j==0 or i==0 and j==1 or i==3 and j==3):
                        self.elasticGrid.SetReadOnly(i,j,False)
#        elif event.GetInt() == 1:
#            self.elasticGrid.SetCellBackgroundColour(0,2,wx.WHITE)
#            self.elasticGrid.SetCellBackgroundColour(2,2,wx.WHITE)
#            self.elasticGrid.SetCellBackgroundColour(3,3,wx.WHITE)
#            self.Refresh()
        elif event.GetInt() <= 1 :
            self.elasticGrid.SetCellBackgroundColour(0,2,wx.WHITE)
            self.elasticGrid.SetCellBackgroundColour(2,2,wx.WHITE)
            self.Refresh()

    def showData(self):
        self.materialText.SetValue(self.controller.epscData.matParam[self.kind].nameMaterial)
        self.crystalRadio.SetSelection(self.controller.epscData.matParam[self.kind].typeCrystal)
        self.crystalRadio.Enable(False)
        for i in range(6):
            for j in range(6):
                self.elasticGrid.SetCellValue(i,j,str(self.controller.epscData.matParam[self.kind].elastic[i][j]))
        self.showFlag = True

    def filesData(self):
        return({"Phase1":"MATERIAL_1.sx","2Phase1":"MATERIAL_1.sx","2Phase2":"MATERIAL_2.sx"})

    def crystalData(self):
        return(["BCC","FCC","HCP"])


    def OnElasticChange(self,event):
#        if self.kind == "2Phase2" :
#        if self.crystalRadio.GetSelection()==1 :
#            self.elasticGrid.SetCellValue(1,1,self.elasticGrid.GetCellValue(0,0))
#            self.elasticGrid.SetCellValue(2,2,self.elasticGrid.GetCellValue(0,0))
#            self.elasticGrid.SetCellValue(0,2,self.elasticGrid.GetCellValue(0,1))
#            self.elasticGrid.SetCellValue(1,0,self.elasticGrid.GetCellValue(0,1))
#            self.elasticGrid.SetCellValue(1,2,self.elasticGrid.GetCellValue(0,1))
#            self.elasticGrid.SetCellValue(2,0,self.elasticGrid.GetCellValue(0,1))
#            self.elasticGrid.SetCellValue(2,1,self.elasticGrid.GetCellValue(0,1))
#            C44 = str(float(self.elasticGrid.GetCellValue(0,0))-float(self.elasticGrid.GetCellValue(0,1)))
#            self.elasticGrid.SetCellValue(3,3,C44)
#            self.elasticGrid.SetCellValue(4,4,C44)
#            self.elasticGrid.SetCellValue(5,5,C44)
        if self.crystalRadio.GetSelection()<= 1 :
            self.elasticGrid.SetCellValue(1,1,self.elasticGrid.GetCellValue(0,0))
            self.elasticGrid.SetCellValue(2,2,self.elasticGrid.GetCellValue(0,0))
            self.elasticGrid.SetCellValue(0,2,self.elasticGrid.GetCellValue(0,1))
            self.elasticGrid.SetCellValue(1,0,self.elasticGrid.GetCellValue(0,1))
            self.elasticGrid.SetCellValue(1,2,self.elasticGrid.GetCellValue(0,1))
            self.elasticGrid.SetCellValue(2,0,self.elasticGrid.GetCellValue(0,1))
            self.elasticGrid.SetCellValue(2,1,self.elasticGrid.GetCellValue(0,1))
            self.elasticGrid.SetCellValue(4,4,self.elasticGrid.GetCellValue(3,3))
            self.elasticGrid.SetCellValue(5,5,self.elasticGrid.GetCellValue(3,3))
        else :
            C66 = (float(self.elasticGrid.GetCellValue(0,0))-float(self.elasticGrid.GetCellValue(0,1)))/2
            self.elasticGrid.SetCellValue(1,1,self.elasticGrid.GetCellValue(0,0))
            self.elasticGrid.SetCellValue(1,0,self.elasticGrid.GetCellValue(0,1))
            self.elasticGrid.SetCellValue(1,2,self.elasticGrid.GetCellValue(0,2))
            self.elasticGrid.SetCellValue(2,0,self.elasticGrid.GetCellValue(0,2))
            self.elasticGrid.SetCellValue(2,1,self.elasticGrid.GetCellValue(0,2))
            self.elasticGrid.SetCellValue(4,4,self.elasticGrid.GetCellValue(3,3))
            self.elasticGrid.SetCellValue(5,5,str(C66))

    def setDefault(self):
        matParam = MatParameters()
        self.controller.epscData.matParam[self.kind].nameMaterial = ""
        self.controller.epscData.matParam[self.kind].typeCrystal = 0
        for i in range(6):
            for j in range(6):
                self.controller.epscData.matParam[self.kind].elastic[i][j] = 0
        for i in range(6):
            self.controller.epscData.matParam[self.kind].thermal[i] = 0.0


    def OnCancel(self, event):
        self.setDefault()
        self.__custom_properties()
        self.treePanel.turnOffNode(self.controller.epscData.phaseNum, 1)

    def OnOK(self,event):
        self.controller.epscData.matParam[self.kind].nameMaterial = self.materialText.GetValue()
        self.controller.epscData.matParam[self.kind].typeCrystal = self.crystalRadio.GetSelection()
        if self.crystalRadio.GetSelection() == 0 : # in case of BCC
            self.controller.epscData.matParam[self.kind].numModes = 4
        elif self.crystalRadio.GetSelection() == 1 : # in case of FCC
            self.controller.epscData.matParam[self.kind].numModes = 2
        else : #in case of HCP
            self.controller.epscData.matParam[self.kind].numModes = 8

        for i in range(6):
            for j in range(6):
                self.controller.epscData.matParam[self.kind].elastic[i][j] = float(self.elasticGrid.GetCellValue(i, j))

        for i in range(6):
            self.controller.epscData.matParam[self.kind].thermal[i] = self.thermalGrid.GetCellValue(0, i)


        if self.controller.epscData.phaseNum == 2032 :
            #print self.controller.epscData.phaseNum
            self.updatePhase("template_MATRIX.sx")
        else :
            self.updatePhase("template_" + self.crystalData()[self.controller.epscData.matParam[self.kind].typeCrystal] + ".sx")
#        print self.controller.epscData.matParam[self.kind]
        if (not self.controller.epscData.matParam[self.kind].saved and not self.showFlag) or self.controller.epscData.flagFromFile:
            self.Parent.Parent.createRemainingPages()

        self.flagOK = 1
        self.crystalRadio.Enable(False)
        self.treePanel.turnOnNode(self.controller.epscData.phaseNum, 1)
        self.controller.epscData.matParam[self.kind].saved = True
        self.controller.epscData.isAltered = True

        self.Parent.SetSelection(2)

    def __do_layout(self):
        topBSizer = wx.BoxSizer(wx.VERTICAL)

        dataFGSizer= wx.FlexGridSizer(cols=2 ,hgap=5, vgap=5)
        dataFGSizer.Add(self.materialLabel, 0, wx.ALL, 5)
        dataFGSizer.Add(self.materialText, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        dataFGSizer.Add(self.crystalLabel, 0, wx.ALL, 5)
        dataFGSizer.Add(self.crystalRadio, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)

        elasticFGSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        elasticFGSizer.Add(self.elasticLabel, 0, wx.ALL, 5)
        elasticFGSizer.Add(self.elasticGrid, 0, wx.ALL, 5)

        modeThermalFGSizer = wx.FlexGridSizer(cols=1, hgap=5, vgap=5)
        modeThermalFGSizer.Add(self.thermalLabel, 0, wx.ALL, 5)
        modeThermalFGSizer.Add(self.thermalGrid, 0, wx.ALL, 5)

        btnGSizer = wx.GridSizer(1, 2, 0, 0)
        btnGSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnGSizer.Add(self.cancelBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        topBSizer.Add(dataFGSizer, 0, wx.EXPAND, 0)
        topBSizer.Add(elasticFGSizer, 0, wx.EXPAND)

        topBSizer.Add(modeThermalFGSizer, 0, wx.EXPAND)
        topBSizer.Add(btnGSizer, 0, wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(topBSizer)


# update phase1 file
    def updatePhase(self,file):

        """ create/update matrix data file using template_MATERIAL.sx
        """
        strAll = ""

        fid = open(epscComp.config.dirEpscCore + file, "r")

# for "*Material "
        strAll = "*Material: " + self.controller.epscData.matParam[self.kind].nameMaterial + "\n"
        fid.readline()
# for "*Crystal "
        strAll = strAll + fid.readline()

        strAll = strAll + fid.readline()

# "*Elastic" + elastic stiffness data
        strAll = strAll + fid.readline()
        for i in range(6):
            for j in range(6):
                strAll = strAll + "%2.2f" % self.controller.epscData.matParam[self.kind].elastic[i][j] + "  "
                if j == 5 :
                    strAll = strAll + '\n'
                    fid.readline()

        strAll = strAll + fid.readline()
        strAll = strAll + fid.readline()
        strAll = strAll + fid.readline()
        strAll = strAll + fid.readline()
#"Thermal expansion.. "

        strAll = strAll + fid.readline()
        for i in range(6):
            strAll = strAll + str(self.controller.epscData.matParam[self.kind].thermal[i]) + "  "
        strAll = strAll + "\n"
        fid.readline()

        while 1:
            line = fid.readline()
            if not line :
                break
            strAll = strAll + line
        fid.close()

        fid = open(epscComp.config.dirEpscCore+ "template_MATERIAL.sx",'w')
        fid.write(strAll)
        fid.close

        print strAll


if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel=Phase1Panel(parent=frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()