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
import os
import epscComp.config
from SCMPanel import SCMPanel
from epscComp.diffractionData import DiffractionData

class DiffractionPanel(wx.Panel, SCMPanel):

    """ DiffractionPanel is the panel which gets diffraction information.
    """

    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.controller = self.Parent.Parent.controller
        self.treePanel = self.Parent.Parent.treePanel
        self.kind = self.Parent.Parent.kind
        self.planeType = []
        self.chi = []
        self.eta = []
        self.angle = []

        if self.controller.epscData.phaseNum == 201 or self.controller.epscData.phaseNum == 2021 or self.controller.epscData.phaseNum == 2031 :
            self.phase = "Phase1"
        else :
            self.phase = "Phase2"

        self.getDefault(self.controller.epscData.matParam[self.kind].typeCrystal)
        self.sbox_hkl = wx.StaticBox(self, -1, "Add your diffraction data.")
        self.sbox_selected = wx.StaticBox(self, -1, "Remove from the default.")

        self.hklGrid = wx.grid.Grid(self)
        self.hklGrid.CreateGrid(1, 5)
        for i in range(5):
            self.hklGrid.SetColSize(i,50)
            self.hklGrid.SetColLabelValue(i,self.labelData()[i])
        self.hklGrid.SetRowLabelSize(0)
        self.hklGrid.SetColLabelSize(20)
        self.button_Add = wx.Button(self, -1, "Add")

        self.listbox_selected = wx.ListBox(self, 70, (350, 50), (250, 270), self.listDefault, wx.LB_SINGLE)
        self.button_Remove = wx.Button(self, -1, "Remove")

        img = wx.Image(epscComp.config.dirImages + "chi_eta.png", wx.BITMAP_TYPE_ANY)
        img = img.Scale(img.GetWidth()*3/5, img.GetHeight()*3/5)
        self.sb = wx.StaticBitmap(self, -1, wx.BitmapFromImage(img))
        self.button_MoveUp = wx.Button(self, -1, "Move Up")
        self.button_MoveDown = wx.Button(self, -1, "Move Down")

        self.okBtn = wx.Button(self, -1, "OK")
        self.cancelBtn = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.button_Add)
        self.Bind(wx.EVT_BUTTON, self.OnMoveUp, self.button_MoveUp)
        self.Bind(wx.EVT_BUTTON, self.OnMoveDown, self.button_MoveDown)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.button_Remove)
        self.__do_layout()

    def dataPhaseNum(self):
        return({"Phase1":"1","2Phase1":"1", "2Phase2":"2"})

    def labelData(self):
        return(["h","k","l",u"\u03C7" + "(chi)",u"\u03B7"+"(eta)"])

    def getDefault(self, crystalType):

        fid = open(epscComp.config.dirEpscCore + epscComp.config.file_Diffraction[crystalType], "r")

        listDefault = []
        listDefault = fid.readlines()
        self.top_text = listDefault[:5]
        fid.close()
        self.listDefault = listDefault[5:]
#        self.controller.epscData.numDiffractionData[self.kind] = len(self.listDefault)

    def separateData(self):
        self.numLong = 0
        self.numTrans = 0
        self.numRolling = 0
        self.chi = []
        self.eta = []
        for i in range(self.controller.epscData.numDiffractionData[self.phase]) :
            a = self.listDefault[i].split()
#            if self.controller.epscData.matParam.getData("")
            if self.controller.epscData.phaseNum == 201 :
                strPhase = ""
            elif self.controller.epscData.phaseNum == 2021 or self.controller.epscData.phaseNum == 2022 :
                strPhase = "2"
            else :
                strPhase = "3"

            if self.controller.epscData.matParam[self.kind].typeCrystal == 2 :
                # ex. if "crystalPhase1" is HCP
                b = a[:4]
                self.chi.append(a[4])
                self.eta.append(a[5])
            else :
                b = a[:3]
                self.chi.append(a[3])
                self.eta.append(a[4])
            self.planeType.append(''.join(b))

            if float(self.chi[i]) == 0 and float(self.eta[i]) == 0 :
                self.angle.append("Long")
                self.numLong +=1
            elif float(self.chi[i]) == 90 and float(self.eta[i]) == 90:
                self.angle.append("Rolling")
                self.numRolling +=1
            elif float(self.chi[i]) == 90 and float(self.eta[i]) == 0:
                self.angle.append("Trans")
                self.numTrans +=1

#            print self.planeType[i]
#            print self.chi[i]
#            print self.eta[i]

    def showData(self):
        pass

    def OnOK(self,event):

        self.controller.epscData.numDiffractionData[self.phase] = len(self.listDefault)
        self.listDefault = []
        for i in range(self.controller.epscData.numDiffractionData[self.phase]):
            self.listbox_selected.Select(i)
            self.listDefault.append(self.listbox_selected.GetStringSelection())

        strTop = (''.join(self.top_text)).replace("$Num_Diffraction", str(self.controller.epscData.numDiffractionData[self.phase]))
        fid = open(epscComp.config.dirEpscCore + "DIFFRACTION_" + self.dataPhaseNum()[self.kind] + ".dif", "w")
        fid.write(strTop)
        fid.write(''.join(self.listDefault))
        fid.close()

#        print numData

        self.separateData()
        self.controller.epscData.numDiffractionData["Trans" + self.phase] = self.numTrans
        self.controller.epscData.numDiffractionData["Long" + self.phase] = self.numLong
        self.controller.epscData.numDiffractionData["Rolling" + self.phase] = self.numRolling
