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

class HKLDialog(wx.Dialog):
    """
       Dialog for selecting HKL data for optimization
    """
    def __init__(self, parent, winSize):
        # begin wxGlade: VoceDialog.__init__
        wx.Dialog.__init__(self, parent, size=winSize)
        self.epscData = parent.controller.epscData
        if self.epscData.phaseNum != 2022 and self.epscData.phaseNum != 2032 :
            self.phase = "Phase1"
        else :
            self.phase = "Phase2"
        self.chkbox = []
        listHKL = []
        for i in range(self.epscData.numDiffractionData[self.phase]) :
           listHKL.append(str(self.epscData.listDiffractionData[self.phase][i].name) + "_" + self.epscData.listDiffractionData[self.phase][i].angle)
#            self.Bind(wx.EVT_CHEKBOX, self.OnHKL, self.chkbox[i])
        self.chkHKL = wx.CheckListBox(self,-1,(80,60),wx.DefaultSize, listHKL)
        for i in range(self.epscData.numDiffractionData[self.phase]) :
           if self.epscData.listDiffractionData[self.phase][i].flagOn == True :
               self.chkHKL.Check(i)
        self.btn_OK = wx.Button(self, -1, "OK")
        self.btn_Cancel = wx.Button(self, -1, "Cancel")

        self.Bind(wx.EVT_CHECKLISTBOX, self.OnHKL, self.chkHKL)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.btn_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.btn_Cancel)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def OnHKL(self, event):
        index = event.GetSelection()
        if self.chkHKL.IsChecked(index):
            self.epscData.listDiffractionData[self.phase][index].flagOn = True
        else :
            self.epscData.listDiffractionData[self.phase][index].flagOn = False


    def OnOK(self, event):
        self.Close()

    def OnCancel(self, event):
        self.Close()

    def __set_properties(self):

        self.SetTitle("Select HKLs")


    def __do_layout(self):
        # begin wxGlade: VoceDialog.__do_layout
        sizer_top = wx.BoxSizer(wx.VERTICAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)

#        for i in range(self.epscData.numDiffractionData[self.phase]) :
#            sizer_top.Add(self.chkbox[i], 2,  wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer_top.Add(self.chkHKL, 2, wx.ALIGN_CENTER|wx.ALL, 5)
        sizer_btn.Add(self.btn_OK, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_btn.Add(self.btn_Cancel, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        sizer_top.Add(sizer_btn, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_top)
        sizer_top.Fit(self)
        sizer_top.SetSizeHints(self)
        self.Layout()
        # end wxGlade

# end of class VoceDialog

########################## Code Testing Start ##################################

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    hklDialog = HKLDialog(None, 1)
    app.SetTopWindow(hklDialog)
    hklDialog.Show()
    app.MainLoop()

########################### Code Testing End ###################################

