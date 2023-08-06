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
from SCMPanel import SCMPanel

class TexturePanel(wx.Panel, SCMPanel):

    """ Panel to get file of texture data.
    """

    def __init__(self, *args, **kwds):
        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)
        self.controller = self.Parent.Parent.controller
        self.treePanel = self.Parent.Parent.treePanel
        self.kind = self.Parent.Parent.kind

        self.label_top = wx.StaticText(self, -1, "     Select the texture file.")

        self.radio_random10 = wx.RadioButton(self, -1, "")
        self.label_random10  = wx.StaticText(self, -1,"Random generated grains (1000 grains)",size=(300,20))

        self.radio_random2916 = wx.RadioButton(self, -1, "")
        self.label_random2916 = wx.StaticText(self, -1,"Random 10 degree mesh(2916 grains)", size=(300,20))

#        self.radio_random5 = wx.RadioButton(self, -1, "")
#        self.label_random5 = wx.StaticText(self, -1,"Random. 5 degree mesh (23328 grains)", size=(300,20))

        self.radio_mg1944 = wx.RadioButton(self, -1, "")
        self.label_mg1944 = wx.StaticText(self, -1,"Magnesium extrusion texture (1944 grains)", size=(300,20))

#        self.radio_mg15548 = wx.RadioButton(self, -1, "")
#        self.label_mg15548 = wx.StaticText(self, -1,"Magnesium extrusion texture (15548 grains)", size=(300,20))

        self.radio_custom = wx.RadioButton(self, -1, "")
        self.label_custom  = wx.StaticText(self, -1,"Custom texture file",size=(300,20))

        self.okBtn = wx.Button(self, -1, "OK")
        self.cancelBtn = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_BUTTON, self.OnOK, self.okBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancelBtn)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRandom10, self.radio_random10)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRandom2916, self.radio_random2916)
#        self.Bind(wx.EVT_RADIOBUTTON, self.OnRandom5, self.radio_random5)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnMg1944, self.radio_mg1944)
#        self.Bind(wx.EVT_RADIOBUTTON, self.OnMg15548, self.radio_mg15548)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnCustom, self.radio_custom)
        self.__do_layout()
        self.__setProperties()

    def __setProperties(self):
        if self.controller.epscData.textureFileNum == 1 :
            self.radio_random10.SetValue(True)
        elif self.controller.epscData.textureFileNum == 2 :
            self.radio_random2916.SetValue(True)
        elif self.controller.epscData.textureFileNum == 3 :
            self.radio_random5.SetValue(True)
        elif self.controller.epscData.textureFileNum == 4:
            self.radio_mg1944.SetValue(True)
        elif self.controller.epscData.textureFileNum == 5:
            self.radio_mg15548.SetValue(True)
        elif self.controller.epscData.textureFileNum == 0 :
            self.radio_custom.SetValue(True)

    def dataPhaseNum(self):
        return({"Phase1":"1","2Phase1":"1", "2Phase2":"2"})

    def showData(self):
        if self.controller.epscData.textureFileNum == 1 :
            self.radio_random10.SetValue(True)
        elif self.controller.epscData.textureFileNum == 2 :
            self.radio_random2916.SetValue(True)
