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
from hklDialog import HKLDialog
from SCMPanel import SCMPanel

class OptBCCDataPanel(wx.Panel, SCMPanel):
    """
    Optimization data input panel for BCC structure
    Selection of macro and hkl.
    Low and high values for bounded optimization
    """

    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.controller = self.Parent.Parent.controller
        self.sizer_Model_staticbox = wx.StaticBox(self, -1, "Model Parameters Setting")
        self.sizer_Experiment_staticbox = wx.StaticBox(self, -1, "Experiment Data Setting")
        self.chkbox_macro = wx.CheckBox(self, -1,"Macro (Extensometer)")
        self.chkbox_hkl = wx.CheckBox(self, -1,"HKL (Neutron)")
        self.button_HKL = wx.Button(self, -1, "Select HKLs")

        self.static_line_1 = wx.StaticLine(self, -1, style=wx.LI_VERTICAL)

        self.sizer_slip_staticbox = []
        self.sizer_slip_staticbox.append(wx.StaticBox(self, -1, "Slip {110}<111>"))
        self.sizer_slip_staticbox.append(wx.StaticBox(self, -1, "Slip {112}<111>"))
        self.sizer_slip_staticbox.append(wx.StaticBox(self, -1, "Slip {123}<111>"))
#        self.sizer_slip_staticbox.append(wx.StaticBox(self, -1, "Twin {112}<111>"))
        self.chbox_voceBCC = [[],[],[],[]]
        self.label_name_voceBCC = []
        self.label_initial_voceBCC = []
        self.label_low_voceBCC = []
        self.label_high_voceBCC = []
        self.text_initial_voceBCC = [[],[],[],[]]
        self.text_low_voceBCC = [[],[],[],[]]
        self.text_high_voceBCC = [[],[],[],[]]
        self.nameVoce = ["Tau Zero","Tau One","Theta Zero","Theta One"]
        for i in range(3) :
            self.label_name_voceBCC.append(wx.StaticText(self, -1, "Name "))
            self.label_initial_voceBCC.append(wx.StaticText(self, -1, "Initial "))
            self.label_low_voceBCC.append(wx.StaticText(self, -1, "Low "))
            self.label_high_voceBCC.append(wx.StaticText(self, -1, "High "))
            for j in range(4) :
                self.chbox_voceBCC[i].append(wx.CheckBox(self, -1, self.nameVoce[j]))
                self.text_initial_voceBCC[i].append(wx.TextCtrl(self, -1,size=(50,-1)))
                self.text_low_voceBCC[i].append(wx.TextCtrl(self, -1,size=(50,-1)))
                self.text_high_voceBCC[i].append(wx.TextCtrl(self, -1,size=(50,-1)))
                self.text_initial_voceBCC[i][j].Enable(False)
#        if self.controller.epscData.phaseNum == 201 :
#            self.label_init_ph1 = wx.StaticText(self, -1, "Initial ")
#            self.text_ctrl_tauZeroP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("vocePhase1",0,0)),size=(50,-1))
#            self.text_ctrl_tauOneP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("vocePhase1",0,1)),size=(50,-1))
#            self.text_ctrl_thetaZeroP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("vocePhase1",0,2)),size=(50,-1))
#            self.text_ctrl_thetaOneP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("vocePhase1",0,3)),size=(50,-1))
#        else :
#            self.label_init_ph1 = wx.StaticText(self, -1, "Initial ")
#            self.text_ctrl_tauZeroP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("voce2Phase1",0,0)),size=(50,-1))
#            self.text_ctrl_tauOneP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("voce2Phase1",0,1)),size=(50,-1))
#            self.text_ctrl_thetaZeroP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("voce2Phase1",0,2)),size=(50,-1))
#            self.text_ctrl_thetaOneP_init = wx.TextCtrl(self, -1, str(self.controller.epscData.matParam.getMatrix("voce2Phase1",0,3)),size=(50,-1))

        self.button_OK = wx.Button(self, -1, "OK")
        self.button_Cancel = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON,self.OnOK, self.button_OK)
        self.Bind(wx.EVT_BUTTON,self.OnCancel, self.button_Cancel)
        self.Bind(wx.EVT_BUTTON, self.OnHKL, self.button_HKL)
        self.Bind(wx.EVT_CHECKBOX, self.OnChkHKL, self.chkbox_hkl)
        self.__set_properties()
        self.__do_layout()
