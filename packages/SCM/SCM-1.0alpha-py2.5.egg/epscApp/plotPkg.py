import wx
from wx import xrc
from wx.lib.plot import PlotCanvas
import wx.lib.plot as plot
import epscComp.config

class PlotPkg:
    def __init__(self, frame, plotinfo, pos=wx.Point(0,0), size=wx.Size(100,100),
                 title = '', xaxis='strain', yaxis = 'stress (MPa)', xrange=None, yrange=None,
                 showToggleProperty=True, plotpriori=[]):
        self.frame = frame
        self.plotinfo = plotinfo # copy the reference of plotinfo.
        self.title = title
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.xrange = xrange
        self.yrange = yrange
        self.panel = xrc.XmlResource(epscComp.config.dirImages + 'panels.xrc').LoadPanel(frame, 'Plot')
        self.panel.SetPosition(pos)
        self.panel.SetSize(size)
        temppanel = xrc.XRCCTRL(self.panel, 'Plot')
        pos  = temppanel.GetPosition()
        size = temppanel.GetSize()
        #temppanel.Hide()
        self.CreateCanvas(pos, size)
        self.panel.Bind(wx.EVT_SIZE,   self.OnPanelSize)
        self.panel.Bind(wx.EVT_BUTTON, self.OnImport, id=xrc.XRCID('Import'))
        self.panel.Bind(wx.EVT_BUTTON, self.OnClear,  id=xrc.XRCID('Clear'))
        self.panel.Bind(wx.EVT_BUTTON, self.OnToggleProperty,  id=xrc.XRCID('ToggleProperty'))
        self.panel.Bind(wx.EVT_BUTTON, self.OnOK,  id=xrc.XRCID('OK'))
        self.panel.Bind(wx.EVT_BUTTON, self.OnReset,  id=xrc.XRCID('Reset'))
        #self.OnToggleProperty(None)
        self.ShowToggleProperty(showToggleProperty)
        self.OnPanelSize(None)
        self.DrawCanvas()
        self.title = ""
        self.setXRange(xrange)
        self.setYRange(yrange)
        return

    def setXRange(self, xrange):
        self.xrange = xrange
        if(xrange != None):
            if(xrange[0] != None): self.getControl('XMin').SetValue(str(xrange[0]))
            else:                  self.getControl('XMin').SetValue('')
            if(xrange[1] != None): self.getControl('XMax').SetValue(str(xrange[1]))
            else:                  self.getControl('XMax').SetValue('')
        else:
            self.getControl('XMin').SetValue('')
            self.getControl('XMax').SetValue('')
        return

    def setYRange(self, yrange):
        self.yrange = yrange
        if(yrange != None):
            if(yrange[0] != None): self.getControl('YMin').SetValue(str(yrange[0]))
            else:                  self.getControl('YMin').SetValue('')
            if(yrange[1] != None): self.getControl('YMax').SetValue(str(yrange[1]))
            else:                  self.getControl('YMax').SetValue('')
        else:
            self.getControl('YMin').SetValue('')
            self.getControl('YMax').SetValue('')
        return

    def OnOK(self, evt):
        xmin = self.getControl('XMin').GetValue()
        xmax = self.getControl('XMax').GetValue()
        xrange = None
        if((xmin != '') or (xmax != '')):
            if(xmin != ''): xmin = float(xmin)
            else:           xmin = None
            if(xmax != ''): xmax = float(xmax)
            else:           xmax = None
            if((xmin != None) and (xmax != None) and (xmin >= xmax)):
                msg  = 'xmin should be smaller than xmax'
                dlg = wx.MessageDialog(self.frame, msg, 'Error', wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            xrange = (xmin, xmax)
        self.setXRange(xrange)

        ymin = self.getControl('YMin').GetValue()
        ymax = self.getControl('YMax').GetValue()
        yrange = None
        if((ymin != '') or (ymax != '')):
            if(ymin != ''): ymin = float(ymin)
            else:           ymin = None
            if(ymax != ''): ymax = float(ymax)
            else:           ymax = None
            if((ymin != None) and (ymax != None) and (ymin >= ymax)):
                msg  = 'ymin should be smaller than ymax'
                dlg = wx.MessageDialog(self.frame, msg, 'Error', wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            yrange = (ymin, ymax)
        self.setYRange(yrange)

        self.DrawCanvas()
        return

    def OnReset(self, event):
        self.setXRange(None)
        self.setYRange(None)
        self.DrawCanvas()
        return

    def getControl(self, ctrlname):
        ctrl = xrc.XRCCTRL(self.panel, ctrlname)
        return ctrl

    def OnToggleProperty(self, event):
        if(self.getControl('Property').IsShown() == False):
            self.getControl('ToggleProperty').SetLabel("<")
            self.getControl('Property').Show()
        else:
            self.getControl('ToggleProperty').SetLabel(">")
            self.getControl('Property').Hide()
        self.OnPanelSize(None)
        return

    def ShowToggleProperty(self, show):
        if(show == True):
            self.getControl('ToggleProperty').Show()
        else:
            self.getControl('ToggleProperty').Hide()
            self.getControl('Property').Hide()
        return

    def CreateCanvas(self, pos, size):
        class MyPlotCanvas(wx.lib.plot.PlotCanvas):
            def __init__(self, parent, plotpkg, id=wx.ID_ANY, pos=wx.DefaultPosition,
                        size=wx.DefaultSize, style=0, name="plotCanvas"):
                wx.lib.plot.PlotCanvas.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)
                self.plotpkg = plotpkg
                #self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
                return
            def OnMouseRightDown(self, event):
                return
            def OnContextMenu(self, event):
                self.plotpkg.OnCanvasContextMenu(event)
                return
        self.canvas = MyPlotCanvas(self.panel, self, pos=pos, size=size)
        self.canvas.SetPosition(pos)
        self.canvas.SetSize(size)
        self.canvas.SetEnableLegend(True)
        return

    def GetPanel(self):
        return self.panel

    def getControl(self, ctrlname):
        ctrl = xrc.XRCCTRL(self.panel, ctrlname)
        return ctrl

    def OnPanelSize(self, event):
        gap = 0
        if(self.getControl('Property').IsShown()):
            gap = self.getControl('Property').GetSize().height
        size = self.panel.GetSize()
        size.height -= gap
        pos = wx.Point(0,gap)
        self.canvas.SetPosition(pos)
        self.canvas.SetSize(size)
        self.canvas.Update();

        #xrc.XRCCTRL(self.panel, 'Clear').Refresh()
        #xrc.XRCCTRL(self.panel, 'Import').Refresh()
        self.panel.Update();
        if(event is not None):
            event.Skip()
        self.getControl('ToggleProperty').Refresh()
        self.getControl('Property').Refresh()
        return

    def OnCanvasContextMenu(self, event):
        # Prepare popup menu IDs
        if not hasattr(self, "idExport"):
            self.idExport = wx.NewId()
            self.idImport = wx.NewId()
            self.idClear  = wx.NewId()
            self.canvas.Bind(wx.EVT_MENU, self.OnExport, id=self.idExport)
            self.canvas.Bind(wx.EVT_MENU, self.OnImport, id=self.idImport)
            self.canvas.Bind(wx.EVT_MENU, self.OnClear,  id=self.idClear)
        # make a popup menu
        menu = wx.Menu()
        menu.Append(self.idClear,  "Clear")
        menu.Append(self.idImport, "Import")
        menu.Append(self.idExport, "Export")
        self.canvas.PopupMenu(menu)
        menu.Destroy()
        return

    def OnExport(self, event):
        return

    def OnImport(self, evt):
        return

    def OnClear(self, evt):
        #self.DrawCanvas()
        #self.frame.OnClear(self)
        return

    def PlotOpen(self):
        return

    def makePlotData(self,X,Y):
        output = []
        l = min(len(X),len(Y))
        for i in range(l):
            output.append((X[i], Y[i]))
        return output

    def DrawCanvas(self):
        #http://www.daniweb.com/forums/thread70736.html
        # define inner-function to make strain percentile
        def getFrom(info, name, defaultvalue):
            if(info.has_key(name)):
                return info[name]
            return defaultvalue
        # draw dataImported
        drawinfos = []
        checkDrawEmpty = True
        xlist = []
        ylist = []
        for infoname in self.plotinfo:
            info = self.plotinfo[infoname]
            if(len(info['x']) != 0):
                checkDrawEmpty = False
            else:
                continue
            # prepare range setting
            if(len(info['x']) >= 1):
                xlist = xlist + info['x']
                ylist = ylist + info['y']
            # prepare drawing
            drawdata = self.makePlotData(info['x'], info['y'])
            legend=info['name']
            colour=getFrom(info, 'color', 'black')
            width=getFrom(info, 'width', 1)
            type = getFrom(info,'type','marker')
            if(type == 'marker'):
                marker = getFrom(info, 'marker', 'circle')
                size = getFrom(info, 'size', 1)
                fillstyle = getFrom(info, 'fillstyle', wx.SOLID)
                drawinfo = plot.PolyMarker(drawdata, legend=legend, colour=colour, width=width, size=size, marker=marker, fillstyle=fillstyle)
            elif(type == 'line'):
                drawinfo = plot.PolyLine  (drawdata, legend=legend, colour=colour, width=width)
            else: pass
            drawinfos.append(drawinfo)
            pass
        if(checkDrawEmpty):
            self.DrawCanvasEmpty()
            return
        gc = plot.PlotGraphics(drawinfos, self.title, self.xaxis, self.yaxis)
        if(self.title != None):
            gc.setTitle(self.title)

        xrange = self.xrange
        yrange = self.yrange
        if((self.xrange != None) and (self.xrange[0] == None)): xrange = (min(xlist), xrange[1] )
        if((self.xrange != None) and (self.xrange[1] == None)): xrange = (xrange[0],  max(xlist))
        if((self.xrange != None) and (xrange[0] >= xrange[1])): xrange = (xrange[0],xrange[0]+1)
        if((self.yrange != None) and (self.yrange[0] == None)): yrange = (min(ylist), yrange[1] )
        if((self.yrange != None) and (self.yrange[1] == None)): yrange = (yrange[0],  max(ylist))
        if((self.yrange != None) and (yrange[0] >= yrange[1])): yrange = (yrange[0],yrange[0]+1)
        if((xrange != None) and (len(xrange) > 0)):
            if(yrange == None):
                if(xrange == None):
                    # (x none), (y none)
                    yrange = (min(ylist), max(ylist))
                    dyrange = yrange[1] - yrange[0]
                    yrange = (yrange[0] - 0.1*dyrange, yrange[1] + 0.1*dyrange)
                else:
                    # (x not none), (y none)
                    for i in range(len(xlist)):
                        x = xlist[i]
                        y = ylist[i]
                        if((xrange[0] <= x) and (x <=xrange[1])):
                            if(yrange == None):
                                yrange = (y,y)
                            else:
                                yrange = (min(yrange[0],y), max(yrange[1],y))
                    if(yrange != None):
                        dyrange = yrange[1] - yrange[0]
                        yrange = (yrange[0] - 0.1*dyrange, yrange[1] + 0.1*dyrange)
            else:
                # (x not none), (y not none)
                pass

        self.canvas.Draw(graphics=gc, xAxis=xrange, yAxis=yrange, dc=None)
        self.getControl('ToggleProperty').Refresh()
        self.getControl('Property').Refresh()
        return

    def DrawCanvasEmpty(self):
        # draw empty
        data = [(1,1)]
        points = plot.PolyMarker(data, colour='white', width=0)
        gc = plot.PlotGraphics([points], self.title, self.xaxis, self.yaxis)
        self.canvas.Draw(gc, xAxis= (0,10), yAxis= (0,1000))
        self.getControl('ToggleProperty').Refresh()
        self.getControl('Property').Refresh()
        return

    def Update(self):
        self.DrawCanvas()
        self.canvas.Update()
        self.getControl('ToggleProperty').Update()
        self.getControl('Property').Update()
        return

    def UpdateProperty(self, event):
        if(event == None):
            self.getControl('XRange').SetValue(self.xrange)
            self.getControl('YRange').SetValue(self.yrange)
        else:
            pass
        return

    def SetEnableTitle(self, value):
        self.canvas.SetEnableTitle(value)
        return

    def SetTitle(self, title):
        self.title = title
        return

    def ToggleBorderRaised(self):
        self.canvas.ToggleWindowStyle(wx.BORDER_RAISED)
        return

    def SetXRange(self, xrange):
        self.xrange = xrange
        return

    def SetYRange(self, yrange):
        self.yrange = yrange
        return


    ##############################################################
    # grid control
    def GetEnableGrid(self):
        return self.canvas.GetEnableGrid()
    def GetGridColour(self):
        return self.canvas.GetGridColour();
    def SetEnableGrid(self, value):
        self.canvas.SetEnableGrid(value);
        return
    def SetGridColour(self, colour):
        self.canvas.SetGridColour(colour);
        return


if __name__ == '__main__':
    import frame
    app = frame.MyApp(False)
    app.MainLoop()
