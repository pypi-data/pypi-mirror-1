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

import os
import sys
import wx

from epscController import EpscController
from materialsNotebook import MaterialsNotebook
from optNotebook import OptNotebook
from plotNotebook import PlotNotebook
from welcomePanel import WelcomePanel
from treePanel import TreePanel
from plotPanel import PlotPanel
from aboutbox import AboutBox
from reportPanel import ReportPanel
from scmProject import ScmProject
from simulationPanel import SimulationPanel
import epscComp.config

#from eshelbyComp.eshelbyGUI import EshelbyGUI


class EpscGui(wx.Frame):

    """
     EpscGui is the top GUI class which maintains all the widgets.
     The left pane is a tree control from treePanel and the right pane is a dynamic panel.

     ** Node Type in the left pane **
     "Model"  -- model parameters
     "Experiment" -- experimental data file names
     "Optimization" -- optimization parameters

    """

    def __init__(self, parent, id=-1, title="Cy-SCM (EPSC)",pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
                                            wx.SUNKEN_BORDER |
                                            wx.CLIP_CHILDREN):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        icon = wx.Icon(os.path.join(epscComp.config.dirImages, "scm_icon.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.SetTitle("Cy-SCM (EPSC)")
        # tell FrameManager to manage this frame
        self._mgr = wx.aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        self._perspectives = []

#        outputTextCtrl = wx.TextCtrl(self,-1, "", wx.Point(0, 0), wx.Size(150, 50),
#                           wx.NO_BORDER | wx.TE_MULTILINE)
#        self.outputTextCtrl = epscComp.myOut.MyOut(outputTextCtrl)
        self.controller = EpscController(self)

        self.currentRun = 0
        self.previousPhase = None

        self.project = ScmProject(self)
        self.flagSave = False
        self.flagClose = False
       # sys.stdout = self.outputTextCtrl
        # create menu

        self.createMenuBar()

        self.statusbar = self.CreateStatusBar(1, wx.ST_SIZEGRIP)
#        self.statusbar.SetStatusWidths([-2, -3])
        self.statusbar.SetStatusText("Ready", 0)
#        self.statusbar.SetStatusText("SCM", 1)

        self.SetInitialSize(wx.Size(980, 780))

        # create some toolbars
        self.createToolBar()

        # add a bunch of panes
        self.treePanel = TreePanel(self)
        self._mgr.AddPane(self.treePanel, wx.aui.AuiPaneInfo().
                          Name("treePane").Caption("Active Data").
                          MinSize(wx.Size(200.400)).
                          Left().Layer(1).CloseButton(True).MaximizeButton(True))

        self.plotPanel = PlotPanel(self)
        self.plotPanel.controller = self.controller

        self._mgr.AddPane(self.plotPanel, wx.aui.AuiPaneInfo().
                          Name("plotPane").Caption("Plot Options").
                          MinSize(wx.Size(200.400)).
                          Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))

#        self._mgr.AddPane(self.CreateTextCtrl(), wx.aui.AuiPaneInfo().
#                          Name("outputPane").Caption("SCM Output").
#                          BestSize(wx.Size(200,100)).
#                          Bottom().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))

     # create some center panes

        self.centerPanels = {
                             "Phase1"    :    MaterialsNotebook(self),
                             "2Phase1"    :    MaterialsNotebook(self),
                             "2Phase2"    :    MaterialsNotebook(self),
                             "2Phase1_BMG"    :    MaterialsNotebook(self),
                             "2Phase2_BMG"    :    MaterialsNotebook(self),
                             "welcomePanel"    :   WelcomePanel(self),
                             "Opt"    : OptNotebook(self),
                             "plot"    : PlotNotebook(self),
                             "simulation" : SimulationPanel(self)
                             }

        for key in self.centerPanels :
           self._mgr.AddPane(self.centerPanels[key], wx.aui.AuiPaneInfo().Name(key).
                              MinSize(wx.Size(500,500)).
                              CenterPane().Hide())
           self.centerPanels[key].controller = self.controller
           self.centerPanels[key].treePanel = self.treePanel
           self.centerPanels[key].kind = key
           self.centerPanels[key].setProperties()

          # make some default perspectives

        all_panes = self._mgr.GetAllPanes()

        for ii in xrange(len(all_panes)):
            if not all_panes[ii].IsToolbar():
                all_panes[ii].Hide()

        self._mgr.GetPane("welcomePanel").Show()
        self._mgr.GetPane("treePane").Show().Left().Layer(1).Row(0).Position(0)
        self._mgr.GetPane("plotPane").Show().Left().Layer(1).Row(0).Position(1)

        perspective_default = self._mgr.SavePerspective()

        self._perspectives.append(perspective_default)

        # "commit" all changes made to FrameManager
        self._mgr.Update()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def menuData1(self):
        """ File menus
        """
        return("&File",
                    (101, "&New Project  ","Start new project with SCM model creation and optimization", self.OnNew),
                    (102, "&Open Project  ","Restore previous project file with model parameters, experiment files, and optimization setting", self.OnOpen),
                    (103, "&Save Project  ","Save project file with model parameters, experiment files, and optimization setting", self.OnSave),
#                    (105, "&Close Project  ","Close", self.OnCloseProject),
                    (104, "&Quit  ","Quit", self.OnCloseWindow))

    def menuDataView(self):
        """ View menus
        """
        return("&View",
                    (301, "Default Window Layout",  "Default Window Layout",self.OnRestorePerspective),
                    (None,None,None,None),
                    (302, "Hide Tree Panel", "Hide Active Data Tree Panel", self.OnView),
                    (303, "Hide Plot Panel", "Hide Plot Options Panel", self.OnView),)
#                    (304, "Hide Output Panel", "Hide Output Panel", self.OnView))

    def menuData2(self):
        """ Model menus
        """
        return("&Phase",
            (201, "1Phase:Polycrystal", "Single Phase polycrystal System",  self.OnPhase))
#            (202, "2Phase:Polycrystal", "2Phase:Polycrystal",  self.OnPhase))
#            (203, "2Phase:Polycrystal + Amorphous", "2Phase:Polycrystal + Amorphous",  self.OnPhase))

    def menuData4(self):
        """ Optimization menus
        """
        return("&Optimization",
                (401, "Algorithms", "Scipy and mystic optimization algorithm", self.OnAlgorithm),
                (402, "Parameters", "Parameters", self.OnParameters))
    def menuData5(self):
        """ Run menus
        """
        return("&Run",
                (501, "Run Model", "Run single SCM run", self.OnRunModel),
                (502, "Run Optimization", "Run multi SCM runs to match with experimental data", self.OnRunOptimization),
                (503, "Analytical Simulation", "Run analytical simulation to match with experimental data", self.OnRunSimulation),
                )

    def menuData6(self):
        """ Plot menus
        """
        return("&Plot",
                (601, "Plot Model Run - Macro", "Plot Model", self.OnPlotMacro),
                (602, "Plot Model Run - Neutron", "Plot Model", self.OnPlotNeutron))

    def menuData7(self):
        """ Help menus
        """
        return("&Help",
                (701, "About Cy-SCM", "Self Consistent Modeling Package developed by DANSE project at Iowa State Univeristy ", self.OnAbout),
                (702, "Report Bugs", "Send email to engdiff-users@gmail.com", self.OnReport))

#    def menuData8(self):
#        """ Model menus
#        """
#        return("&Model",
##               (803, "Eshelby", "Eshelby", self.OnModel),
#               (801, "EPSC", "Elasto Plastic Self Consistent Modeling", self.OnModel))
##               (802, "VPSC", "VPSC", self.OnModel))


    def createMenuBar(self):
        """ Create a menu bar and put menus on it
        """
        menuBar = wx.MenuBar()

        menuLabel = self.menuData1()[0]
        menuItems = self.menuData1()[1:]
        menuBar.Append(self.createMenu(menuItems), menuLabel)

#        menuLabel = self.menuData8()[0]
#        menuItems = self.menuData8()[1:]
#        menuBar.Append(self.createMenu(menuItems), menuLabel)



        menuLabel = self.menuData2()[0]
        menuItems = self.menuData2()[1:]
#        menuBar.Append(self.createCheckMenu(menuItems), menuLabel)
        menuBar.Append(self.createMenu(menuItems), menuLabel)


        menuLabel = self.menuData4()[0]
        menuItems = self.menuData4()[1:]
        menuBar.Append(self.createMenu(menuItems), menuLabel)
        menuLabel = self.menuData5()[0]
        menuItems = self.menuData5()[1:]
        menuBar.Append(self.createMenu(menuItems),menuLabel)
#        menuLabel = self.menuData6()[0]
#        menuItems = self.menuData6()[1:]
#        menuBar.Append(self.createMenu(menuItems),menuLabel)

        menuLabel = self.menuDataView()[0]
        menuItems = self.menuDataView()[1:]
        menuBar.Append(self.createMenu(menuItems), menuLabel)

        menuLabel = self.menuData7()[0]
        menuItems = self.menuData7()[1:]
        menuBar.Append(self.createMenu(menuItems),menuLabel)

        self.SetMenuBar(menuBar)

    def createMenu(self,menuData):
        """ Create each menus
        """
        menu = wx.Menu()
        for eachId, eachLabel, eachStatus, eachHandler in menuData:
            if not eachLabel:
                menu.AppendSeparator()
                continue
            if eachLabel == "2Phase:Polycrystal" :
                submenu = wx.Menu()
                phase1 = submenu.Append(2021, "Phase1")
                phase2 = submenu.Append(2022, "Phase2")
                self.Bind(wx.EVT_MENU,  self.OnPhase, phase1)
                self.Bind(wx.EVT_MENU,  self.OnPhase, phase2)
                menuItem = menu.AppendMenu(eachId, eachLabel, submenu)
            elif eachLabel == "2Phase:Polycrystal + Amorphous" :
                submenu = wx.Menu()
                phase1 = submenu.Append(2031, "Phase1")
                phase2 = submenu.Append(2032, "Phase2-BMG")
                self.Bind(wx.EVT_MENU,  self.OnPhase, phase1)
                self.Bind(wx.EVT_MENU,  self.OnPhase, phase2)
                menuItem = menu.AppendMenu(eachId, eachLabel, submenu)

            else:
                menuItem = menu.Append(eachId, eachLabel, eachStatus)
                if eachLabel == "VPSC" or eachLabel=="Algorithms" or eachLabel=="Parameters":
                    menuItem.Enable(False)
                if eachLabel == "VPSC" :
                    menuItem.Enable(False)

            self.Bind(wx.EVT_MENU,eachHandler,menuItem)
        return menu

    def createToolBar(self):
        """Create a tool bar and put it in parent frame
        """
        tsize = (24,24)
        new_bmp =   wx.Bitmap(epscComp.config.dirImages + "folder_yellow.png", wx.BITMAP_TYPE_ANY)
        open_bmp = wx.Bitmap(epscComp.config.dirImages + "folder_yellow_open.png", wx.BITMAP_TYPE_ANY)
        save_bmp = wx.Bitmap(epscComp.config.dirImages + "3floppy_unmount.png", wx.BITMAP_TYPE_ANY)
        configure_bmp = wx.Bitmap(epscComp.config.dirImages + "configure.png", wx.BITMAP_TYPE_ANY)
        opt_bmp = wx.Bitmap(epscComp.config.dirImages + "optimize.png", wx.BITMAP_TYPE_ANY)
        run_bmp = wx.Bitmap(epscComp.config.dirImages + "model_run.png", wx.BITMAP_TYPE_ANY)
        exp_bmp = wx.Bitmap(epscComp.config.dirImages + "edu_science.png", wx.BITMAP_TYPE_ANY)
        opt_bmp = wx.Bitmap(epscComp.config.dirImages + "opt_run.png", wx.BITMAP_TYPE_ANY)
        plot_bmp = wx.Bitmap(epscComp.config.dirImages + "plot.png", wx.BITMAP_TYPE_ANY)
        cancel_bmp = wx.Bitmap(epscComp.config.dirImages + "cancel.png", wx.BITMAP_TYPE_ANY)

        self.toolbar = self.CreateToolBar()
        self.toolbar.SetToolBitmapSize(tsize)
        self.toolbar.AddLabelTool(10, "New", new_bmp, shortHelp="New", longHelp="Start new project with SCM model creation and optimization")
        self.Bind(wx.EVT_TOOL, self.OnNew, id=10)
        self.toolbar.AddLabelTool(20, "Open", open_bmp, shortHelp="Open", longHelp="Restore previous project file with model parameters, experiment files, and optimization setting")
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=20)
        self.toolbar.AddLabelTool(30, "Save", save_bmp, shortHelp="Save", longHelp="Save project file with model parameters, experiment files, and optimization setting")
        self.Bind(wx.EVT_TOOL, self.OnSave, id=30)
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(40, "Run", run_bmp, shortHelp="Run", longHelp="Run single SCM run")
        self.Bind(wx.EVT_TOOL, self.OnRunModel, id=40)
        self.toolbar.AddLabelTool(50, "Optimize", opt_bmp, shortHelp="Optimize", longHelp="Run multi SCM runs to match with experimental data")
        self.Bind(wx.EVT_TOOL, self.OnRunOptimization, id=50)
        self.toolbar.AddLabelTool(70, "Plot", plot_bmp, shortHelp="Plot", longHelp="Show plotting panels")
        self.Bind(wx.EVT_TOOL, self.OnPlot, id=70)
        self.toolbar.AddLabelTool(60, "Cancel", cancel_bmp, shortHelp="Cancel", longHelp="Stop SCM engine or optimization process")
        self.Bind(wx.EVT_TOOL, self.OnCancelRun, id=60)
