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

class ProcessPanel(wx.Panel, SCMPanel):

    """ Panel to get information about process.
            Process Number
            Type of process
                Temperature, Strain, Stress
    """

    def __init__(self, *args, **kwds):

        tempKwds={}
        for key in kwds :
            if key != "processNum" :
                tempKwds["key"] = kwds["key"]
        SCMPanel.__init__(self, *args, **tempKwds)
        wx.Panel.__init__(self, *args, **tempKwds)

        self.processNum = kwds["processNum"]
        self.controller = self.Parent.Parent.controller
        self.treePanel = self.Parent.Parent.treePanel
        self.kind = self.Parent.Parent.kind

        self.selectedProcess = 0
        self.tempStart = 0
        self.tempFinal = 0
        self.strain = 0
        self.stress = 0


        self.label_numStep = wx.StaticText(self, -1, "Number Of Steps", size=(150,20))
        self.text_numStep = wx.TextCtrl(self, -1, "100", size=(100,20))

        self.radio_temperature = wx.RadioButton(self, -1, "")
        self.label_temperature= wx.StaticText(self, -1, "Temperature", size=(150,20))
        self.label_startTemp = wx.StaticText(self, -1, "Initial Temp (K)", size=(120,20))
        self.text_startTemp = wx.TextCtrl(self, -1, "",size=(100,20))
        self.label_finalTemp = wx.StaticText(self, -1, "Final Temp (K)", size=(100,20))
        self.text_finalTemp = wx.TextCtrl(self, -1, "", size=(100,20))

        self.radio_strain = wx.RadioButton(self, -1, "")
        self.label_strain= wx.StaticText(self, -1, "Strain", size=(150,20))
        self.label_strainDelta = wx.StaticText(self, -1, "Maximum Strain", size=(120,20))
        self.text_strainDelta = wx.TextCtrl(self, -1, "-0.016",size=(100,20))
        self.radio_strain.SetValue(True)

        self.radio_stress = wx.RadioButton(self, -1, "")
        self.label_stress= wx.StaticText(self, -1, "Stress", size=(150,20))
        self.label_stressFinal = wx.StaticText(self, -1, "Maximum Stress (GPa)", size=(120,20))
        self.text_stressFinal = wx.TextCtrl(self, -1, "",size=(100,20))

        self.okBtn = wx.Button(self, -1, "OK")
        self.cancelBtn = wx.Button(self, -1, "Cancel")

        if self.controller.epscData.processDataSaved == True :
            self.getData()

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioTemp, self.radio_temperature)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioStrain, self.radio_strain)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioStress, self.radio_stress)
 #       self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnElasticChange, self.elasticGrid)
        self.__do_layout()

    def showData(self):
        self.text_numStep.SetValue(str(self.controller.epscData.processParam.numSteps))
        if self.controller.epscData.processParam.selectedProcess == 1:
            self.radio_temperature.SetValue(True)
            self.text_startTemp.SetValue(str(self.controller.epscData.processParam.tempStart))
            self.text_finalTemp.SetValue(str(self.controller.epscData.processParam.tempFinal))
        elif self.controller.epscData.processParam.selectedProcess == 2:
            self.radio_strain.SetValue(True)
            self.text_strainDelta.SetValue(str(self.controller.epscData.processParam.strain))
        else :
            self.radio_stress.SetValue(True)
            self.text_stressFinal.SetValue(str(self.controller.epscData.processParam.stress))

    def OnRadioTemp(self, event):
        self.selectedProcess = 1
        self.text_strainDelta.Enable(False)
        self.text_stressFinal.Enable(False)
        self.text_startTemp.Enable(True)
        self.text_finalTemp.Enable(True)

    def OnRadioStrain(self, event):
        self.selectedProcess = 2
        self.text_startTemp.Enable(False)
        self.text_finalTemp.Enable(False)
        self.text_stressFinal.Enable(False)
        self.text_strainDelta.Enable(True)

    def OnRadioStress(self, event):
        self.selectedProcess = 3
        self.text_startTemp.Enable(False)
        self.text_finalTemp.Enable(False)
        self.text_strainDelta.Enable(False)
        self.text_stressFinal.Enable(True)

    def updateEpscData(self):
        self.controller.epscData.processParam.numSteps = self.numSteps
        self.controller.epscData.processParam.selectedProcess = self.selectedProcess
        self.controller.epscData.processParam.tempStart = self.tempStart
        self.controller.epscData.processParam.tempFinal = self.tempFinal
        self.controller.epscData.processParam.strain = self.strain
        self.controller.epscData.processParam.stress = self.stress
        self.controller.epscData.processParam.saved = True

    def OnOK(self,event):

        self.numSteps = self.text_numStep.GetValue()
        if self.numSteps == "" :
            msg = "You should input Number of Steps!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