#        print self.controller.epscData.numDiffractionData["Long" + self.phase]
        self.controller.epscData.listDiffractionData[self.phase] = []
        for i in range(self.controller.epscData.numDiffractionData[self.phase]) :
            diffData = DiffractionData(self.planeType[i],self.chi[i],self.eta[i],self.angle[i])
            self.controller.epscData.listDiffractionData[self.phase].append(diffData)
            if self.angle[i] == "Trans" :
                self.controller.epscData.listDiffractionData["Trans" + self.phase].append(diffData)
            elif self.angle[i] == "Long" :
                self.controller.epscData.listDiffractionData["Long" + self.phase].append(diffData)
            elif self.angle[i] == "Rolling" :
                self.controller.epscData.listDiffractionData["Rolling" + self.phase].append(diffData)

        self.controller.epscData.diffractionDataSaved = True
        self.Parent.SetSelection(5)

        self.treePanel.turnOnNode(self.controller.epscData.phaseNum, 4)

    def OnCancel(self, event):
        self.getDefault(self.controller.epscData.matParam[self.kind].typeCrystal)
        self.listbox_selected.Set(self.listDefault)
        self.treePanel.turnOffNode(self.controller.epscData.phaseNum, 4)
        self.controller.epscData.diffractionDataSaved = False

    def OnAdd(self, event):

        str = " "
        for i in range(5):
            if i==3:
                str = str + "         " + self.hklGrid.GetCellValue(0,i)
            elif i ==4 :
                str = str + "       " + self.hklGrid.GetCellValue(0,i)
            else:
                str = str + "  " + self.hklGrid.GetCellValue(0,i)

        str += "    \n"
        self.listDefault.append(str)
        self.listbox_selected.Append(str)
        self.controller.epscData.matParam[self.kind].numDiffraction = len(self.listDefault)

    def OnMoveUp(self, event):
        """ When clicked, move the selected diffraction to one position up
        """
        if self.listbox_selected.GetSelection() != wx.NOT_FOUND :
            self.currentItemIndex = self.listbox_selected.GetSelection()
            self.currentItem = self.listbox_selected.GetStringSelection()
            if self.currentItemIndex > 0 :
                self.listbox_selected.Insert(self.currentItem, self.currentItemIndex-1)
                self.listbox_selected.Delete(self.currentItemIndex+1)
                self.listbox_selected.SetSelection(self.currentItemIndex-1)

    def OnMoveDown(self, event):
        """ When clicked, move the selected diffraction one position down
        """
        if self.listbox_selected.GetSelection() != wx.NOT_FOUND :
            self.currentItemIndex = self.listbox_selected.GetSelection()
            self.currentItem = self.listbox_selected.GetStringSelection()
            if self.currentItemIndex < self.listbox_selected.GetCount()-1 :
                self.listbox_selected.Delete(self.currentItemIndex)
                self.listbox_selected.Insert(self.currentItem, self.currentItemIndex+1)
                self.listbox_selected.SetSelection(self.currentItemIndex+1)

    def OnRemove(self, event):
        if self.listbox_selected.GetSelection()!= wx.NOT_FOUND :
            index = self.listbox_selected.GetSelection()
            del self.listDefault[self.listbox_selected.GetSelection()]
            self.listbox_selected.Delete(self.listbox_selected.GetSelection())
            self.controller.epscData.matParam[self.kind].numDiffraction =len(self.listDefault)
            if index <= len(self.listDefault)-1 :
                self.listbox_selected.SetSelection(index)

    def __do_layout(self):
        mainBSizer = wx.BoxSizer(wx.VERTICAL)
        topBSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnBSizer = wx.BoxSizer(wx.VERTICAL)


        sizer_sbox_hkl = wx.StaticBoxSizer(self.sbox_hkl,wx.VERTICAL)
        sizer_sbox_selected = wx.StaticBoxSizer(self.sbox_selected,wx.VERTICAL)

        sizer_sbox_hkl.Add(self.hklGrid, 0, wx.ALL, 5)
        sizer_sbox_hkl.Add(self.button_Add, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_sbox_hkl.Add(self.sb)

        btn2BSizer = wx.BoxSizer(wx.HORIZONTAL)
        btn2BSizer.Add(self.button_MoveUp, 0, wx.EXPAND, 0)
        btn2BSizer.Add((20,20))
        btn2BSizer.Add(self.button_MoveDown, 0, wx.EXPAND, 0)
        btn2BSizer.Add((20,20))
        btn2BSizer.Add(self.button_Remove, 0, wx.EXPAND, 5)
        sizer_sbox_selected.Add(self.listbox_selected, 0, wx.ALL, 5)
        sizer_sbox_selected.Add(btn2BSizer, 0, wx.ALL, 5)


        btnGSizer = wx.GridSizer(1, 2, 0, 0)
        btnGSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnGSizer.Add(self.cancelBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        topBSizer.Add((40,20))
        topBSizer.Add(sizer_sbox_hkl, 0, wx.EXPAND, 0)
        topBSizer.Add((20,20))
        topBSizer.Add(sizer_sbox_selected, 0, wx.EXPAND, 0)
        btnBSizer.Add(btnGSizer, 0, wx.EXPAND, 0)
        mainBSizer.Add((20,20))
        mainBSizer.Add(topBSizer, 0, wx.EXPAND, 0)
        mainBSizer.Add((20,20))
        mainBSizer.Add(btnBSizer, 0, wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(mainBSizer)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel=DiffractionPanel(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()