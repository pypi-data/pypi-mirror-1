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
from plotPkgErrMonitor import PlotPkgErrMonitor


class PlotPanelErrMonitor(wx.Panel):
    def __init__(self, plotnotebook):
        wx.Panel.__init__(self, plotnotebook.notebook, -1, size=wx.Size(700,700))

        self.plotnotebook = plotnotebook

        self.paneChildren = {}
        self.paneChildren['errmonitor']  = PlotPkgErrMonitor(self,
                                                             plotinfo=plotnotebook.plotinfos['errmonitor'],
                                                             title = '',
                                                             xaxis='Iteration',
                                                             yaxis='MSE')
        self.paneChildren['errmonitor'].SetEnableGrid(True)
        self.paneChildren['errmonitor'].SetGridColour(wx.ColorRGB(0xAAAAAA))

        self.Bind(wx.EVT_SIZE,   self.OnSize)
        self.SetSize(wx.Size(700,700))
        return

    def OnSize(self, event):
        size = self.GetSize()

        self.paneChildren['errmonitor'].GetPanel().SetPosition(wx.Point(0,0))
        self.paneChildren['errmonitor'].GetPanel().SetSize(size)
        self.paneChildren['errmonitor'].GetPanel().Update()

        self.Update()
        return

    def updatePlot(self, plotname=''):
        if(plotname == ''):
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
            self.updatePlot('errmonitor')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetEnableTitle(value)
        return

    def SetTitle(self, plotname, title):
        if(plotname == ''):
            self.updatePlot('errmonitor')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetTitle(title)
        return

    def ToggleBorderRaised(self, plotname):
        if(plotname == ''):
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