#        self.showData()

    def showData(self):

        if self.controller.epscData.optData.getData("expData")=="macro":
            self.chkbox_macro.SetValue(True)
        elif self.controller.epscData.optData.getData("expData")=="hkl":
            self.chkbox_hkl.SetValue(True)
        elif self.controller.epscData.optData.getData("expData")=="both":
            self.chkbox_macro.SetValue(True)
            self.chkbox_hkl.SetValue(True)
        #print self.controller.epscData.optData.getData("expData")
        for i in range(3) :
            for j in range(4) :
                self.chbox_voceBCC[i][j].SetValue(self.controller.epscData.optData.voceFlag[i][j])
#                self.controller.epscData.matParam.setMatrix(i,j,self.text_initial_voceBCC[i][j])
                self.text_low_voceBCC[i][j].SetValue(str(self.controller.epscData.optData.lowVoce[i][j]))
                self.text_high_voceBCC[i][j].SetValue(str(self.controller.epscData.optData.highVoce[i][j]))
        self.showVoce()

    def disableRanges(self):
        for i in range(3):
            for j in range(4) :
                self.text_low_voceBCC[i][j].Enable(False)
                self.text_high_voceBCC[i][j].Enable(False)

    def enableRanges(self):
         for i in range(3):
            for j in range(4) :
                self.text_low_voceBCC[i][j].Enable(True)
                self.text_high_voceBCC[i][j].Enable(True)

    def showVoce(self):

        for i in range(3):
            if i+1 in self.controller.epscData.matParam["Phase1"].selectedSystems :
                for j in range(4) :
                    self.chbox_voceBCC[i][j].Enable(True)
                    self.text_initial_voceBCC[i][j].SetValue(str(self.controller.epscData.matParam["Phase1"].voce[i][j]))
            else :
                for j in range(4) :
                    self.chbox_voceBCC[i][j].Enable(False)

        self.Update()

    def refreshOptimizedVoce(self, p):
        count = 0
        for i in range(3):
            if i+1 in self.controller.epscData.matParam["Phase1"].selectedSystems :
                for j in range(4) :
                    if self.controller.epscData.optData.voceFlag[i][j]==1 :
                        self.text_initial_voceBCC[i][j].SetValue(str(p[count]))
                        count +=1
        self.Update()

    def OnHKL(self, event):
        if self.controller.epscData.diffractionDataSaved :
            dialog = HKLDialog(parent=self, winSize=(300,300))
        else :
            msg = "You should input diffraction data first!"
            dialog = wx.MessageDialog(self, msg, "Warning", wx.OK)

        dialog.ShowModal()
        dialog.Destroy()
        event.Skip()


    def OnChkHKL(self, event):
        if event.IsChecked():
            self.button_HKL.Enable(True)
        else :
            self.button_HKL.Enable(False)


    def OnOK(self,event):
        if self.chkbox_macro.GetValue() == True :
            self.controller.epscData.optData.setData("expData","macro")
            if self.chkbox_hkl.GetValue() == True :
                self.controller.epscData.optData.setData("expData","both")
        else :
            self.controller.epscData.optData.setData("expData","hkl")
        #print self.controller.epscData.optData.getData("expData")
        for i in range(3) :
            for j in range(4) :
                self.controller.epscData.optData.voceFlag[i][j]= self.chbox_voceBCC[i][j].GetValue()