#        toolbar.AddLabelTool(50, "Exp", exp_bmp, shortHelp="Exp", longHelp = "Experimental files setting")
#        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=50)
        self.ToolBar.EnableTool(60, False)
        self.toolbar.Realize()

    def panelsData(self):
        return({201:"Phase1",2021:"2Phase1",2022:"2Phase2", \
                2031:"2Phase1_BMG",2032:"2Phase2_BMG", \
                401:"Opt",402:"Opt"})

    def phaseSet(self):
        return({201:"1Phase",2021:"2Phase",2022:"2Phase",2031:"BMG",2032:"BMG", \
                401:"Opt",402:"Opt"})

    def checkForSave(self):
        """Pop up a dialog if the project needs to be saved.

        returns:
        wx.ID_YES if the user chose to save the project.
        wx.ID_NO if the user chose not to save the project.
        wx.ID_CANCEL if they changed their mind about their action.
        """
        code = wx.ID_NO

        if self.controller.epscData.isAltered and self.flagSave == False:
            d = wx.MessageDialog( self, "Would you like to save this session?",
                    "Save?", wx.YES_NO|wx.CANCEL)
            code = d.ShowModal()
            if code == wx.ID_YES:
                code = self.OnSave(None)
            self.controller.newEpscData()
            d.Destroy()
            self.closePanels()

        return code

    def closePanels(self):
