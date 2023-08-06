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

class DeformationPanel(wx.Panel, SCMPanel):

    """ DeformationPane is the panel which gets voce parameters.
    """

    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.controller = self.Parent.Parent.controller
        self.treePanel = self.Parent.Parent.treePanel
        self.kind = self.Parent.Parent.kind
        self.num_selected = 0
        self.str_selected = ""

        self.num_selected_systems = 0
        self.label_empty = wx.StaticText(self, -1, "      ")
        self.label_hkl = wx.StaticText(self, -1,"h    k    l", size=(170,20))
        self.label_tauZero = wx.StaticText(self, -1, "Tau Zero (GPa)", size=(100,20))
        self.label_tauOne = wx.StaticText(self, -1, "Tau One (GPa)", size=(100,20))
        self.label_thetaZero = wx.StaticText(self, -1, "Theta Zero (GPa)", size=(100,20))
        self.label_thetaOne = wx.StaticText(self, -1, "Theta One (GPa)", size=(100,20))

        if self.controller.epscData.phaseNum == 2032 :
            self.label_Matrix = wx.StaticText(self, -1, "Only one slip system for matrix", size=(200,20))
            self.text_Matrix_tauZero = wx.TextCtrl(self, -1, "")
            self.text_Matrix_tauOne = wx.TextCtrl(self, -1, "")
            self.text_Matrix_thetaZero = wx.TextCtrl(self, -1, "")
            self.text_Matrix_thetaOne = wx.TextCtrl(self, -1, "")

        elif self.controller.epscData.matParam[self.kind].typeCrystal == 0 : # in case of BCC
            self.chbox_BCC = []
            self.label_BCC = []
            self.text_BCC_tauZero = []
            self.text_BCC_tauOne = []
            self.text_BCC_thetaZero = []
            self.text_BCC_thetaOne = []
            labelBCC = ["{110}<111> Slip","{112}<111> Slip","{123}<111> Slip"]
            for i in range(3) :
                self.chbox_BCC.append(wx.CheckBox(self, -1, ""))
                self.label_BCC.append(wx.StaticText(self, -1,labelBCC[i],size=(170,20)))
                self.text_BCC_tauZero.append(wx.TextCtrl(self, -1,""))
                self.text_BCC_tauOne.append(wx.TextCtrl(self, -1,""))
                self.text_BCC_thetaZero.append(wx.TextCtrl(self, -1,""))
                self.text_BCC_thetaOne.append(wx.TextCtrl(self, -1,""))
                self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.chbox_BCC[i])

        elif self.controller.epscData.matParam[self.kind].typeCrystal == 1 : # in case of FCC
            self.chbox_FCC = []
            self.label_FCC = []
            self.text_FCC_tauZero = []
            self.text_FCC_tauOne = []
            self.text_FCC_thetaZero = []
            self.text_FCC_thetaOne = []
            labelFCC = ["{110}<111> Slip"]
            for i in range(1) :
                self.chbox_FCC.append(wx.CheckBox(self, -1, ""))
                self.label_FCC.append(wx.StaticText(self, -1,labelFCC[i],size=(170,20)))
                self.text_FCC_tauZero.append(wx.TextCtrl(self, -1,""))
                self.text_FCC_tauOne.append(wx.TextCtrl(self, -1,""))
                self.text_FCC_thetaZero.append(wx.TextCtrl(self, -1,""))
                self.text_FCC_thetaOne.append(wx.TextCtrl(self, -1,""))
                self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.chbox_FCC[i])

        else : #in case of HCP
            self.chbox_HCP = []
            self.label_HCP = []
            self.text_HCP_tauZero = []
            self.text_HCP_tauOne = []
            self.text_HCP_thetaZero = []
            self.text_HCP_thetaOne = []
            labelHCP = ["BASAL","PRSM1ORD","PRSM2ORD","PYR1ORDA","PYR1C+A","PYR2ORDR","PYR_COMP_TWIN","PYR_TENS_TWIN"]
            for i in range(8) :
                self.chbox_HCP.append(wx.CheckBox(self, -1, ""))
                self.label_HCP.append(wx.StaticText(self, -1,labelHCP[i],size=(170,20)))
                self.text_HCP_tauZero.append(wx.TextCtrl(self, -1,""))
                self.text_HCP_tauOne.append(wx.TextCtrl(self, -1,""))
                self.text_HCP_thetaZero.append(wx.TextCtrl(self, -1,""))
                self.text_HCP_thetaOne.append(wx.TextCtrl(self, -1,""))

        self.okBtn = wx.Button(self, -1, "OK")
        self.cancelBtn = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        self.__do_layout()
        self.showData()

    def crystalData(self):
        return(["BCC","FCC","HCP"])

    def __do_layout(self):
        topBSizer = wx.BoxSizer(wx.VERTICAL)

        labelFGSizer= wx.FlexGridSizer(cols=6,hgap=5, vgap=5)
        labelFGSizer.Add(self.label_empty, 0, wx.ALL, 5)
        labelFGSizer.Add(self.label_hkl, 0, wx.ALL, 5)
        labelFGSizer.Add(self.label_tauZero, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        labelFGSizer.Add(self.label_tauOne, 0, wx.ALL, 5)
        labelFGSizer.Add(self.label_thetaZero, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        labelFGSizer.Add(self.label_thetaOne, 0, wx.ALL, 5)

        topBSizer.Add((20,20))
        topBSizer.Add(labelFGSizer, 0, wx.EXPAND, 0)
        if self.controller.epscData.phaseNum == 2032 :
            dataFGSizer_0 = wx.FlexGridSizer(cols=6, hgap=5, vgap=5)
            dataFGSizer_0.Add(self.label_Matrix, 0, wx.ALL, 5)
            dataFGSizer_0.Add(self.text_Matrix_tauZero, 0, wx.ALL, 5)
            dataFGSizer_0.Add(self.text_Matrix_tauOne, 0, wx.ALL, 5)
            dataFGSizer_0.Add(self.text_Matrix_thetaZero, 0, wx.ALL, 5)
            dataFGSizer_0.Add(self.text_Matrix_thetaOne, 0, wx.ALL, 5)
            topBSizer.Add(dataFGSizer_0, wx.EXPAND, 0)
        elif self.controller.epscData.matParam[self.kind].typeCrystal == 0 :
            for i in range(3):
                dataFGSizer_1 = wx.FlexGridSizer(cols=6, hgap=5, vgap=5)
                dataFGSizer_1.Add(self.chbox_BCC[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.label_BCC[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_BCC_tauZero[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_BCC_tauOne[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_BCC_thetaZero[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_BCC_thetaOne[i], 0, wx.ALL, 5)
                topBSizer.Add(dataFGSizer_1, 0, wx.EXPAND, 0)
        elif self.controller.epscData.matParam[self.kind].typeCrystal == 1:
            for i in range(1) :
                dataFGSizer_1 = wx.FlexGridSizer(cols=6, hgap=5, vgap=5)
                dataFGSizer_1.Add(self.chbox_FCC[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.label_FCC[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_FCC_tauZero[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_FCC_tauOne[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_FCC_thetaZero[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_FCC_thetaOne[i], 0, wx.ALL, 5)
                topBSizer.Add(dataFGSizer_1, 0, wx.EXPAND, 0)

        elif self.controller.epscData.matParam[self.kind].typeCrystal == 2 :
            for i in range(8):
                dataFGSizer_1 = wx.FlexGridSizer(cols=6, hgap=5, vgap=5)
                dataFGSizer_1.Add(self.chbox_HCP[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.label_HCP[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_HCP_tauZero[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_HCP_tauOne[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_HCP_thetaZero[i], 0, wx.ALL, 5)
                dataFGSizer_1.Add(self.text_HCP_thetaOne[i], 0, wx.ALL, 5)
                topBSizer.Add(dataFGSizer_1, 0, wx.EXPAND, 0)
        btnGSizer = wx.GridSizer(1, 2, 0, 0)
        btnGSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnGSizer.Add(self.cancelBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        topBSizer.Add(btnGSizer, 0, wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(topBSizer)

    def filesData(self):
        return({"Phase1":"MATERIAL_1.sx","2Phase1":"MATERIAL_1.sx","2Phase2":"MATERIAL_2.sx"})

    def checkValues(self):

        if self.controller.epscData.matParam[self.kind].typeCrystal == 0 :
            for i in range(3):
                if self.chbox_BCC[i].GetValue() :
                    if self.text_BCC_tauZero[i].IsEmpty():
                        msg = "EPSC needs Tau Zero for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if self.text_BCC_tauOne[i].IsEmpty():
                        msg = "EPSC needs Tau One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if self.text_BCC_thetaZero[i].IsEmpty():
                        msg = "EPSC needs Theta Zero for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        return 0
                    if self.text_BCC_thetaOne[i].IsEmpty():
                        msg = "EPSC needs Theta One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_BCC_thetaOne[i].GetValue())> float(self.text_BCC_thetaZero[i].GetValue()) :
                        msg = "EPSC needs Theta Zero greater than Theta One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_BCC_tauZero[i].GetValue())<=0:
                        msg = "EPSC needs Tau Zero greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_BCC_tauOne[i].GetValue())<0:
                        msg = "EPSC needs Tau One greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_BCC_thetaZero[i].GetValue())<0:
                        msg = "EPSC needs Theta Zero greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_BCC_thetaOne[i].GetValue())<0:
                        msg = "EPSC needs Theta One greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
        elif self.controller.epscData.matParam[self.kind].typeCrystal == 1 :
            for i in range(1):
                if self.chbox_FCC[i].GetValue() :
                    if self.text_FCC_tauZero[i].IsEmpty():
                        msg = "EPSC needs Tau Zero for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if self.text_FCC_tauOne[i].IsEmpty():
                        msg = "EPSC needs Tau One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if self.text_FCC_thetaZero[i].IsEmpty():
                        msg = "EPSC needs Theta Zero for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        return 0
                    if self.text_FCC_thetaOne[i].IsEmpty():
                        msg = "EPSC needs Theta One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_FCC_thetaOne[i].GetValue())> float(self.text_FCC_thetaZero[i].GetValue()) :
                        msg = "EPSC needs Theta Zero greater than Theta One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_FCC_tauZero[i].GetValue())<=0:
                        msg = "EPSC needs Tau Zero greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_FCC_tauOne[i].GetValue())<0:
                        msg = "EPSC needs Tau One greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_FCC_thetaZero[i].GetValue())<0:
                        msg = "EPSC needs Theta Zero greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_FCC_thetaOne[i].GetValue())<0:
                        msg = "EPSC needs Theta One greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
        else:
            for i in range(8):
                if self.chbox_HCP[i].GetValue() :
                    if self.text_HCP_tauZero[i].IsEmpty():
                        msg = "EPSC needs Tau Zero for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if self.text_HCP_tauOne[i].IsEmpty():
                        msg = "EPSC needs Tau One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if self.text_HCP_thetaZero[i].IsEmpty():
                        msg = "EPSC needs Theta Zero for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        return 0
                    if self.text_HCP_thetaOne[i].IsEmpty():
                        msg = "EPSC needs Theta One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_HCP_thetaOne[i].GetValue())> float(self.text_HCP_thetaZero[i].GetValue()) :
                        msg = "EPSC needs Theta Zero greater than Theta One for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_HCP_tauZero[i].GetValue())<=0:
                        msg = "EPSC needs Tau Zero greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_HCP_tauOne[i].GetValue())<0:
                        msg = "EPSC needs Tau One greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_HCP_thetaZero[i].GetValue())<0:
                        msg = "EPSC needs Theta Zero greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0
                    if float(self.text_HCP_thetaOne[i].GetValue())<0:
                        msg = "EPSC needs Theta One greater than 0 for Voce parameters!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return 0

    def showData(self):
        if self.controller.epscData.matParam[self.kind].typeCrystal == 0 : # in case of BCC

            for i in range(self.controller.epscData.matParam[self.kind].numSystems):
                self.chbox_BCC[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(True)
                self.text_BCC_tauZero[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][0]))
                self.text_BCC_tauOne[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][1]))
                self.text_BCC_thetaZero[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][2]))
                self.text_BCC_thetaOne[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][3]))

        if self.controller.epscData.matParam[self.kind].typeCrystal == 1 : # in case of FCC
            for i in range(self.controller.epscData.matParam[self.kind].numSystems):
                self.chbox_FCC[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(True)
                self.text_FCC_tauZero[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][0]))
                self.text_FCC_tauOne[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][1]))
                self.text_FCC_thetaZero[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][2]))
                self.text_FCC_thetaOne[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][3]))
        if self.controller.epscData.matParam[self.kind].typeCrystal == 2 : # in case of BCC
            for i in range(self.controller.epscData.matParam[self.kind].numSystems):
                self.chbox_HCP[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(True)
                self.text_HCP_tauZero[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][0]))
                self.text_HCP_tauOne[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][1]))
                self.text_HCP_thetaZero[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][2]))
                self.text_HCP_thetaOne[int(self.controller.epscData.matParam[self.kind].selectedSystems[i])-1].SetValue(str(self.controller.epscData.matParam[self.kind].voce[i][3]))

    def OnCheck(self,event):

        if event.IsChecked():
            self.num_selected_systems += 1
        else :
            self.num_selected_systems -= 1
        if self.num_selected_systems > 3:
            msg = "EPSC does not allow more than 3 slip & twining systems for BCC."
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            event.GetEventObject().SetValue(False)
            self.num_selected_systems -= 1
            return

    def OnOK(self,event):
        if self.checkValues()!=0 :
            self.num_selected = 0
            self.str_selected = ""
            if self.controller.epscData.matParam[self.kind].typeCrystal == 0 : # BCC
                for i in range(3) :
                    if self.chbox_BCC[i].GetValue() == True :
                        self.num_selected += 1
                        self.str_selected += str(i+1) + "    "
                        self.controller.epscData.matParam[self.kind].selectedSystems.append(i+1)
                        self.controller.epscData.matParam[self.kind].voce[i][0] = float(self.text_BCC_tauZero[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][1] = float(self.text_BCC_tauOne[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][2] = float(self.text_BCC_thetaZero[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][3] = float(self.text_BCC_thetaOne[i].GetValue())

            elif self.controller.epscData.matParam[self.kind].typeCrystal == 1 :
                for i in range(1):
                    if self.chbox_FCC[i].GetValue() == True :
                        self.num_selected += 1
                        self.str_selected += str(i+1) + "    "
                        self.controller.epscData.matParam[self.kind].selectedSystems.append(i+1)
                        self.controller.epscData.matParam[self.kind].voce[i][0] = float(self.text_FCC_tauZero[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][1] = float(self.text_FCC_tauOne[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][2] = float(self.text_FCC_thetaZero[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][3] = float(self.text_FCC_thetaOne[i].GetValue())

            else: # HCC
                for i in range(8):
                    if self.chbox_HCP[i].GetValue() == True :
                        self.num_selected += 1
                        self.str_selected += str(i+1) + "    "
                        self.controller.epscData.matParam[self.kind].selectedSystems.append(i+1)
                        self.controller.epscData.matParam[self.kind].voce[i][0] = float(self.text_HCP_tauZero[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][1] = float(self.text_HCP_tauOne[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][2] = float(self.text_HCP_thetaZero[i].GetValue())
                        self.controller.epscData.matParam[self.kind].voce[i][3] = float(self.text_HCP_thetaOne[i].GetValue())
            self.controller.epscData.matParam[self.kind].numSystems = self.num_selected
            #for i in range(4):
            #    self.controller.epscData.matParam.setMatrix("voce" + self.kind, 0, i, self.voceGrid.GetCellValue(0, i))
            #self.updateTree()
            self.updatePhase()
            self.treePanel.turnOnNode(self.controller.epscData.phaseNum, 2)
            self.controller.epscData.isAltered = True
            self.Parent.SetSelection(3)
            self.Parent.Parent.Parent.optMenuOn()

    def OnCancel(self, event):
        if self.controller.epscData.matParam[self.kind].typeCrystal == 0 : # in case of BCC
            for i in range(3):
                self.chbox_BCC[i].SetValue(False)
                self.text_BCC_tauZero[i].SetValue("")
                self.text_BCC_tauOne[i].SetValue("")
                self.text_BCC_thetaZero[i].SetValue("")
                self.text_BCC_thetaOne[i].SetValue("")

        if self.controller.epscData.matParam[self.kind].typeCrystal == 1 : # in case of FCC
            for i in range(1):
                self.chbox_FCC[i].selectedSystems[i].SetValue(False)
                self.text_FCC_tauZero[i].SetValue("")
                self.text_FCC_tauOne[i].SetValue("")
                self.text_FCC_thetaZero[i].SetValue("")
                self.text_FCC_thetaOne[i].SetValue("")
        if self.controller.epscData.matParam[self.kind].typeCrystal == 2 : # in case of BCC
            for i in range(8):
                self.chbox_HCP[i].SetValue(False)
                self.text_HCP_tauZero[i].SetValue("")
                self.text_HCP_tauOne[i].SetValue("")
                self.text_HCP_thetaZero[i].SetValue("")
                self.text_HCP_thetaOne[i].SetValue("")
        self.treePanel.turnOffNode(self.controller.epscData.phaseNum, 2)

    def subVoce(self,vocePars,slipNum):
        '''vocePars= a list of voce pars in the correct order'''
        count = 0
#        self.phase1Str = self.strTemplate
        for vocePar in vocePars:
            count = count + 1
            voceStr = "%s" % vocePar
            self.phase1Str = self.phase1Str.replace("$Voce_SS"+slipNum+"_"+`count`,voceStr)
#            p = re.compile(r"\$Voce_SS"+ `slipNum` +"_"+`count`)
#            self.phase1Str, num = re.subn(p,`vocePar`,self.phase1Str)
            print 'Voce parameter %s has been replaced to %s'%(count, vocePar)

# update phase1 file
    def updatePhase(self):

        """ create/update matrix data file using template_matrix.dat
        """
        strAll = ""
        fid = open(epscComp.config.dirEpscCore + "template_MATERIAL.sx")
        strNumModes = "*Number of modes to read:"
        while 1:
            line = fid.readline()
            if not line :
                break
            if line.find(strNumModes)!=-1:
                strAll += line
                strAll += str(self.num_selected) + "\n"
                fid.readline()
                strAll += fid.readline()
                strAll += self.str_selected + "\n"
                fid.readline()
            else :
                strAll += line
        self.strTemplate = strAll
        fid.close()
        if self.kind == "Phase1" or self.kind == "2Phase1" :
            fid = open(epscComp.config.dirEpscCore+ "template_MATERIAL_Phase1_opt.sx",'w')
        elif self.kind == "2Phase2" :
            fid = open(epscComp.config.dirEpscCore+ "template_MATERIAL_Phase2_opt.sx",'w')
        fid.write(strAll)
        fid.close
        self.phase1Str = self.strTemplate
        voce_list = []
        for i in range(8) :
            voce_list.append([self.controller.epscData.matParam[self.kind].voce[i][0],self.controller.epscData.matParam[self.kind].voce[i][1],\
                     self.controller.epscData.matParam[self.kind].voce[i][2],self.controller.epscData.matParam[self.kind].voce[i][3]])
            self.subVoce(voce_list[i],str(i+1))
        #print voce_list

        fid = open(epscComp.config.dirEpscCore+ self.filesData()[self.kind],'w')
        fid.write(self.phase1Str)
        fid.close
        print self.phase1Str