#        if self.selectedProcess == 0 :
#            msg = "You should select the type of process!"
#            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
#            dlg.ShowModal()
#            dlg.Destroy()
#            return
        elif self.selectedProcess == 1 :
            self.tempStart = self.text_startTemp.GetValue()
            self.tempFinal = self.text_finalTemp.GetValue()
        elif self.selectedProcess == 3:
            self.stress = self.text_stressFinal.GetValue()
        else :
            self.selectedProcess = 2
            self.strain = self.text_strainDelta.GetValue()
        self.updateEpscData()
        self.updateProcessFile("PROCESS_" + str(self.processNum) + ".pro")
        self.treePanel.turnOnNode(self.controller.epscData.phaseNum, 5)

    def OnCancel(self, event):
        self.text_numStep.SetValue(str(self.controller.epscData.processParam.numSteps))
        self.radio_strain.SetValue(True)
        self.text_strainDelta.SetValue(str(self.controller.epscData.processParam.strain))
        self.OnRadioStrain(None)
        self.treePanel.turnOffNode(self.controller.epscData.phaseNum, 5)

    def __do_layout(self):
        topBSizer = wx.BoxSizer(wx.VERTICAL)

        stepsFGSizer= wx.FlexGridSizer(cols=3,hgap=5, vgap=5)
        stepsFGSizer.Add((30,20))
        stepsFGSizer.Add(self.label_numStep, 0, wx.ALL, 5)
        stepsFGSizer.Add(self.text_numStep, 0, wx.ALL, 5)

        tempFGSizer= wx.FlexGridSizer(cols=6,hgap=5, vgap=5)
        tempFGSizer.Add(self.radio_temperature, 0, wx.ALL, 5)
        tempFGSizer.Add(self.label_temperature, 0, wx.ALL, 5)
        tempFGSizer.Add(self.label_startTemp, 0, wx.ALL, 5)
        tempFGSizer.Add(self.text_startTemp, 0, wx.ALL, 5)
        tempFGSizer.Add(self.label_finalTemp, 0, wx.ALL, 5)
        tempFGSizer.Add(self.text_finalTemp, 0, wx.ALL, 5)

        strainFGSizer= wx.FlexGridSizer(cols=6,hgap=5, vgap=5)
        strainFGSizer.Add(self.radio_strain, 0, wx.ALL, 5)
        strainFGSizer.Add(self.label_strain, 0, wx.ALL, 5)
        strainFGSizer.Add(self.label_strainDelta, 0, wx.ALL, 5)
        strainFGSizer.Add(self.text_strainDelta, 0, wx.ALL, 5)

        stressFGSizer= wx.FlexGridSizer(cols=6,hgap=5, vgap=5)
        stressFGSizer.Add(self.radio_stress, 0, wx.ALL, 5)
        stressFGSizer.Add(self.label_stress, 0, wx.ALL, 5)
        stressFGSizer.Add(self.label_stressFinal, 0, wx.ALL, 5)
        stressFGSizer.Add(self.text_stressFinal, 0, wx.ALL, 5)

        btnGSizer = wx.GridSizer(1, 2, 0, 0)
        btnGSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnGSizer.Add(self.cancelBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        topBSizer.Add((20,20))
        topBSizer.Add(stepsFGSizer, 0, wx.EXPAND, 5)
        topBSizer.Add(tempFGSizer, 0, wx.EXPAND, 5)
        topBSizer.Add(strainFGSizer, 0, wx.EXPAND, 5)
        topBSizer.Add(stressFGSizer, 0, wx.EXPAND, 5)
        topBSizer.Add((20,20))
        topBSizer.Add(btnGSizer, 0, wx.EXPAND, 5)

        self.SetAutoLayout(True)
        self.SetSizer(topBSizer)

    def replaceData(self, orig):
        orig = orig.replace("$Num_Steps", str(self.numSteps))
        if self.selectedProcess == 1:
            orig = orig.replace("$Start_Temp", str(self.tempStart))
            orig = orig.replace("$Final_Temp", str(self.tempFinal))
        elif self.selectedProcess == 2:
            orig = orig.replace("$Strain", str(self.strain))
        else:
            orig = orig.replace("$Stress", str(self.stress))

        return orig

    def templateFiles(self):
        return({1:"Thermal.pro", 2:"Strain_3.pro", 3:"Stress_3.pro"})

    def updateProcessFile(self,file):

        """ create/update process file
        """
        strAll = ""
        if self.selectedProcess == 0 :
            self.selectedProcess = 2
        fid = open(epscComp.config.dirEpscCore + self.templateFiles()[self.selectedProcess])

        while 1:
            line = fid.readline()
            if not line :
                break
            strAll = strAll + line
        fid.close()

        strResult = self.replaceData(strAll)
        print strResult
        fid = open(epscComp.config.dirEpscCore+ file, 'w')
        fid.write(strResult)
        fid.close
        self.controller.epscData.processDataSaved = True

    def getData(self):
        if self.controller.epscData.processParam.saved :
            self.showData()
        else:
            self.getDatafromFile()

    def getDatafromFile(self):

        """ get existing data from process files (PROCESS_1.pro, PROCESS_2.pro, etc)
        """
        strAll = ""

        fid = open(epscComp.config.dirEpscCore + "PROCESS_" + str(self.processNum) + ".pro")

        while 1:
            line = fid.readline()
            if not line :
                break
            strAll = strAll + line
            line.find("*Number of steps")
            strAll = strAll + line
        fid.close()


if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel=Phase1Panel(frame,("test",23))
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()