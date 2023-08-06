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

class OptAlgorithm(wx.Panel, SCMPanel):
    """
        Panel for choice of optimization algorithm
        ==> leastsq, fmin, bounded-fmin
    """
    def __init__(self,*args, **kwds):

        SCMPanel.__init__(self, *args, **kwds)
        wx.Panel.__init__(self, *args, **kwds)

        self.selectedAlgorithm = 0
#        self.sizer_criteria_staticbox = wx.StaticBox(self, -1, "Criteria")
        self.radio_box_algorithm = wx.RadioBox(self, -1, "Algorithm", choices=["leastsq(Levenberg-Marquardt)", "fmin(Simplex)", "boxmin(Constrained Simplex)", "fmin-mystic", "Differential Evolution"], majorDimension=4, style=wx.RA_SPECIFY_COLS)
#        self.label_1 = wx.StaticText(self, -1, "func (cost function):")
#        self.text_ctrl_1 = wx.TextCtrl(self, -1, "default")
#        self.label_4 = wx.StaticText(self, -1, "maxfunc (maximum function evaluation):")
#        self.text_ctrl_4 = wx.TextCtrl(self, -1, "100")
#        self.label_2 = wx.StaticText(self, -1, "xtol (x tolerance):")
#        self.text_ctrl_2 = wx.TextCtrl(self, -1, "1.49e-8")
#        self.label_5 = wx.StaticText(self, -1, "full output:")
#        self.text_ctrl_5 = wx.TextCtrl(self, -1, "1")
#        self.label_3 = wx.StaticText(self, -1, "ftol (f tolerance):")
#        self.text_ctrl_3 = wx.TextCtrl(self, -1, "1.49e-8")

        self.button_OK = wx.Button(self, -1, "OK")
        self.button_Cancel = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_RADIOBOX, self.OnRadio, self.radio_box_algorithm)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.button_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.button_Cancel)
        self.__set_properties()
        self.__do_layout()


    def name_algorithm(self):
        return({"leastsq":0,"fmin":1,"boxmin":2,"fmin-mystic":3,"de":4})

    def showData(self):
        self.radio_box_algorithm.SetSelection(self.name_algorithm()[self.controller.epscData.optData.nameAlgorithm])

    def OnRadio(self, event):
        self.selectedAlgorithm = event.GetInt()

    def OnOK(self,event):

        if self.selectedAlgorithm == 0 :
            self.controller.epscData.optData.nameAlgorithm = "leastsq"
            if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
                self.Parent.optBCC.disableRanges()
            elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
                 self.Parent.optFCC.disableRanges()
            else :
                 self.Parent.optHCP.disableRanges()
        elif self.selectedAlgorithm == 1 :
            self.controller.epscData.optData.nameAlgorithm = "fmin"
            if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
                self.Parent.optBCC.disableRanges()
            elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
                 self.Parent.optFCC.disableRanges()
            else :
                 self.Parent.optHCP.disableRanges()
        elif self.selectedAlgorithm == 2 :
            self.controller.epscData.optData.nameAlgorithm = "boxmin"
            if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
                self.Parent.optBCC.enableRanges()
            elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
                 self.Parent.optFCC.enableRanges()
            else :
                 self.Parent.optHCP.enableRanges()
        elif self.selectedAlgorithm == 3 :
            self.controller.epscData.optData.nameAlgorithm = "fmin-mystic"
            if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
                self.Parent.optBCC.enableRanges()
            elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
                 self.Parent.optFCC.enableRanges()
            else :
                 self.Parent.optHCP.enableRanges()
        elif self.selectedAlgorithm == 4 :
            self.controller.epscData.optData.nameAlgorithm = "de"
            if self.controller.epscData.matParam["Phase1"].typeCrystal == 0 :
                self.Parent.optBCC.enableRanges()
            elif self.controller.epscData.matParam["Phase1"].typeCrystal == 1 :
                 self.Parent.optFCC.enableRanges()
            else :
                 self.Parent.optHCP.enableRanges()
        self.controller.epscData.optData.turnOnFlag("optAlgorithm")
        self.treePanel.turnOnOptNode(0)

    def OnCancel(self,event):
        self.radio_box_algorithm.SetSelection(0)
        self.controller.epscData.optData.turnOffFlag("optAlgorithm")
        self.treePanel.turnOffOptNode(0)

    def __set_properties(self):
        # begin wxGlade: OptAlgorithm.__set_properties
        self.SetSize((547, 253))
        self.radio_box_algorithm.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: OptAlgorithm.__do_layout
        sizer_top = wx.BoxSizer(wx.VERTICAL)
        sizer_OK = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)
#        sizer_criteria = wx.StaticBoxSizer(self.sizer_criteria_staticbox, wx.VERTICAL)
#        grid_sizer_1 = wx.FlexGridSizer(3, 4, 0, 0)
        sizer_top.Add(self.radio_box_algorithm, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 2)
#        grid_sizer_1.Add(self.label_1, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.text_ctrl_1, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.label_4, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.text_ctrl_4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.label_2, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.text_ctrl_2, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.label_5, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.text_ctrl_5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.label_3, 0, wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add(self.text_ctrl_3, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
#        grid_sizer_1.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
#        grid_sizer_1.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
#        sizer_criteria.Add(grid_sizer_1, 1, wx.EXPAND, 0)
#        sizer_top.Add(sizer_criteria, 0, wx.ALL|wx.EXPAND, 2)
        sizer_btn.Add((20, 20), 1, wx.ADJUST_MINSIZE, 0)
        sizer_btn.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
        sizer_top.Add(sizer_btn, 0, wx.ALL|wx.EXPAND, 2)
        sizer_OK.Add((20, 20), 1, wx.ADJUST_MINSIZE, 0)
        sizer_OK.Add(self.button_OK, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_OK.Add(self.button_Cancel, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_top.Add(sizer_OK, 0, wx.ALL|wx.EXPAND, 2)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_top)
        # end wxGlade

# end of class OptAlgorithm


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = (None, -1, "")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
