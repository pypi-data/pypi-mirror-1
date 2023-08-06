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
from wx import xrc
import sys
from plotPkg import PlotPkg
from plotPkgErrMonitor import PlotPkgErrMonitor
from plotPanelSimulation import PlotPanelSimulation

class PlotPanelOverview(wx.Panel):
    def __init__(self, plotnotebook):
        wx.Panel.__init__(self, plotnotebook.notebook, -1, size=wx.Size(700,700))

        self.plotnotebook = plotnotebook
        self.flagRun = True
        self.paneChildren = {}
        self.paneChildren['macro']  = PlotPkg(self,
                                              plotinfo=plotnotebook.plotinfos['macro'],
                                              title = 'Macro',
                                              xaxis='Strain (%)',
                                              yaxis='Stress (MPa)',
                                              xrange=None)
        self.paneChildren['HKL-Long'] = PlotPkg(self,
                                              plotinfo=plotnotebook.plotinfos['HKL-Long'],
                                              title = 'HKL-Long',
                                              xaxis='Strain (%)',
                                              yaxis='Stress (MPa)',
                                              xrange=None)
        self.paneChildren['HKL-Trans'] = PlotPkg(self,
                                              plotinfo=plotnotebook.plotinfos['HKL-Trans'],
                                              title = 'HKL-Trans',
                                              xaxis='Strain (%)',
                                              yaxis='Stress (MPa)',
                                              xrange=None)

        self.paneChildren['errmonitor']  = PlotPkgErrMonitor(self,
                                                             plotinfo=plotnotebook.plotinfos['errmonitor'],
                                                             title = '',
                                                             xaxis='Iteration',
                                                             yaxis='MSE')
        self.Bind(wx.EVT_SIZE,   self.OnSize)
        self.SetSize(wx.Size(700,800))
        return

    def OnSize(self, event):
        gap = 5
        size = self.GetSize()
        size -= wx.Size(gap,gap)
        size.Scale(0.5,0.5)

        self.paneChildren['HKL-Long'].GetPanel().SetPosition(wx.Point(0,0))
        self.paneChildren['HKL-Long'].GetPanel().SetSize(size)
        self.paneChildren['HKL-Long'].GetPanel().Update()

        self.paneChildren['HKL-Trans'].GetPanel().SetPosition(wx.Point(size.width+gap,0))
        self.paneChildren['HKL-Trans'].GetPanel().SetSize(size)
        self.paneChildren['HKL-Trans'].GetPanel().Update()

#        self.paneChildren['phase2'].GetPanel().SetPosition(wx.Point(size.width+gap,0))
#        self.paneChildren['phase2'].GetPanel().SetSize(size)
#        self.paneChildren['phase2'].GetPanel().Update()

        self.paneChildren['macro'].GetPanel().SetPosition(wx.Point(0,size.height+gap))
        self.paneChildren['macro'].GetPanel().SetSize(size)
        self.paneChildren['macro'].GetPanel().Update()

        self.paneChildren['errmonitor'].GetPanel().SetPosition(wx.Point(size.width+gap,size.height+gap))
        self.paneChildren['errmonitor'].GetPanel().SetSize(size)
        self.paneChildren['errmonitor'].GetPanel().Update()

        self.Update()
        return

    def updatePlot(self, plotname=''):
        if(plotname == ''):
            self.updatePlot('HKL-Long')
            self.updatePlot('HKL-Trans')
#            self.updatePlot('phase2')
            self.updatePlot('macro')
            self.updatePlot('errmonitor')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        plotpkg = self.paneChildren[plotname]
        plotpkg.Update()
        return

    def clear(self):
        return

    def SetEnableTitle(self, plotname, value):
        if(plotname == ''):
            self.updatePlot('HKL-Long')
            self.updatePlot('HKL-Trans')
#            self.updatePlot('phase2')
            self.updatePlot('macro')
            self.updatePlot('errmonitor')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetEnableTitle(value)
        return

    def SetTitle(self, plotname, title):
        if(plotname == ''):
            self.updatePlot('HKL-Long')
            self.updatePlot('HKL-Trans')
#            self.updatePlot('phase2')
            self.updatePlot('macro')
            self.updatePlot('errmonitor')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetTitle(title)
        return

    def ToggleBorderRaised(self, plotname):
        if(plotname == ''):
            self.updatePlot('HKL-Long')
            self.updatePlot('HKL-Trans')
#            self.updatePlot('phase2')
            self.updatePlot('macro')
            self.updatePlot('errmonitor')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].ToggleBorderRaised()
        return

if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel = PlotMainPanel(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
