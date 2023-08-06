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
import epscComp.utility
from SCMPanel import SCMPanel

class ExperimentPanel(wx.Panel, SCMPanel):

    """ Phase1Panel is the panel which gets material parameters of matrix.
    """

    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.controller = self.Parent.Parent.controller
        self.treePanel = self.Parent.Parent.treePanel
        self.kind = self.Parent.Parent.kind

        self.text = "The file format is as follows:\n\
            1st  column(Macro_Strain):    Macro strain, in %\n\
            2nd  column(Macro_Strain_Error):    Standard deviation for macro strain, in % \n\
            3rd  column(Macro_Stress):    Macro stress, in MPa \n\
            4th  column(Macro_Stress_Error):    Standard deviation for macro stress, in MPa \n\
            5th  column(ex. 110_Long):    Longitudinal lattice strain for the first reflection in micro strain (10-6) \n\
            6th  column(ex. 110_Long_Error):    Standard deviation of the above lattice strain in micro strain (10-6) \n\
            7th  column:    Continue with longitudinal lattice strains for other reflections\n\
            8th  column:    Continue with standard deviations for the longitudinal lattice strains\n\
            9th  column(ex. 110_Trans):    Transverse  lattice strain for the first reflection in micro strain (10-6) \n\
            10th column(ex. 110_Trans_Error):    Standard deviation of the above lattice strain in micro strain (10-6) \n\
            11th column:    Continue with transverse lattice strains for other reflections\n\
            12th column:    Continue with standard deviations for the transverse lattice strains\n\n\
            Note:\n\
            1. _Error columns are optional\n\
            2. Column orders can be arbitrary\n\
            3. HKL experimental data number is not necessarily same as that of DIFFRACTION.DIF\n"

        self.file_Exp = ""
        self.label_exp = wx.StaticText(self, -1, self.text, size=(650,300))

        self.sbox_Exp = wx.StaticBox(self, -1, "Experiment Data File")
        self.text_Exp = wx.TextCtrl(self, -1, "", size=(500,-1))
        self.button_Exp = wx.Button(self, 30, "Browse")

        self.Bind(wx.EVT_BUTTON, self.OnExpDataFile, self.button_Exp)
        self.okBtn = wx.Button(self, -1, "OK")
        self.cancelBtn = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
 #       self.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnElasticChange, self.elasticGrid)
        self.__do_layout()
        self.showData()

    def showData(self):
        self.text_Exp.SetValue(self.controller.epscData.expData.expFile)
        self.file_Exp = self.controller.epscData.expData.expFile

    def OnExpDataFile(self, event):
        dlg = wx.FileDialog(
            self, message = "Choose an experiment data file",
            defaultDir = epscComp.config.dirEpscCore,
            defaultFile = "",
            wildcard = "All files (*.*)|*.*",
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK :
            self.file_Exp = dlg.GetPaths()[0]
            self.text_Exp.SetValue(dlg.GetPaths()[0])

    def OnOK(self,event):

        if not self.file_Exp :
            msg = "You should input experimental file name!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if(epscComp.utility.checkExp(self.file_Exp, ['Macro_Strain','Macro_Stress']) == False):
            msg  = "Input data format is not valid.\n"
            msg += "Header format must be \"Macro_Strain\" and \"Macro_Stress\"" + '\n'
            msg += ', and two columns for strain and stress are reqiured for data format.'
            dlg = wx.MessageDialog(self, msg, "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.controller.epscData.phaseNum == 201 \
            or self.controller.epscData.phaseNum == 2021 \
            or self.controller.epscData.phaseNum == 2031 :
            self.controller.epscData.expData.expFile = self.file_Exp
#            print "in exp panel" , self.controller.epscData.expData.expFile
        else :
            self.controller.epscData.expData.expPh2File = self.file_Exp
#        if self.controller.epscData.expData.checkFlagOn("expData") == False: # if first time, create tree item
#            self.treePanel.macroItem = self.treePanel.tree.AppendItem \
#            (self.treePanel.expItem, "Experimental data file: On")
#            self.treePanel.tree.Expand(self.treePanel.expItem)
        self.treePanel.turnOnExpNode()
        self.controller.epscData.expData.turnOnFlag("expData")
#        self.controller.epscOpt.colData.collectExpData()
        self.controller.epscData.isAltered = True


    def OnCancel(self, event):
        self.text_Exp.SetValue("")
        self.treePanel.turnOffExpNode()
        self.controller.epscData.expData.turnOffFlag("expData")

    def __do_layout(self):
        topBSizer = wx.BoxSizer(wx.VERTICAL)

        sizer_sbox_Exp = wx.StaticBoxSizer(self.sbox_Exp, wx.HORIZONTAL)

        stepsFGSizer= wx.FlexGridSizer(cols=3,hgap=5, vgap=5)
        stepsFGSizer.Add((30,20))
        stepsFGSizer.Add(self.label_exp, 0, wx.ALL, 5)

        grid_sizer_Exp = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        grid_sizer_Exp.Add(self.text_Exp, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 5)
        grid_sizer_Exp.Add(self.button_Exp, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_sbox_Exp.Add(grid_sizer_Exp, 0, wx.EXPAND, 0)

        btnGSizer = wx.GridSizer(1, 2, 0, 0)
        btnGSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnGSizer.Add(self.cancelBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        topBSizer.Add((20,20))
        topBSizer.Add(stepsFGSizer, 0, wx.EXPAND, 5)
        topBSizer.Add((20,20))
        topBSizer.Add(sizer_sbox_Exp, 0, wx.EXPAND, 5)
        topBSizer.Add(btnGSizer, 0, wx.EXPAND, 5)

        self.SetAutoLayout(True)
        self.SetSizer(topBSizer)

