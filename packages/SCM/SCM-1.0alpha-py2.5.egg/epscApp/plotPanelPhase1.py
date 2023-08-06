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


class PlotPanelPhase1(wx.Panel):
    def __init__(self, plotnotebook, name):
        wx.Panel.__init__(self, plotnotebook.notebook, -1, size=wx.Size(700,700))
        self.plotnotebook = plotnotebook
        self.name = name

        self.paneChildren = {}
        self.paneChildren[self.name] = PlotPkg(self,
                                              plotinfo=plotnotebook.plotinfos[self.name],
                                              title = '',
                                              xaxis='Strain (%)',
                                              yaxis='Stress (MPa)',
                                              xrange=None)
        self.paneChildren[self.name].SetEnableGrid(True)
        self.paneChildren[self.name].SetGridColour(wx.ColorRGB(0xAAAAAA))

        self.Bind(wx.EVT_SIZE,   self.OnSize)
        self.SetSize(wx.Size(700,700))
        return

    def OnSize(self, event):
        size = self.GetSize()

        self.paneChildren[self.name].GetPanel().SetPosition(wx.Point(0,0))
        self.paneChildren[self.name].GetPanel().SetSize(size)
        self.paneChildren[self.name].GetPanel().Update()

        self.Update()
        return

    def updatePlot(self, plotname=''):
        if(plotname == ''):
            self.updatePlot(self.name)
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
            self.updatePlot(self.name)
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetEnableTitle(value)
        return

    def SetTitle(self, plotname, title):
        if(plotname == ''):
            self.updatePlot(self.name)
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetTitle(title)
        return

    def ToggleBorderRaised(self, plotname):
        if(plotname == ''):
            self.updatePlot(self.name)
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
