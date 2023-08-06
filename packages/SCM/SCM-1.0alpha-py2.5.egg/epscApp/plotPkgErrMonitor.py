import wx
from wx.lib.plot import PlotCanvas
from plotPkg import PlotPkg
import wx.lib.plot as plot

class PlotPkgErrMonitor(PlotPkg):
    def __init__(self, frame, plotinfo, pos=wx.Point(0,0), size=wx.Size(100,100), title = '', xaxis='Iteration', yaxis = 'MSE'):
        PlotPkg.__init__(self, frame, plotinfo, pos, size, title, xaxis, yaxis, xrange=None, yrange=None)
        return

    def OnClear(self, evt):
        #self.DrawCanvas()
        #self.frame.OnClear(self)
        return

    def DrawCanvas(self):
        #http://www.daniweb.com/forums/thread70736.html
        if(len(self.plotinfo) == 0):
            PlotPkg.DrawCanvas(self)
            return
        # define inner-function to make strain percentile
        def getFrom(info, name, defaultvalue):
            if(info.has_key(name)):
                return info[name]
            return defaultvalue
        # draw dataImported
        drawinfos = []
        maxError = 0
        countIter = 10
        for infoname in self.plotinfo:
            info = self.plotinfo[infoname]
            #collect plotting info
            drawdata = self.makePlotData(info['x'], info['y'])
            legend=info['name']
            colour=getFrom(info, 'color', 'black')
            width=getFrom(info, 'width', 1)
            type = getFrom(info,'type','marker')
            if(len(drawdata) == 0):
                self.DrawCanvasEmpty()
                return
            if(len(drawdata) == 1):
                type = 'marker'
            if(type == 'marker'):   drawinfo = plot.PolyMarker(drawdata, legend=legend, colour=colour, width=width)
            elif(type == 'line'): drawinfo = plot.PolyLine  (drawdata, legend=legend, colour=colour, width=width)
            drawinfos.append(drawinfo)
            # update iteration count and max error
            countIter = max(countIter, len(drawdata))
            for (x,y) in drawdata:
                maxError = max(maxError, y)
        gc = plot.PlotGraphics(drawinfos, self.title, self.xaxis, self.yaxis)
        self.canvas.Draw(graphics=gc, xAxis=(0,countIter), yAxis=(0,maxError*1.2), dc=None)
        return

    def DrawCanvasEmpty(self):
        # draw empty
        data = [(0,0)]
        points = plot.PolyLine(data, colour='white', width=0)
        gc = plot.PlotGraphics([points], self.title, self.xaxis, self.yaxis)
        self.canvas.Draw(gc, xAxis= (0,10), yAxis= (0,1))
        return


if __name__ == '__main__':
    import Frame
    app = Frame.MyApp(False)
    app.MainLoop()
