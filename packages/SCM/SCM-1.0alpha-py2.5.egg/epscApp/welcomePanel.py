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
import wx.lib.fancytext as fancytext
from string import center
import epscComp.config

class WelcomePanel(wx.Panel):
    """
        Default panel in the center position
    """
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        png = wx.Image(epscComp.config.dirImages + "scmFront.jpg", wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.stImage = wx.StaticBitmap(self, -1, png, (10, 10), (png.GetWidth(), png.GetHeight()))
        self.__do_layout()

    def setProperties(self):
        pass

    def __do_layout(self):
        sizer_0 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.stImage, 1,
                wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        sizer_0.Add(sizer_1, 1,
                wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_0)

    # Methods overloaded from PDFPanel
    def refresh(self):
        return