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
import wx.lib
import wx.lib.hyperlink

querySCMTickets = ''.join(["http://danse.us/trac/SCM/query",
    '?status=new&status=assigned&status=reopened',
    '&order=priority'])
engdiffUsers = "http://groups.google.com/group/engdiff-users"
_authdata = '99.77.79.61.111.82.67.112'

class ReportPanel(wx.Dialog):
    """ dialog for reporting bugs
    """
    def __init__(self, *args, **kwds):
        # begin wxGlade: ErrorReportDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_header = wx.StaticText(self, -1, "SCMM has encountered a problem. We are sorry for the inconvenience.")
        self.label_text = wx.StaticText(self, -1, "To help us improve this software, please provide at least a short summary of the problem. When you click the Send Error Report button, the short summary, full description, error log and the version of the software will be sent to developers.")
        self.label_view_ticket = wx.StaticText(self, -1, "You can view current bug reports and feature requests ")
        self.ticketlink = wx.lib.hyperlink.HyperLinkCtrl(self, -1, "here.")
        self.label_view_community = wx.StaticText(self, -1, "Discuss SCM and learn about new developments and features")
        self.communitylink = wx.lib.hyperlink.HyperLinkCtrl(self, -1, "here.")
        self.label_email = wx.StaticText(self, -1, "Your email address")
        self.text_ctrl_reporter = wx.TextCtrl(self, -1, "")
        self.label_summary = wx.StaticText(self, -1, "Short summary:")
        self.text_ctrl_summary = wx.TextCtrl(self, -1, "")
        self.label_description = wx.StaticText(self, -1, "Full description:")
        self.text_ctrl_description = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.label_log = wx.StaticText(self, -1, "Error log:")
        self.text_ctrl_log = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.static_line_1 = wx.StaticLine(self, -1)
        self.button_send = wx.Button(self, -1, "Send Report")
        self.button_close = wx.Button(self, wx.ID_CANCEL, "Close")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.onSummaryText, self.text_ctrl_summary)
        self.Bind(wx.EVT_BUTTON, self.onSend, self.button_send)
        # end wxGlade
        self.__customProperties()
        return

    def __set_properties(self):
        # begin wxGlade: ErrorReportDialog.__set_properties
        self.SetTitle("Problem Report for PDFGui")
        self.SetSize((540, 600))
        self.button_send.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ErrorReportDialog.__do_layout
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        sizer_email = wx.BoxSizer(wx.HORIZONTAL)
        sizer_ticket_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_ticket = wx.BoxSizer(wx.HORIZONTAL)
        sizer_main.Add(self.label_header, 0, wx.ALL|wx.EXPAND, 5)
        sizer_main.Add(self.label_text, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_ticket.Add(self.label_view_ticket, 0, wx.ALL|wx.EXPAND, 5)
        sizer_ticket.Add(self.ticketlink, 1, wx.TOP|wx.BOTTOM, 5)
        sizer_main.Add(sizer_ticket, 0, wx.TOP|wx.BOTTOM, 5)
        sizer_ticket_copy.Add(self.label_view_community, 0, wx.ALL|wx.EXPAND, 5)
        sizer_ticket_copy.Add(self.communitylink, 1, wx.TOP|wx.BOTTOM, 5)
        sizer_main.Add(sizer_ticket_copy, 0, wx.TOP|wx.BOTTOM, 5)
        sizer_email.Add(self.label_email, 0, wx.ALL, 5)
        sizer_email.Add(self.text_ctrl_reporter, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_main.Add(sizer_email, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 10)
        sizer_main.Add(self.label_summary, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        sizer_main.Add(self.text_ctrl_summary, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        sizer_main.Add(self.label_description, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        sizer_main.Add(self.text_ctrl_description, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        sizer_main.Add(self.label_log, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        sizer_main.Add(self.text_ctrl_log, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 5)
        sizer_main.Add(self.static_line_1, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 5)
        sizer_buttons.Add((20, 20), 1, 0, 0)
        sizer_buttons.Add(self.button_send, 0, wx.ALL, 5)
        sizer_buttons.Add(self.button_close, 0, wx.ALL, 5)
        sizer_main.Add(sizer_buttons, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_main)
        self.Layout()
        # end wxGlade

    def __customProperties(self):
        """Set custom properties."""
        # Events
        self.errorReport = True
        self.ticketlink.SetURL(querySCMTickets)
        self.ticketlink.SetToolTip(wx.ToolTip(querySCMTickets))
        self.communitylink.SetURL(engdiffUsers)
        self.communitylink.SetToolTip(wx.ToolTip(engdiffUsers))
        return

    def ShowModal(self):
        # there are 2 modes: error report and feature request
        if self.text_ctrl_log.GetValue().strip() == "":
            self.SetTitle("Feature Request / Bug Report")
            self.label_header.SetLabel("Share you thoughts about SCM!")
            self.label_text.SetLabel("To help us improve this software, please provide a short summary of the problem or request.  When you click the Send Report button, the short summary, full description and the version of the software will be sent to developers.")
            self.label_log.SetLabel("")
            self.text_ctrl_log.Hide()
            self.errorReport = False
        else:
            self.SetTitle("Problem Report for SCM")
            self.label_header.SetLabel("SCM has encountered a problem. We are sorry for the inconvenience.")
            self.label_text.SetLabel("To help us improve this software, please provide a short summary of how the error occurred. When you click the Send Report button, the short summary, full description and the version of the software will be sent to developers.")
            self.label_log.SetLabel("Error log:")
            self.text_ctrl_log.Show()
            self.errorReport = True

        wx.Dialog.ShowModal(self)


    def onSend(self, event): # wxGlade: ErrorReportDialog.<event_handler>
        import urllib2,urllib,cookielib

        description = self.text_ctrl_description.GetValue().strip() + "\n"
        traceback = 'N/A'
        if self.errorReport:
            traceback = '\n' + self.text_ctrl_log.GetValue().strip() + '\n'

        reporter = self.text_ctrl_reporter.GetValue().strip()
        if not reporter: reporter = 'anonymous'

        ticketinfo = {'summary': self.text_ctrl_summary.GetValue().strip(),
                    'description' : description,
                    #'priority' : 'major',
                    #'type': 'defect',
                    #'component' : 'pdfgui' ,
                    #'version': __version__,
                    'reporter':reporter,
                    'traceback': traceback,
                    #'action' :'create',
                    #'status' : 'new',
                    #'milestone': '',
                    #'owner' : 'nobody'
                    }
        data_get = {}
        data_get['summary'] = self.text_ctrl_summary.GetValue().strip()
        data_get['description'] = description
        data_get['reporter'] = reporter

        headers = {'User-agent':'SCM (compatible; MSIE 5.5; WindowsNT)'}


        rooturl = 'http://engdiff.engineering.iastate.edu'
        ticketurl = rooturl + '/bin/postBugReport.asp'


#        cookier = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
#        opener = urllib2.build_opener(handler, cookier)
#        urllib2.install_opener(opener)

        try:
            # login: authenticate for the session
#            urllib2.urlopen(loginurl)
#            content = urllib.urlencode(ticketinfo)
#            request = urllib2.Request(ticketurl, content, headers)
#            handle = urllib2.urlopen(request)
            content = urllib.urlencode(data_get)
            full_url = ticketurl + "?" + content
            print full_url
            request = urllib2.Request(full_url)
            handle = urllib2.urlopen(request)
            # handle.read() # result, but can be discarded
        except IOError,e:
            errorinfo = str(e)
            if hasattr(e, 'code'):
                errorinfo += '< Error code = %s >'%e.code
            dlg = wx.MessageDialog(self, "Report can not be sent: " + errorinfo, "Error", wx.CANCEL|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        except:
            raise
        else: # success
            dlg = wx.MessageDialog(self, "Your report has been sent", "Message sent", wx.OK|wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.Close()
        event.Skip()

    def onSummaryText(self, event): # wxGlade: ErrorReportDialog.<event_handler>
        """Enable sending only if short summary is filled out."""
        self.button_send.Enable(True)
        value = self.text_ctrl_summary.GetValue()
        if not value.strip():
            self.button_send.Enable(False)
        event.Skip()

# end of class ErrorReportDialog


##### testing code ############################################################
class MyApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        self.dialog = reportPanel(None, -1, "")
        self.SetTopWindow(self.dialog)
        self.test()
        self.dialog.ShowModal()
        self.dialog.Destroy()
        return 1

    def test(self):
         '''Testing code goes here.'''
         errortext = """\
Exception in thread Thread-3:\n\
Traceback (most recent call last):\n\
  File "/usr/lib/python2.4/threading.py", line 442, in __bootstrap\n\
    self.run()\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/PDFGui/gui/../control/fitting.py", line 54, in run\n\
    self.fitting.run()\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/PDFGui/gui/../control/fitting.py", line 299, in run\n\
    if self.refine_step():\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/PDFGui/gui/../control/fitting.py", line 504, in refine_step\n\
    phase.obtainRefined(self.server, iphase)\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/PDFGui/gui/../control/fitstructure.py", line 79, in obtainRefined\n\
    self.refined.readStr(server.save_struct_string(iphase), 'pdffit')\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/Structure/Structure/structure.py", line 141, in readStr\n\
    new_structure = parse(s, format)\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/Structure/Structure/Parsers/__init__.py", line 43, in parse\n\
    stru = p.parseLines(lines)\n\
  File "/u23b/farrowch/Programming/Pyre/diffraction/Structure/Structure/Parsers/P_pdffit.py", line 85, in parseLines\n\
    xyz = [ float(w) for w in wl1[1:4] ]\n\
StructureFormatError: 10: file is not in PDFFit format"""

#         self.dialog.text_ctrl_log.SetValue(errortext)
         self.dialog.text_ctrl_log.SetValue(" ")
# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()

##### end of testing code #####################################################