#        self.nt2phase1.Close()
#        self.nt2phase2.Close()
        if self.controller.epscData.phaseNum == 201 :
            self.centerPanels["Phase1"].removePages()
            self.centerPanels["Opt"].removePages()
        elif self.controller.epscData.phaseNum == 2021 or self.controller.epscData.phaseNum==2022:
            self.centerPanels["2Phase1"].removePages()
            self.centerPanels["2Phase2"].removePages()
            self.centerPanels["Opt"].removePages()
        elif self.controller.epscData.phaseNum == 2031 or self.controller.epscData.phaseNum==2032:
            self.centerPanels["2Phase1_BMG"].removePages()
            self.centerPanels["2Phase2_BMG"].removePages()
            self.centerPanels["Opt"].removePages()


    def OnNew(self, event):
        retVal = self.checkForSave()
        self.project.fullPath = ""
        self.treePanel.clearTree()
        self.clearPlots()
        self.closePanels()
        self.showPanel("welcomePanel")
        self.flagSave = False
        self.flagClose = True
        self.centerPanels["plot"].clearPlot()

    def OnCloseProject(self, event):
        retVal = self.checkForSave()

        self.project.fullPath = ""
        self.controller.newEpscData()
        self.treePanel.clearTree()
        self.closePanels()
        self.showPanel("welcomePanel")
        self.project.close()
        self.clearPlots()
        self.flagClose = True

    def OnOpen(self, event):

        dlg = wx.FileDialog(
            self, message = "Choose a project file",
            defaultDir = os.getcwd(),
            defaultFile = "",
            wildcard = "SCM project (*.prj)|*.prj|" "All files (*.*)|*.*",
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK :
            retVal = self.checkForSave()
            self.treePanel.clearTree()
            self.project.open(dlg.GetPaths()[0])
#            try :
            self.switchRightPanel(self.controller.epscData.phaseNum,"Open")
#            except:
#                msg = "The data you entered does not match with Cy-Epsc."
#                dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
#                dlg.ShowModal()
#                dlg.Destroy()
#                self.project = ScmProject(self)
#                return 0
            self.treePanel.setTree(self.controller.epscData.phaseNum)
            self.clearPlots()
            self.controller.epscData.flagFromFile = True
            self.flagSave = False
            self.flagClose = False

    def OnSave(self, event):
        if self.project.flag == True :
            self.project.save()
        elif self.controller.epscData.isAltered :
            dlg = wx.FileDialog(
            self, message = "Choose a project file",
            defaultDir = os.getcwd(),
            defaultFile = "project1.prj",
            wildcard = "SCM project (*.prj)|*.prj|" "All files (*.*)|*.*",
            style=wx.SAVE | wx.CHANGE_DIR
            )
            if dlg.ShowModal() == wx.ID_OK :
                self.project.saveAs(dlg.GetPaths()[0])
        self.flagSave = True

    def OnCloseWindow(self, event):
        """ Close main application
        """
        self.Destroy()

    def OnView(self, event):
        Id = event.GetId()
        if Id == 302 :
            if self._mgr.GetPane("treePane").IsShown() == True :
                self._mgr.GetPane("treePane").Hide()

        elif Id == 303 :
            if self._mgr.GetPane("plotPane").IsShown() == True :
                self._mgr.GetPane("plotPane").Hide()
        else :
            if self._mgr.GetPane("outputPane").IsShown() == True :
                self._mgr.GetPane("outputPane").Hide()
        self._mgr.Update()
        return


    def OnModel(self, event):
        """ Open the model which user selected
        """
        Id = event.GetId()
        if Id == 803 :
            eshelbyFrame = EshelbyGUI(None, -1, "Eshelby Frame",size=(700,480))
            eshelbyFrame.Show()

    def OnPhase(self, event):
        """ Open phase panel
        """
        Id = event.GetId()
        self.controller.epscData.phaseNum = Id
        self.controller.epscData.phaseName = self.phaseSet()[Id]
        if self.previousPhase == None :
            self.previousPhase = Id
        self.switchRightPanel(Id)
        self.treePanel.setTree(Id)

    def OnAlgorithm(self, event):
        """ Open optimization algorithm panel
        """
        self.switchRightPanel(401)
        self.centerPanels["Opt"].showPanels()

    def OnParameters(self, event):
        """ Open optimization parameters panel
        """
        self.switchRightPanel(402)
        self.centerPanels["Opt"].showPanels()

    def checkInputs(self):
        """ Check out whether users input data required
        """
        if not self.controller.epscData.generalData.saved :
            msg = "You should input general parameters!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        if not self.controller.epscData.matParam["Phase1"].saved :
            msg = "You should input material parameters!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        if not self.controller.epscData.textureDataSaved :
            msg = "You should input texture data!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        if not self.controller.epscData.diffractionDataSaved :
            msg = "You should input diffraction data!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        if not self.controller.epscData.processDataSaved :
            msg = "You should input process data!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        return 1

    def OnRunModel(self, event):
        """ Run epsc model
        """
        if self.checkInputs()==0 :
            return

        self.currentRun = 2
        self.controller.runOptimizer(mode="run")
        self.controller.epscData.flagRun = True
        self.OnPlot(None)

    def enableToolbar(self,mode):
        menuBar = self.GetMenuBar()
        runMenu = menuBar.FindItemById(501)
        optMenu = menuBar.FindItemById(502)
        if mode == 0 :
            self.ToolBar.EnableTool(40, False)
            self.ToolBar.EnableTool(50, False)
            self.ToolBar.EnableTool(60, True)
#            self.ToolBar.EnableTool(70, False)
            runMenu.Enable(False)
            optMenu.Enable(False)

        elif mode ==1 :
            self.ToolBar.EnableTool(40, True)
            self.ToolBar.EnableTool(50, True)
            self.ToolBar.EnableTool(60, False)
#            self.ToolBar.EnableTool(70, True)
            runMenu.Enable(True)
            optMenu.Enable(True)

    def OnRunSimulation(self, event):
        """ Run epsc analytical simulation
        """

#        if self.controller.epscData.expData.checkFlagOn("exp") == False :
#            msg = "You should input experimental data!"
#            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
#            dlg.ShowModal()
#            dlg.Destroy()
#            return
        self.showPanel("simulation")

    def OnRunOptimization(self,event):
        """ Run optimization engine
        """
        if self.checkInputs()==0 :
            return
        if not self.controller.epscData.optData.checkFlagOn("optAlgorithm"):
            msg = "You should input optimization algorithm!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        if not self.controller.epscData.optData.checkFlagOn("optData"):
            msg = "You should input optimization data!"
            dlg = wx.MessageDialog(self, msg, "Warning", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return 0
        self.currentRun = 2
        self.centerPanels['plot'].clearError()
        self.OnPlot(None)
        self.plotPanel.disableButton()
        self.controller.runOptimizer(option='leastsq')
        self.controller.epscData.flagRun = True

    def OnCancelRun(self, event):
        self.controller.kill(self.currentRun)
        self.enableToolbar(1)

    def OnPreference(self, event):pass

    def OnToolClick(self, event):
        if event.GetId() == 40 :
            self.OnRunModel(event)

        elif event.GetId() == 50 :
            self.OnRunOptimization(event)

        elif event.GetId() == 60 :
            self.OnCancelRun(event)


    def OnPlot(self, event):

#        self.plotPanel.onPlot(None)
        self.showPanel("plot")


    def OnAbout(self,event):
        about = AboutBox(None, -1, "")
        about.ShowModal()

    def OnReport(self,event):
        report = ReportPanel(None, -1, "")
        report.ShowModal()


    def OnClose(self, event):
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()

    def OnRestorePerspective(self, event):

        self._mgr.LoadPerspective(self._perspectives[0])

    def clearPlots(self):
        self.centerPanels["plot"].clearPlot("macro")
        self.centerPanels["plot"].clearPlot("HKL-Long")
        self.centerPanels["plot"].clearPlot("HKL-Trans")
        self.centerPanels["plot"].clearPlot("errmonitor")

    def checkPhase(self, phaseNum):
        if self.phaseSet()[phaseNum]!="Opt" :
            if self.phaseSet()[phaseNum]!= self.phaseSet()[self.previousPhase] :
                return True
        else :
            return False

    def switchRightPanel(self, phaseNum, type="default"):
        if type=="Open":
            self.centerPanels[self.panelsData()[phaseNum]].createPages(type)
            self.centerPanels["Opt"].createPages()
        else :
            if self.checkPhase(phaseNum) and phaseNum != self.previousPhase:
                if self.checkForSave()!= wx.ID_CANCEL :
                    self.treePanel.clearTree()
                    self.controller.newEpscData()
                    self.centerPanels[self.panelsData()[phaseNum]].createPages(type)
                    self.centerPanels["Opt"].createPages()
                else :
                    return
            if self.flagClose == True :
                self.controller.newEpscData()
                self.centerPanels[self.panelsData()[phaseNum]].createPages(type)
                self.centerPanels["Opt"].createPages()
                self.flagClose = False
            if self.panelsData()[phaseNum] != "Opt" :
                self.previousPhase = phaseNum
                self.centerPanels[self.panelsData()[phaseNum]].nb.general.setProperties()

            if phaseNum == 2021 :
                self.centerPanels["2Phase1"].nb.general.showVolFrac()
            elif phaseNum == 2022 :
                self.centerPanels["2Phase2"].nb.general.showVolFrac()
#        elif self.phaseSet()[phaseNum] == "opt" :
#            self.ntOpt.nb.optBCC.showVoce()

        if self.controller.epscData.isAltered == True :
            if phaseNum == 201 :
                self.centerPanels["Phase1"].showData()

        self.showPanel(self.panelsData()[phaseNum])
        self._mgr.Update()

    def optMenuOn(self):
        item = self.GetMenuBar().FindItemById(401)
        item2 = self.GetMenuBar().FindItemById(402)
        item.Enable(True)
        item2.Enable(True)
        self.centerPanels["Opt"].showVoce()

    def showPanel(self, panelType):
        for key in self.centerPanels :
            self._mgr.GetPane(key).Show(panelType == key)
        self._mgr.Update()

class EpscApp(wx.App):
    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect, filename)

    def OnExit(self):
        self.ExitMainLoop()

if __name__=='__main__':
    App = EpscApp(redirect = False)
    frame = EpscGui(parent=None, id=-1, title="EPSC APP")
#    processing.freezeSupport()
    try:
        frame.Show()
        App.MainLoop()
    finally:
        del App

