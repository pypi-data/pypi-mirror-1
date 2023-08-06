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
import sys
import scipy
import epscComp.config
import epscComp.utility
from epscComp.collectData import CollectData


class PlotPanelSimulation(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)

#        self.plotnotebook = plotnotebook
        self.model_x = scipy.arange(0.0, -2.7, -0.1)
        self.exp_y = [0.00,-73.97,-147.94,-221.91,-295.88,-369.85,-443.82,\
               -517.79,-591.75,-668.55,-744.69,-817.95,-894.54,-971.56,\
               -1043.30,-1099.13,-1147.84,-1204.84,-1239.90,-1248.05,-1286.99,\
               -1311.00,-1319.53,-1336.57,-1341.16,-1349.12,-1359.27,-1359.28]
#        self.exp_y = -1*self.exp_y

        voceName = ["Modulus(GPa)", "Sigma Zero(MPa)", "Sigma One(MPa)", "Theta Zero(MPa)", "Theta One(MPa)"]
        self.label_name_voce = []
        self.text_min = []
        self.text_max = []
        self.slider = []
        self.tension = 0
        self.flagExpFile = False
        self.expFile = ""

        self.button_Exp = wx.Button(self, -1, "Exp data file import")
        self.button_Clear = wx.Button(self, -1, "Clear")
        self.static_box = wx.StaticBox(self, -1, "Analytic Simulation")
        for i in range(5):
            self.label_name_voce.append(wx.StaticText(self, -1, voceName[i]))
            if i==0:
                self.slider.append(wx.Slider(
                                self, -1, 70, 10, 1000, (10, 10), (250, 40),
                                wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS))
            elif i==2 :
                self.slider.append(wx.Slider(
                                self, -1, 400, 10, 1000, (10, 10), (250, 40),
                                wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS))

            elif i==4:
                self.slider.append(wx.Slider(
                                self, -1, 30, 0, 100, (10, 10), (250, 40),
                                wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS))
                self.slider[i].SetTickFreq(5, 1)
                self.text_min.append(wx.TextCtrl(self, -1,"10",size=(50,-1)))
                self.text_max.append(wx.TextCtrl(self, -1,"100",size=(50,-1)))
            else :
                self.slider.append(wx.Slider(
                                self, -1, 700, 10, 1000, (10, 10), (250, 40),
                                wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS))

            if i!=4 :
                self.slider[i].SetTickFreq(5, 1)
                self.text_min.append(wx.TextCtrl(self, -1,"10",size=(50,-1)))
                self.text_max.append(wx.TextCtrl(self, -1,"1000",size=(50,-1)))
#            self.text_max[i].SetValue("Max")
#            self.text_min[i].SetValue("Min")
#        self.button_plot = wx.Button(self, -1, "Plot")
#        self.button_clearPlot = wx.Button(self, -1, "Clear Plot")
        self.radio = wx.RadioBox(self, -1, "", wx.DefaultPosition, \
                                        wx.DefaultSize, ["Compression","Tension"])

        self.button_setRange = wx.Button(self, -1, "Set Range")
        self.Bind(wx.EVT_SLIDER, self.OnSlider)
        self.Bind(wx.EVT_RADIOBOX, self.OnRadio)
        self.Bind(wx.EVT_BUTTON,self.OnExp, self.button_Exp)
        self.Bind(wx.EVT_BUTTON,self.OnClear, self.button_Clear)
        self.Bind(wx.EVT_BUTTON,self.OnSetRange, self.button_setRange)
#        self.Bind(wx.EVT_SIZE,   self.OnSize)
        self.__do_layout()

    def OnRadio(self, event):
        self.tension = event.GetInt()
        if self.tension == 1 :
            self.model_x = scipy.arange(0.0, 2.7, 0.1)
        else :
            self.model_x = scipy.arange(0.0, -2.7, -0.1)
        self.OnSlider(None)

    def OnSlider(self, event):
        modulus = self.slider[0].GetValue()
        tauZero = self.slider[1].GetValue()
        tauOne = self.slider[2].GetValue()
        thetaZero = self.slider[3].GetValue()
        thetaOne = self.slider[4].GetValue()

        listY = self.update_y(modulus,tauZero,tauOne,thetaZero,thetaOne)
#        print listY
        plotinfos_model = {"name":"model","x": list(self.model_x),"y":list(listY),'type':'line', 'color':'red', 'width':1}
        self.Parent.updatePlot("macro",plotinfos_model)