#        elif self.controller.epscData.textureFileNum ==2 :
#            self.radio_random5.SetValue(True)
        elif self.controller.epscData.textureFileNum == 4:
            self.radio_mg1944.SetValue(True)
        elif self.controller.epscData.textureFileNum == 5:
            self.radio_mg15548.SetValue(True)
        elif self.controller.epscData.textureFileNum == 0:
            self.radio_custom.SetValue(True)

    def OnRandom10(self, event):
        self.controller.epscData.textureFileNum = 1

    def OnRandom2916(self, event):
        self.controller.epscData.textureFileNum = 2

    def OnRandom5(self, event):
        self.controller.epscData.textureFileNum = 3

    def OnMg1944(self, event):
        self.controller.epscData.textureFileNum = 4

    def OnMg15548(self, event):
        self.controller.epscData.textureFileNum = 5

    def OnCustom(self, event):
        self.controller.epscData.textureFileNum = 0

    def OnOK(self,event):
        if os.name == 'nt' :
            strCopy = "copy "
            os.system(strCopy + '"' + epscComp.config.dirEpscCore + epscComp.config.file_Texture[self.controller.epscData.textureFileNum] \
                      + '" "' + epscComp.config.dirEpscCore + "TEXTURE_" + self.dataPhaseNum()[self.kind] + '.tex"')

        else :
            strCopy = "cp "
            os.system(strCopy + epscComp.config.dirEpscCore + epscComp.config.file_Texture[self.controller.epscData.textureFileNum] \
                      + " " + epscComp.config.dirEpscCore + "TEXTURE_" + self.dataPhaseNum()[self.kind] + ".tex")

        self.controller.epscData.isAltered = True
        self.controller.epscData.textureDataSaved = True
        self.Parent.SetSelection(4)

        self.treePanel.turnOnNode(self.controller.epscData.phaseNum, 3)

    def OnCancel(self, event):

            self.radio_random10.SetValue(True)
            self.radio_random2916.SetValue(False)
            self.radio_mg1944.SetValue(False)

            self.radio_custom.SetValue(False)
            self.controller.epscData.textureFileNum = 1
            self.controller.epscData.textureDataSaved = False
            self.treePanel.turnOffNode(self.controller.epscData.phaseNum, 3)

    def __do_layout(self):
        topBSizer = wx.BoxSizer(wx.VERTICAL)

        dataFGSizer_1 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        dataFGSizer_1.Add(self.radio_random10, 0, wx.ALL, 5)
        dataFGSizer_1.Add(self.label_random10, 0, wx.ALL, 5)

        dataFGSizer = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        dataFGSizer.Add(self.radio_random2916, 0, wx.ALL, 5)
        dataFGSizer.Add(self.label_random2916, 0, wx.ALL, 5)

#        dataFGSizer_2 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
#        dataFGSizer_2.Add(self.radio_random5, 0, wx.ALL, 5)
#        dataFGSizer_2.Add(self.label_random5, 0, wx.ALL, 5)

        dataFGSizer_3 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        dataFGSizer_3.Add(self.radio_mg1944, 0, wx.ALL, 5)
        dataFGSizer_3.Add(self.label_mg1944, 0, wx.ALL, 5)

#        dataFGSizer_4 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
#        dataFGSizer_4.Add(self.radio_mg15548, 0, wx.ALL, 5)
#        dataFGSizer_4.Add(self.label_mg15548, 0, wx.ALL, 5)

        dataFGSizer_5 = wx.FlexGridSizer(cols=2, hgap=5, vgap=5)
        dataFGSizer_5.Add(self.radio_custom, 0, wx.ALL, 5)
        dataFGSizer_5.Add(self.label_custom, 0, wx.ALL, 5)

        btnGSizer = wx.GridSizer(1, 2, 0, 0)
        btnGSizer.Add(self.okBtn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnGSizer.Add(self.cancelBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        topBSizer.Add((20,20))
        topBSizer.Add(self.label_top, 0, wx.EXPAND, 0)
        topBSizer.Add((20,20))
        topBSizer.Add(dataFGSizer_1, 0, wx.EXPAND, 0)
        topBSizer.Add(dataFGSizer, 0, wx.EXPAND, 0)
#        topBSizer.Add(dataFGSizer_2, 0, wx.EXPAND, 0)
        topBSizer.Add(dataFGSizer_3, 0, wx.EXPAND, 0)
#        topBSizer.Add(dataFGSizer_4, 0, wx.EXPAND, 0)
        topBSizer.Add(dataFGSizer_5, 0, wx.EXPAND, 0)
        topBSizer.Add((20,20))

        topBSizer.Add(btnGSizer, 0, wx.EXPAND, 0)

        self.SetAutoLayout(True)
        self.SetSizer(topBSizer)

if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1,'dynamic test',size=(800,900))
    panel=TexturePanel(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()