#                self.controller.epscData.matParam.setMatrix(i,j,self.text_initial_voceBCC[i][j])
                self.controller.epscData.optData.lowVoce[i][j]= self.text_low_voceBCC[i][j].GetValue()
                self.controller.epscData.optData.highVoce[i][j]= self.text_high_voceBCC[i][j].GetValue()

        self.treePanel.turnOnOptNode(1)

        self.controller.epscData.optData.turnOnFlag("range")
        self.controller.epscData.optData.turnOnFlag("optData")

    def OnCancel(self, event):
        self.showVoce()
        for i in range(4):
            for j in range(4) :
                self.chbox_voceBCC[i][j].SetValue(False)

        self.treePanel.turnOffOptNode(1)
        self.controller.epscData.optData.turnOffFlag("optData")


    def __set_properties(self):
        # begin wxGlade: OptData.__set_properties
        self.SetSize((664, 398))
        self.SetScrollbar(wx.VERTICAL,0,6,50)
        self.FitInside()
        self.chkbox_macro.SetValue(1)
        #self.radio_box_1.SetSelection(1)
        #self.radio_box_2.SetSelection(0)
#        self.checkbox_tauZeroP.SetValue(1)
#        self.checkbox_tauOneP.SetValue(1)
#        self.checkbox_thetaZeroP.SetValue(1)

#        self.checkbox_tauZeroP2.SetValue(1)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: OptData.__do_layout
        sizer_top = wx.BoxSizer(wx.VERTICAL)
        sizer_OK = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)
        sizer_Model = wx.StaticBoxSizer(self.sizer_Model_staticbox, wx.VERTICAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 2, 0, 0)

        sizer_ph2_power = wx.BoxSizer(wx.VERTICAL)

        #sizer_ph1_voce = wx.BoxSizer(wx.VERTICAL)

        sizer_ph1_power = wx.BoxSizer(wx.VERTICAL)
        sizer_Experiment = wx.StaticBoxSizer(self.sizer_Experiment_staticbox, wx.VERTICAL)
        sizer_Experiment.Add(self.chkbox_macro, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_Experiment.Add(self.chkbox_hkl, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_Experiment.Add(self.button_HKL, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_top.Add(sizer_Experiment, 0, wx.ALL|wx.EXPAND, 2)

        for i in range(3):
            sizer_ph1 = wx.StaticBoxSizer(self.sizer_slip_staticbox[i], wx.HORIZONTAL)
            sizer_ph1_voce = wx.FlexGridSizer(5, 4, 0, 0)
            sizer_ph1_voce.Add(self.label_name_voceBCC[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            sizer_ph1_voce.Add(self.label_initial_voceBCC[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            sizer_ph1_voce.Add(self.label_low_voceBCC[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            sizer_ph1_voce.Add(self.label_high_voceBCC[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            for j in range(4) :
                sizer_ph1_voce.Add(self.chbox_voceBCC[i][j], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
                sizer_ph1_voce.Add(self.text_initial_voceBCC[i][j], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
                sizer_ph1_voce.Add(self.text_low_voceBCC[i][j], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
                sizer_ph1_voce.Add(self.text_high_voceBCC[i][j], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)


            sizer_ph1.Add(sizer_ph1_voce, 1, wx.EXPAND, 0)
            grid_sizer_1.Add(sizer_ph1, 1, wx.EXPAND, 0)

        sizer_Model.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        sizer_top.Add(sizer_Model, 0, wx.ALL|wx.EXPAND, 2)
        sizer_btn.Add((20, 20), 1, wx.ADJUST_MINSIZE, 0)
        sizer_btn.Add((20, 20), 1, wx.ADJUST_MINSIZE, 0)
        sizer_top.Add(sizer_btn, 0, wx.ALL|wx.EXPAND, 2)
        sizer_OK.Add((20, 20), 1, wx.ADJUST_MINSIZE, 0)
        sizer_OK.Add(self.button_OK, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_OK.Add(self.button_Cancel, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_top.Add(sizer_OK, 0, wx.ALL|wx.EXPAND, 2)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_top)
        # end wxGlade

# end of class OptData


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1, 'dynamic test', size=(800,600))
    frame_1 = OptBCCDataPanel(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
