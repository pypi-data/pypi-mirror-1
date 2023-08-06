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
from SCMPanel import SCMPanel

class PlotPanel(wx.Panel, SCMPanel):
    """ panel for plotting
    """
    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.sizer_4_staticbox = wx.StaticBox(self, -1, "Neutron")
        self.sizer_3_staticbox = wx.StaticBox(self, -1, "Macro")
        self.macroModelCheck = wx.CheckBox(self, -1, "Model Result")
        self.macroExpCheck = wx.CheckBox(self, -1, "Experiment Data")
        self.neutronModelCheck = wx.CheckBox(self, -1, "Model Result")
        self.neutronExpCheck = wx.CheckBox(self, -1, "Experiment Data")
        self.macroModelCheck.SetValue(True)
        self.macroExpCheck.SetValue(True)
        self.neutronModelCheck.SetValue(True)
        self.neutronExpCheck.SetValue(True)

        self.static_line_1 = wx.StaticLine(self, -1)
        self.plotButton = wx.Button(self, -1, "Plot")
        self.resetButton = wx.Button(self, -1, "Reset")
        self.gauge = wx.Gauge(self, -1, 50, (110, 95), (210, 20))
#        self.gauge.Enable()
#        self.gauge.SetValue(11000)
#        self.gauge.Pulse()
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onPlot, self.plotButton)
        self.Bind(wx.EVT_BUTTON, self.onReset, self.resetButton)


    def __set_properties(self):
        # begin wxGlade: PlotPanel.__set_properties
        # end wxGlade
        #self.setToolTips(toolTips)
        pass

    def __do_layout(self):
        # begin wxGlade: PlotPanel.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
        sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
        sizer_3.Add(self.macroModelCheck, 1, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_3.Add(self.macroExpCheck, 1, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 10)
        sizer_4.Add(self.neutronModelCheck, 1, wx.LEFT|wx.ADJUST_MINSIZE|wx.EXPAND, 10)
        sizer_4.Add(self.neutronExpCheck, 1, wx.LEFT|wx.ADJUST_MINSIZE|wx.EXPAND, 10)
        sizer_1.Add(sizer_4, 1, wx.EXPAND, 10)
        sizer_1.Add(sizer_6, 1, wx.EXPAND, 0)
        sizer_1.Add(self.static_line_1, 0, wx.BOTTOM|wx.EXPAND, 5)
        sizer_2.Add(self.plotButton, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_2.Add(self.resetButton, 0, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_1.Add(self.gauge, 0, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        # end wxGlade

    # USER CONFIGURATION CODE #################################################

    def enableWidgets(self, on=True):
        """Enable or disable the widgets."""
        self.macroDataList.Enable(on)
        self.neutronDataList.Enable(on)
        self.resetButton.Enable(on)
        self.plotButton.Enable(on)
        return


    def onPlot(self, event):
        """Plot some stuff."""

#        self.Parent.showPanel("plot")
        self.Parent.clearPlots()
        self.Parent.OnPlot(None)
        if self.macroModelCheck.GetValue() == True :
            if self.controller.epscData.flagRun == False :
                msg = "You should run the model to plot!"
                dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if self.macroExpCheck.GetValue() == True :
                self.macro = 2
            else :
                self.macro = 1
            self.controller.plotEngine.plotMacroTop(self.Parent,self.macro)
        else :
            if self.macroExpCheck.GetValue() == True :
                self.macro = 3
                if self.controller.epscData.expData.checkFlagOn("expData") :
                    self.controller.plotEngine.plotMacroTop(self.Parent,self.macro)
                else :
                    msg = "You should input the experimental files to plot!"
                    dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            else:
                self.macro = 0

        if self.neutronModelCheck.GetValue() == True :
            if self.controller.epscData.flagRun == False :
                    msg = "You should run the model to plot!"
                    dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            if self.neutronExpCheck.GetValue() == True :
                self.neutron = 2
            else :
                self.neutron = 1

            self.controller.plotEngine.plotNeutronTop(self.Parent,self.neutron)
        else :
            if self.neutronExpCheck.GetValue() == True:
                self.neutron = 3
                if self.controller.epscData.expData.checkFlagOn("expData"):
                    if self.controller.epscData.diffractionDataSaved :
                        self.controller.plotEngine.plotNeutronTop(self.Parent,self.neutron)
                    else :
                        msg = "You should input the diffraction data to plot!"
                        dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return
                else :
                    msg = "You should input the experimental files to plot!"
                    dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            else:
                self.neutron = 0


    def onReset(self, event): # wxGlade: PlotPanel.<event_handler>
        """Reset everything."""
        self.macroExpCheck.SetValue(False)
        self.macroModelCheck.SetValue(False)
        self.neutronExpCheck.SetValue(False)
        self.neutronModelCheck.SetValue(False)
        return

    def _check(self, event):
        try:
            self._plot(None)
            self.plotButton.Enable()
        except ControlConfigError:
            self.plotButton.Disable()

    def disableButton(self):
        self.plotButton.Enable(False)

    def enableButton(self):
        self.plotButton.Enable(True)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel=PlotPanel(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()