#        self.Parent.plotnotebook.updatePlot("macro",plotinfos_exp)


    def update_y(self,modulus,tau0,tau1,theta0,theta1):

        model_y = []
        epsilon_0 = float(tau0)/float(modulus)*0.1 # epsilson zero = tau zero / E

#        print modulus,tau0,tau1,theta0,theta1,epsilon_0
        for x in self.model_x:
            if abs(x) <= abs(epsilon_0):
                y = modulus*abs(x)*10
                if self.tension == 0 :
                    y=-1*y
                model_y.append(y)
            else:
                y = tau0 + (tau1+theta1*abs(abs(x)-epsilon_0))*\
                    (1-scipy.exp(-theta0*abs(abs(x)-epsilon_0)/tau1))
                if self.tension == 0 :
                    y=-1*y
                model_y.append(y)
        return model_y


    def OnExp(self,event):
        dlg = wx.FileDialog(
            self, message = "Choose an experiment data file",
            defaultDir = epscComp.config.dirEpscCore,
            defaultFile = "",
            wildcard = "All files (*.*)|*.*",
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK :
            self.expFile = dlg.GetPaths()[0]
            self.flagExpFile = True
            if(epscComp.utility.checkExp(self.expFile, ['Macro_Strain','Macro_Stress']) == False):
                msg  = "Input data format is not valid.\n"
                msg += "Header format must be \"Macro_Strain\" and \"Macro_Stress\"" + '\n'
                msg += ', and two columns for strain and stress are reqiured for data format.'
                dlg = wx.MessageDialog(self, msg, "Error", wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.collectExpData()
            plotinfos_exp = {"name":"exp","x": list(self.macroExpX),\
                        "y":list(self.macroExpY),'type':'marker', 'color':'blue', 'width':1}

            self.Parent.updatePlot("macro",plotinfos_exp)

    def OnClear(self, event):
        self.flagExpFile = False
        self.expFile = ""
        plotinfos_exp = {"name":"exp","x": [],\
                        "y":[],'type':'marker', 'color':'blue', 'width':1}

        self.Parent.updatePlot("macro",plotinfos_exp)
        plotinfos_model = {"name":"model","x": [],\
                        "y":[],'type':'marker', 'color':'blue', 'width':1}

        self.Parent.updatePlot("macro",plotinfos_model)

    def OnSetRange(self, event):
        for i in range(5):
            self.slider[i].SetMin(int(self.text_min[i].GetValue()))
            self.slider[i].SetMax(int(self.text_max[i].GetValue()))

    def OnSize(self, event):
        pass
#        size = self.GetSize()

#        self.Update()
#        return

    def collectExpData(self):
        fid = open(self.expFile, 'r')
        strAll = fid.read()
        dataExp,labels = epscComp.utility.getLabelAndDataArray(strAll)
        self.macroExpX = dataExp["Macro_Strain"]
        self.macroExpY = dataExp["Macro_Stress"]
        self.model_x = self.macroExpX
        fid.close()


    def __do_layout(self):
        sizer_top = wx.BoxSizer(wx.VERTICAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)

        sizer_sbs = wx.StaticBoxSizer(self.static_box, wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(5, 4, 0, 0)
        for i in range(5):
            grid_sizer_1.Add(self.label_name_voce[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            grid_sizer_1.Add(self.slider[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            grid_sizer_1.Add(self.text_min[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
            grid_sizer_1.Add(self.text_max[i], 0, wx.ALL|wx.ADJUST_MINSIZE, 5)

#        sizer_btn.Add(self.button_plot,0, wx.ALL|wx.ADJUST_MINSIZE, 5)
#        sizer_btn.Add(self.button_clearPlot,0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_btn.Add(self.radio,0,wx.ALL|wx.ADJUST_MINSIZE,0)
        sizer_btn.Add((200,10))
        sizer_btn.Add(self.button_setRange,0, wx.ALL|wx.ADJUST_MINSIZE, 5)


        sizer_sbs.Add(grid_sizer_1, 1, wx.EXPAND, 0)

        sizer_top.Add(self.button_Exp, 0, wx.ALL|wx.EXPAND, 2)
        sizer_top.Add(self.button_Clear, 0, wx.ALL|wx.EXPAND, 2)
        sizer_top.Add(sizer_sbs, 0, wx.ALL|wx.EXPAND, 2)
        sizer_top.Add(sizer_btn, 0, wx.ALL|wx.EXPAND, 2)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_top)


if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel = PlotPanelSimulation(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
