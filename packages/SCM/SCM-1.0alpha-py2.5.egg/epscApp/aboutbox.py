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
import wx.lib.hyperlink
import random
import os.path
import os
import epscComp.config

_acknowledgement =  \
'''This software was developed by the Iowa State University as part of the
Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
project funded by the US National Science Foundation.

'''

_homepage = "http://engdiff.org"


# authors list is shuffled randomly every time
_authors = []
_paper = "http://danse.us/trac/SCM/newticket"
_license = "mailto:engdiff@gmail.com"


def launchBrowser(url):
    '''Launches browser and opens specified url

    In some cases may require BROWSER environment variable to be set up.

    @param url: URL to open
    '''
    import webbrowser
    webbrowser.open(url)


class AboutBox(wx.Dialog):
    '''"About" Dialog
    Shows product name, current version, authors, and link to the product page.

    '''

    def __init__(self, *args, **kwds):

        # begin wxGlade: DialogAbout.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)

        # Mac doesn't display images with transparent background so well, keep it for Windows
        if os.name == 'nt':
            self.bitmap_logo = wx.StaticBitmap(self, -1, wx.Bitmap(epscComp.config.dirImages + "scm_logo.gif"))
        else:
            self.bitmap_logo = wx.StaticBitmap(self, -1, wx.Bitmap(epscComp.config.dirImages + "scm_logo.gif"))

        #self.bitmap_logo = wx.StaticBitmap(self, -1, wx.Bitmap(os.path.join("images","angles.png")))
        self.label_title = wx.StaticText(self, -1, "Cy-SCM")
        self.label_version = wx.StaticText(self, -1, "")
        self.label_build = wx.StaticText(self, -1, "Build:")
        self.label_svnrevision = wx.StaticText(self, -1, "")
        self.label_copyright = wx.StaticText(self, -1, "(c) 2007, Iowa State University")
        self.label_author = wx.StaticText(self, -1, "authors")
        self.hyperlink = wx.lib.hyperlink.HyperLinkCtrl(self, -1, _homepage, URL=_homepage)
        #self.hyperlink_license = wx.lib.hyperlink.HyperLinkCtrl(self, -1, "Comments? Bugs? Requests?", URL=_paper)
        #self.hyperlink_license = wx.StaticText(self, -1, "Comments? Bugs? Requests?")
        #self.hyperlink_paper = wx.lib.hyperlink.HyperLinkCtrl(self, -1, "Send us a ticket", URL=_license)
        self.static_line_1 = wx.StaticLine(self, -1)
        self.label_acknowledgement = wx.StaticText(self, -1, _acknowledgement)
        self.static_line_2 = wx.StaticLine(self, -1)
        self.bitmap_button_nsf = wx.BitmapButton(self, -1, wx.NullBitmap)
        self.bitmap_button_danse = wx.BitmapButton(self, -1, wx.NullBitmap)
        self.bitmap_button_isu = wx.BitmapButton(self, -1, wx.NullBitmap)
        self.static_line_3 = wx.StaticLine(self, -1)
        self.button_OK = wx.Button(self, wx.ID_OK, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.onNsfLogo, self.bitmap_button_nsf)
        self.Bind(wx.EVT_BUTTON, self.onDanseLogo, self.bitmap_button_danse)
        self.Bind(wx.EVT_BUTTON, self.onISUlogo, self.bitmap_button_isu)
        # end wxGlade

        # fill in acknowledgements
#       self.text_ctrl_acknowledgement.SetValue(__acknowledgement__)

        # randomly shuffle authors' names
        random.shuffle(_authors)
        strLabel = ", ".join(_authors)

        # display version and svn revison numbers
#        verwords = __version__.split('.')
#        version = '.'.join(verwords[:-1])
#        revision = verwords[-1]

        self.label_author.SetLabel(strLabel)
#        self.label_version.SetLabel(version)
#        self.label_svnrevision.SetLabel(__version__)

        # set bitmaps for logo buttons
        logo = wx.Bitmap(epscComp.config.dirImages + "nsf_logo.png")
        self.bitmap_button_nsf.SetBitmapLabel(logo)
        logo = wx.Bitmap(epscComp.config.dirImages + "danse_logo.png")
        self.bitmap_button_danse.SetBitmapLabel(logo)
        logo = wx.Bitmap(epscComp.config.dirImages + "Engdiff_logo.gif")
        self.bitmap_button_isu.SetBitmapLabel(logo)

        # resize dialog window to fit version number nicely
        if wx.VERSION >= (2,7,2,0):
            size = [self.GetEffectiveMinSize()[0], self.GetSize()[1]]
        else:
            size = [self.GetBestFittingSize()[0], self.GetSize()[1]]

        self.Fit()
