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
from plotPanelSimulation import PlotPanelSimulation
from SCMPanel import SCMPanel

class SimulationPanel(wx.Panel, SCMPanel):
    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.plotinfos = {}

        self.plotinfos['macro'] = {}
        self.plotinfos['macro']['model'] = {'name':'model', 'x':[], 'y':[], 'type':'line', 'color':'red', 'width':1}
        self.plotinfos['macro']['exp'] = {'name':'exp', 'x':[], 'y':[], 'type':'marker', 'color':'blue', 'width':1}

        self.paneChildren = {}
        self.paneChildren['macro']  = PlotPkg(self,
                                              plotinfo=self.plotinfos['macro'],
                                              title = 'Macro',
                                              xaxis='Strain (%)',
                                              yaxis='Stress (MPa)',
                                              xrange=None)

        self.paneChildren['simulation'] = PlotPanelSimulation(self)
        self.Bind(wx.EVT_SIZE,   self.OnSize)
        self.SetSize(wx.Size(700,800))
        return

    def setProperties(self):
        pass

    def OnSize(self, event):
        gap = 5
        size = self.GetSize()
        size -= wx.Size(gap,gap)
        size.Scale(0.5,0.5)

        self.paneChildren['macro'].GetPanel().SetPosition(wx.Point(100,0))
        self.paneChildren['macro'].GetPanel().SetSize((size.width+100,size.height-50))
        self.paneChildren['macro'].GetPanel().Update()
        self.paneChildren['simulation'].SetPosition(wx.Point(100,size.height-50))
        self.paneChildren['simulation'].SetSize((size.width+100,size.height+100))
        self.paneChildren['simulation'].Update()

        self.Update()
        return

    def updatePlot(self, plotname='', plotinfo={}):
        if(self.plotinfos.has_key(plotname)):
            self.plotinfos[plotname][plotinfo['name']] = plotinfo

        if(self.paneChildren.has_key(plotname) is False):
            return
        plotpkg = self.paneChildren[plotname]
        plotpkg.Update()
        return

    def clear(self):
        return

    def SetEnableTitle(self, plotname, value):
        if(plotname == ''):
            self.updatePlot('macro')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetEnableTitle(value)
        return

    def SetTitle(self, plotname, title):
        if(plotname == ''):
            self.updatePlot('macro')
            return
        if(self.paneChildren.has_key(plotname) is False):
            return
        self.paneChildren[plotname].SetTitle(title)
        return

    def ToggleBorderRaised(self, plotname):
        if(plotname == ''):
            self.updatePlot('macro')
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
