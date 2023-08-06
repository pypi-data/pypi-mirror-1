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
import plotPanelOverview
import plotPanelMacro
import plotPanelPhase1
#import plotPanelPhase2
import plotPanelErrMonitor
import plotPanelSimulation

class PlotNotebook(wx.Panel, SCMPanel):
    def __init__(self, *args, **kwds):

        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.notebook = wx.Notebook(self, -1, style=0)

        self.plotinfos = {}
        self.plotinfos['HKL-Long'] = {}
        self.plotinfos['HKL-Trans'] = {}

#        self.plotinfos['phase2'] = {}
        self.plotinfos['macro'] = {}
        self.plotinfos['macro']['model'] = {'name':'model', 'x':[], 'y':[], 'type':'line', 'color':'red', 'width':1}
        self.plotinfos['macro']['exp'] = {'name':'exp', 'x':[], 'y':[], 'type':'marker', 'color':'blue', 'width':1}

        self.plotinfos['errmonitor'] = {}
        self.plotinfos['errmonitor']['MSE'] = {'name':'MSE', 'x':[0], 'y':[0], 'type':'line', 'color':'red', 'width':1}

        self.panes = {}
        self.panes['overview']   = plotPanelOverview.PlotPanelOverview(self)
        self.panes['HKL-Long']     = plotPanelPhase1.PlotPanelPhase1(self, 'HKL-Long')
        self.panes['HKL-Trans']     = plotPanelPhase1.PlotPanelPhase1(self, 'HKL-Trans')
#        self.panes['phase2']     = plotPanelPhase2.PlotPanelPhase2(self)
        self.panes['macro']      = plotPanelMacro.PlotPanelMacro(self)
        self.panes['errmonitor'] = plotPanelErrMonitor.PlotPanelErrMonitor(self)
        #self.panes['simulation'] = plotPanelSimulation.PlotPanelSimulation(self.notebook)

        self.__set_properties()
        self.__do_layout()
        self.panes['overview'].updatePlot()
        # end wxGlade
        return

    def setProperties(self):
        pass

    def __set_properties(self):
        # begin wxGlade: PlotNotebook.__set_properties
        self.notebook.SetMinSize((731, 576))
        pass
        # end wxGlade
        return

    def __do_layout(self):
        # begin wxGlade: PlotNotebook.__do_layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.notebook.AddPage(self.panes['overview'], 'Overview')
        self.notebook.AddPage(self.panes['HKL-Long'], 'Phase 1 - HKL-Long')
        self.notebook.AddPage(self.panes['HKL-Trans'], 'Phase 1 - HKL-Trans')
#        self.notebook.AddPage(self.panes['phase2'], 'Phase 2 - Matrix')
        self.notebook.AddPage(self.panes['macro'], 'Macro')

#        self.notebook.AddPage(self.panes['simulation'], 'Simulation')
        self.notebook.AddPage(self.panes['errmonitor'], 'MSE(Mean Square Error)')
        sizer.Add(self.notebook, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        #sizer.Fit(self)
        sizer.SetSizeHints(self)
        # end wxGlade
        return


    def updatePlot(self, plotname='', plotinfo={}):
        if(self.plotinfos.has_key(plotname)):
            self.plotinfos[plotname][plotinfo['name']] = plotinfo
        self.panes['overview'].updatePlot(plotname);
        self.panes['HKL-Long'].updatePlot(plotname);
        self.panes['HKL-Trans'].updatePlot(plotname);
#        self.panes['phase2'].updatePlot(plotname);
        self.panes['macro'].updatePlot(plotname);
        self.panes['errmonitor'].updatePlot(plotname);
        return

    def clearPlot(self, plotname=''):
        if(self.plotinfos.has_key(plotname)):
            self.plotinfos[plotname].clear()
        self.panes['overview'].updatePlot(plotname);
        self.panes['HKL-Long'].updatePlot(plotname);
        self.panes['HKL-Trans'].updatePlot(plotname);
#        self.panes['phase2'].updatePlot(plotname);
        self.panes['macro'].updatePlot(plotname);
        self.panes['errmonitor'].updatePlot(plotname);
        return

    def addError(self, error):
        if not self.plotinfos['errmonitor'].has_key('MSE') :
            self.plotinfos['errmonitor']['MSE'] = {'name':'MSE', 'x':[0], 'y':[0], 'type':'line', 'color':'red', 'width':1}
        num = len(self.plotinfos['errmonitor']['MSE']['x'])
        self.plotinfos['errmonitor']['MSE']['x'].append(num+1)
        self.plotinfos['errmonitor']['MSE']['y'].append(error)
        self.panes['overview'].updatePlot('errmonitor');
        self.panes['errmonitor'].updatePlot('errmonitor');
        return

    def clearError(self):
        self.plotinfos['errmonitor']['MSE'] = {'name':'MSE', 'x':[], 'y':[], 'type':'line', 'color':'red', 'width':1}
        self.panes['overview'].updatePlot('errmonitor');
        self.panes['errmonitor'].updatePlot('errmonitor');
        return


    def SetEnableTitle(self, plotname, value):
        self.panes['overview'].SetEnableTitle(plotname, value);
        self.panes['HKL-Long'].SetEnableTitle(plotname, value);
        self.panes['HKL-Trans'].SetEnableTitle(plotname, value);
#        self.panes['phase2'].SetEnableTitle(plotname, value);
        self.panes['macro'].SetEnableTitle(plotname, value);
        self.panes['errmonitor'].SetEnableTitle(plotname, value);
        return

    def SetTitle(self, plotname, title):
        self.panes['overview'].SetTitle(plotname, title);
        self.panes['HKL-Long'].SetTitle(plotname, title);
        self.panes['HKL-Trans'].SetTitle(plotname, title);
#        self.panes['phase2'].SetTitle(plotname, title);
        self.panes['macro'].SetTitle(plotname, title);
        self.panes['errmonitor'].SetTitle(plotname, title);
        return

    def ToggleBorderRaised(self, plotname):
        self.panes['overview'].ToggleBorderRaised(plotname);
        self.panes['HKL-Long'].ToggleBorderRaised(plotname);
        self.panes['HKL-Trans'].ToggleBorderRaised(plotname);
#        self.panes['phase2'].ToggleBorderRaised(plotname);
        self.panes['macro'].ToggleBorderRaised(plotname);
        self.panes['errmonitor'].ToggleBorderRaised(plotname);
        return

# end of class PlotNotebook


if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'OPT Panel')
    panel=PlotNotebook(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