#        self.SetSize(size)
#       self.FitInside()


    def __set_properties(self):
        # begin wxGlade: DialogAbout.__set_properties
        self.SetTitle("About")
        self.SetSize((600, 595))
        self.label_title.SetFont(wx.Font(26, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_version.SetFont(wx.Font(26, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        #self.hyperlink_license.Enable(False)
        #self.hyperlink_license.Hide()
        #self.hyperlink_paper.Enable(True)
        #self.hyperlink_paper.Hide()
        self.bitmap_button_nsf.SetSize(self.bitmap_button_nsf.GetBestSize())
        self.bitmap_button_danse.SetSize(self.bitmap_button_danse.GetBestSize())
        self.bitmap_button_isu.SetSize(self.bitmap_button_isu.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DialogAbout.__do_layout
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_button = wx.BoxSizer(wx.HORIZONTAL)
        sizer_logos = wx.BoxSizer(wx.HORIZONTAL)
        sizer_header = wx.BoxSizer(wx.HORIZONTAL)
        sizer_titles = wx.BoxSizer(wx.VERTICAL)
        sizer_build = wx.BoxSizer(wx.HORIZONTAL)
        sizer_title = wx.BoxSizer(wx.HORIZONTAL)
        sizer_header.Add(self.bitmap_logo, 0, wx.EXPAND, 0)
        sizer_title.Add(self.label_title, 0, wx.LEFT|wx.EXPAND|wx.ADJUST_MINSIZE, 10)
        sizer_title.Add((20, 20), 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_title.Add(self.label_version, 0, wx.RIGHT|wx.ALIGN_BOTTOM|wx.ADJUST_MINSIZE, 10)
        sizer_titles.Add(sizer_title, 0, wx.EXPAND, 0)
        sizer_build.Add(self.label_build, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_build.Add(self.label_svnrevision, 0, wx.ADJUST_MINSIZE, 0)
        sizer_titles.Add(sizer_build, 0, wx.TOP|wx.EXPAND, 5)
        sizer_titles.Add(self.label_copyright, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ADJUST_MINSIZE, 10)
        sizer_titles.Add(self.label_author, 0, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_titles.Add(self.hyperlink, 0, wx.LEFT|wx.RIGHT, 10)
        sizer_titles.Add((20, 20), 0, wx.ADJUST_MINSIZE, 0)
        #sizer_titles.Add(self.hyperlink_license, 0, wx.LEFT|wx.RIGHT, 10)
        #sizer_titles.Add(self.hyperlink_paper, 0, wx.LEFT|wx.RIGHT, 10)
        sizer_header.Add(sizer_titles, 0, wx.EXPAND, 0)
        sizer_main.Add(sizer_header, 0, wx.BOTTOM|wx.EXPAND, 3)
        sizer_main.Add(self.static_line_1, 0, wx.EXPAND, 0)
        sizer_main.Add(self.label_acknowledgement, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 7)
        sizer_main.Add(self.static_line_2, 0, wx.EXPAND, 0)
        sizer_logos.Add(self.bitmap_button_nsf, 0, wx.LEFT|wx.ADJUST_MINSIZE, 2)
        sizer_logos.Add(self.bitmap_button_danse, 0, wx.LEFT|wx.ADJUST_MINSIZE, 2)
        sizer_logos.Add(self.bitmap_button_isu, 0, wx.LEFT|wx.ADJUST_MINSIZE, 2)
        sizer_logos.Add((50, 50), 0, wx.ADJUST_MINSIZE, 0)
        sizer_main.Add(sizer_logos, 0, wx.EXPAND, 0)
        sizer_main.Add(self.static_line_3, 0, wx.EXPAND, 0)
        sizer_button.Add((20, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_button.Add(self.button_OK, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 10)
        sizer_main.Add(sizer_button, 0, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_main)
        self.Layout()
        self.Centre()
        # end wxGlade

#    def _launchBrowser(self, url):
#        import webbrowser
#        webbrowser.open(url)

    def onNsfLogo(self, event): # wxGlade: DialogAbout.<event_handler>
#        self._launchBrowser("http://www.nsf.gov")
        launchBrowser("http://www.nsf.gov")
        event.Skip()

    def onDanseLogo(self, event): # wxGlade: DialogAbout.<event_handler>
#        self._launchBrowser("http://wiki.cacr.caltech.edu/danse")
        launchBrowser("http://wiki.cacr.caltech.edu/danse")
        event.Skip()

    def onISUlogo(self, event): # wxGlade: DialogAbout.<event_handler>
#        self._launchBrowser("http://www.msu.edu")
        launchBrowser("http://www.engdiff.org")
        event.Skip()

# end of class DialogAbout

##### testing code ############################################################
class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        dialog = DialogAbout(None, -1, "")
        self.SetTopWindow(dialog)
        dialog.ShowModal()
        dialog.Destroy()
        return 1

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

##### end of testing code #####################################################
