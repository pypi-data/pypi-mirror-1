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


import os,sys
import threading
import wx
import signal
from processing import Process,Queue,freezeSupport
from time import sleep

import epscComp.config
from epscComp.collectData import CollectData
from epscComp.plotEngine import PlotEngine
from epscComp.epscOptimizer import EpscOptimizer
from epscComp.epscEngine import EpscEngine
from epscComp.epscData import EpscData
#from epscComp.extendedplotframe import ExtendedPlotFrame
from epscComp.diffractionData import DiffractionData

_help = ''' Epsc command line help menu

-i: epsc model input file (define path and file name)
-x: crystal structure (BCC FCC or HCP)
-o: optimization algorithm (leastsq or fmin)
-d: optimization data set (macro only from cmd)
-p: optimization parameter set (list shown below)
-np: number of optimization parameters
-pval: value of optimization parameters
-e: experimental data file name

Parameters  TauZero(GPa)  TauOne(GPa)  ThetaZero(GPa)  ThetaOne(GPa)

BCC{110}      110v1         110v2           110v3           110v4
BCC{112}      112v1         112v2           112v3           112v4
BCC{123}      123v1         123v2           123v3           123v4
FCC{111}      111v1         111v2           111v3           111v4
HCP-BASAL     baslv1        baslv2          baslv3          baslv4
HCP-PRSM1     prs1v1        prs1v2          prs1v3          prs1v4
HCP-PRSM2     prs2v1        prs2v2          prs2v3          prs2v4
HCP-PYR1      pyr1v1        pyr1v2          pyr1v3          pyr1v4
HCP-PYR2      pyr2v1        pyr2v2          pyr2v3          pyr2v4
HCP-PYRC      pyrcv1        pyrcv2          pyrcv3          pyrcv4
HCP-PYRT      pyrtv1        pyrtv2          pyrtv3          pyrtv4

Examples:

1) running epsc engine from input file

python epscController.py -x BCC -i epscComp\epscCore\user\epscnp_BCC.in

python epscController.py -x FCC -i epscComp\epscCore\user\epscnp_FCC.in

python epscController.py -x HCP -i epscComp\epscCore\user\epscnp_HCP.in

2) running epsc eingine with optimization options

python epscController.py -x BCC -i epscComp\epscCore\user\epscnp.in -e epscComp\epscCore\user\Exp_Example_BCC.dat -o leastsq -np 2 -p 110v1 110v2 -pval 0.2 0.2

python epscController.py -x FCC -i epscComp\epscCore\user\epscnp_FCC.in -e epscComp\epscCore\user\Exp_Example_FCC.dat -o leastsq -np 2 -p 111v1 111v2 -pval 0.05 0.02

python epscController.py -x HCP -i epscComp\epscCore\user\epscnp_HCP.in -e epscComp\epscCore\user\Exp_Example_HCP.dat -o leastsq -np 2 -p baslv1 baslv2  -pval 0.2 0.2


'''

class EpscController(object):

    """
        EpscController is the class which controls all the function behind GUI
        It also support command line operation.
        members: epscData  => data class which has all the data of the project
             modlPar => model parameters class
             epscEngine
             epscOpt => epsc optimization class
    """

    def __init__(self, Parent):

        self.Parent = Parent
        self.epscData = EpscData()
        self.epscOpt = EpscOptimizer(self.epscData)
        self.epscEngine = EpscEngine()
        self.plotEngine = PlotEngine(self)
        self.optResult = []
        self.flagKill = False

    def newEpscData(self):
        self.epscData = EpscData()
        self.epscOpt.epscData = self.epscData
        self.epscOpt.colData.epscData = self.epscData

    def runEpscEngine(self,mode):

        """ function which make EPSC Engine run with user input model parameters
        """

        self.epscEngine.callEngine("run")
        if mode!="file" :
            self.Parent.plotPanel.enableButton()

    def func_draw(self):

        while 1:
            if (self.sigQueue.empty()) and self.flagKill == False:
                wx.MutexGuiEnter()
                self.Parent.plotPanel.gauge.Pulse()
                wx.MutexGuiLeave()
                sleep(0.1)
                continue
            item = self.sigQueue.get()
            if item == 'Stop':
                wx.MutexGuiEnter()
                self.Parent.plotPanel.enableButton()
                self.Parent.enableToolbar(1)
                wx.MutexGuiLeave()
                self.flagKill == True
                break
            elif item == 'Result':
                self.flagKill = True
                result = self.sigQueue.get()
                wx.MutexGuiEnter()
                self.Parent.enableToolbar(1)
                self.Parent.plotPanel.enableButton()
                wx.MutexGuiLeave()
            elif item =='Kill':
                self.flagKill = True
                self.optProcess.terminate()
                print "Optimization process stopped."
                wx.MutexGuiEnter()
                self.Parent.enableToolbar(1)
                self.Parent.plotPanel.enableButton()
                wx.MutexGuiLeave()
            elif item == 'FirstDraw':
                wx.MutexGuiEnter()
                self.Parent.plotPanel.gauge.Pulse()
                self.plotEngine.plotOptMacroTop(self.Parent,2)
                self.plotEngine.plotOptHKLTop(self.Parent,2)
                if self.epscData.phaseNum != 201 :
                    self.plotEngine.plotOptHKLTop(self.Parent,2)
                self.Parent.centerPanels["Opt"].updateParams(self.sigQueue.get())
                wx.MutexGuiLeave()
            elif item == 'RunDraw':
                try :
                    wx.MutexGuiEnter()
                    self.Parent.enableToolbar(1)
                    self.plotEngine.plotOptMacroTop(self.Parent,2)
                    self.plotEngine.plotOptHKLTop(self.Parent,2)
                    if self.epscData.phaseNum != 201 :
                        self.plotEngine.plotOptHKLTop(self.Parent,2)
                    wx.MutexGuiLeave()
                except :
                    return
                self.flagKill == True
                
                break
            elif item == 'Draw':
                wx.MutexGuiEnter()
                self.Parent.plotPanel.gauge.Pulse()
                self.plotEngine.plotOptMacroTop(self.Parent,2)
                self.plotEngine.plotOptHKLTop(self.Parent,2)

                if self.epscData.phaseNum != 201 :
                    self.plotEngine.plotOptHKLTop(self.Parent,2)
                self.Parent.centerPanels["Opt"].updateParams(self.sigQueue.get())
                wx.MutexGuiLeave()
            elif item == 'error':
                error = self.sigQueue.get()
                wx.MutexGuiEnter()
                self.Parent.centerPanels["plot"].addError(error)
                wx.MutexGuiLeave()
    def func_draw_console(self):
        app = MyApp(0)
        self.graph = app.graph
        self.graph_hkl = app.graph_hkl
        try :
            app.MainLoop()
        except SystemExit:
            return

    def func_opt(self):
        self.Parent.OnPlot(None)
        optResult = self.epscOpt.callOptimizer()

    def runOptimizer(self, option='leastsq', mode="opt"):

#        self.Parent.OnPlot(None)
#        optResult = self.epscOpt.callOptimizer()

#        self.optThread = OptThread(target=self.func_opt)
#        self.optThread.start()

        self.argQueue = Queue()
        self.sigQueue = Queue()
        if os.name != "posix" :
            sys.executable = r'C:\Python25\python.exe'
            sys.frozen = False
        self.Parent.enableToolbar(0)
#        self.epscOpt.epscData = self.epscData
#        print self.epscOpt.epscData.expData.expFile
        if mode == 'run':

            self.argQueue.put(self.epscEngine)
            self.optProcess = Process(target= f_run, args=(self.argQueue,self.sigQueue))
        else :

            self.argQueue.put(self.epscOpt)
            self.optProcess = Process(target= f_opt, args=(self.argQueue,self.sigQueue))

        self.optProcess.start()
        sys.frozen = True

        self.drawThread = DrawThread(target=self.func_draw)
        self.drawThread.start()

    def kill(self,mode):
        if mode==1:
            self.epscEngine.killProcess()
        elif mode==2:
#            pass
            self.epscOpt.printResultFile()
            print "Optimization process stopped."
            self.sigQueue.put('Stop')
            self.optProcess.terminate()


    def runOptFromConsole(self):

        self.sigQueue = Queue()
        self.drawThread = DrawThread(target=self.func_draw_console)
        self.drawThread.start()
        self.drawThread2 = DrawThread(target=self.func_draw)
        self.drawThread2.start()

        print self.epscOpt.callOptimizer2(self.sigQueue)
        raise SystemExit

    def start_file(self, arg):
        """ Run engine from scripting mode
        """
        dictCopy = {"nt":"copy ", "posix":"cp "}
        dictCrystal = {"BCC":0,"FCC":1,"HCP":2}
        phase = "Phase1"
        opts = self.getOpts(arg)
        print opts

        if opts.has_key("-help") or len(opts) == 0 :
            print _help
            return
        if not opts.has_key("-i"):
            print "Epsc : needs input file (-i) \nUsage : epsc -help"
            return

        ind1 = opts["-i"].rfind("\\")
        dir = opts["-i"][0:ind1]
        fid = open(opts["-i"],"r")
        strCopy = " " + dir + "\\"
        strAll = ""
        while fid :
            line = fid.readline()
            strAll += line
            if not line : break
            if line.find("material data")>=0 :
                matFile = fid.readline()
                matFile = matFile[0:len(matFile)-1]
                self.epscData.generalData.materialFile["Phase1"] = matFile
                strAll += "Material_1.sx\n"
                os.system(dictCopy[os.name] + strCopy + matFile + ' "' + \
                          epscComp.config.dirEpscCore + matFile + '"')
#                print dictCopy[os.name] + strCopy + matFile + ' ' + epscComp.config.dirEpscCore + matFile
                self.makeOptTemplate()
            if line.find("shape+texture")>=0 :
                texFile = fid.readline()
                strAll += texFile
                texFile = texFile[0:len(texFile)-1]
                os.system(dictCopy[os.name] + strCopy + texFile + ' "' + \
                          epscComp.config.dirEpscCore + texFile + '"')

            if line.find("diffraction")>=0 :
                strAll += fid.readline()
                diffFile = fid.readline()
                strAll += diffFile
                diffFile = diffFile[0:len(diffFile)-1]
                os.system(dictCopy[os.name] + strCopy + diffFile + ' "' + \
                          epscComp.config.dirEpscCore + diffFile + '"')
                self.epscData.generalData.diffractionFile[phase] = diffFile.replace("\n","")
                self.setEpscDataDiffraction(opts["-x"])
            if line.find("Number of thermomechanical")>=0 :
                line = fid.readline()
                strAll += line
                processNum = int(line.split()[0])
                strAll += fid.readline()
                processFile = []
                for i in range(processNum):
                    proTemp = fid.readline()
                    strAll += proTemp
                    proTemp = proTemp[0:len(proTemp)-1]
                    processFile.append(proTemp)
                    os.system(dictCopy[os.name] + strCopy + processFile[i] \
                              + ' "' + epscComp.config.dirEpscCore + processFile[i] + '"')
        fid.close()
        fid = open(epscComp.config.dirEpscCore + "epscnp.in", "w")
        fid.write(strAll)
        fid.close()
#        os.system(dictCopy[os.name] + opts["-i"] + ' "' + epscComp.config.dirEpscCore + 'epscnp.in"')
        if not opts.has_key("-o") : # engine run
            self.runEpscEngine("file")
        else : # optimization
            self.epscData.optData.nameAlgorithm = opts["-o"]
            if not opts.has_key("-x") :
                print "Epsc : needs type of crystal structure (-x) \nUsage : epsc -help"
                return
            else :
                self.epscData.matParam["Phase1"].typeCrystal = dictCrystal[opts["-x"]]
            if not opts.has_key("-e") :
                print "Epsc : needs experimental file (-e) \nUsage : epsc -help"
                return
            else :
                ind1 = opts["-e"].rfind("\\")
                dir = opts["-e"][0:ind1]
                expFile = opts["-e"][ind1:]
                self.epscData.expData.expFile = epscComp.config.dirEpscCore + expFile

                os.system(dictCopy[os.name] + " " + opts["-e"] + ' "' + epscComp.config.dirEpscCore + expFile + '"')

                self.epscData.expData.turnOnFlag("expData")
            if not opts.has_key("-np") :
                print "Epsc : needs the number of parameters to optimize(-np) \nUsage : epsc -help"
                return
            else :
                numParams = opts["-np"]
            if not opts.has_key("-p") or not opts.has_key("-pval") :
                print "Epsc : needs voce parameters to optimize (-p, -pval) \nUsage : epsc -help"
                return
            else :
                for i in range(int(numParams)):
                    if self.epscData.matParam["Phase1"].typeCrystal == 0 :
                        if opts["-p"][i]=='110v1':
                            self.epscData.optData.voceFlag[0][0]=1
                            self.epscData.matParam[phase].voce[0][0] = opts["-pval"][i]
                        if opts["-p"][i]=='110v2':
                            self.epscData.optData.voceFlag[0][1]=1
                            self.epscData.matParam[phase].voce[0][1] = opts["-pval"][i]
                        if opts["-p"][i]=='110v3':
                            self.epscData.optData.voceFlag[0][2]=1
                            self.epscData.matParam[phase].voce[0][2] = opts["-pval"][i]
                        if opts["-p"][i]=='110v4':
                            self.epscData.optData.voceFlag[0][3]=1
                            self.epscData.matParam[phase].voce[0][3] = opts["-pval"][i]
                        if opts["-p"][i]=='112v1':
                            self.epscData.optData.voceFlag[1][0]=1
                            self.epscData.matParam[phase].voce[1][0] = opts["-pval"][i]
                        if opts["-p"][i]=='112v2':
                            self.epscData.optData.voceFlag[1][1]=1
                            self.epscData.matParam[phase].voce[1][1] = opts["-pval"][i]
                        if opts["-p"][i]=='112v3':
                            self.epscData.optData.voceFlag[1][2]=1
                            self.epscData.matParam[phase].voce[1][2] = opts["-pval"][i]
                        if opts["-p"][i]=='112v4':
                            self.epscData.optData.voceFlag[1][3]=1
                            self.epscData.matParam[phase].voce[1][3] = opts["-pval"][i]
                        if opts["-p"][i]=='123v1':
                            self.epscData.optData.voceFlag[2][0]=1
                            self.epscData.matParam[phase].voce[2][0] = opts["-pval"][i]
                        if opts["-p"][i]=='123v2':
                            self.epscData.optData.voceFlag[2][1]=1
                            self.epscData.matParam[phase].voce[2][1] = opts["-pval"][i]
                        if opts["-p"][i]=='123v3':
                            self.epscData.optData.voceFlag[2][2]=1
                            self.epscData.matParam[phase].voce[2][2] = opts["-pval"][i]
                        if opts["-p"][i]=='123v4':
                            self.epscData.optData.voceFlag[2][3]=1
                            self.epscData.matParam[phase].voce[2][3] = opts["-pval"][i]
                    if self.epscData.matParam["Phase1"].typeCrystal == 1 :
                        if opts["-p"][i]=='111v1':
                            self.epscData.optData.voceFlag[0][0]=1
                            self.epscData.matParam[phase].voce[0][0] = opts["-pval"][i]
                        if opts["-p"][i]=='111v2':
                            self.epscData.optData.voceFlag[0][1]=1
                            self.epscData.matParam[phase].voce[0][1] = opts["-pval"][i]
                        if opts["-p"][i]=='111v3':
                            self.epscData.optData.voceFlag[0][2]=1
                            self.epscData.matParam[phase].voce[0][2] = opts["-pval"][i]
                        if opts["-p"][i]=='111v4':
                            self.epscData.optData.voceFlag[0][3]=1
                            self.epscData.matParam[phase].voce[0][3] = opts["-pval"][i]
                    if self.epscData.matParam[phase].typeCrystal == 2 :
                        if opts["-p"][i]=='baslv1':
                            self.epscData.optData.voceFlag[0][0]=1
                            self.epscData.matParam[phase].voce[0][0] = opts["-pval"][i]
                        if opts["-p"][i]=='baslv2':
                            self.epscData.optData.voceFlag[0][1]=1
                            self.epscData.matParam[phase].voce[0][1] = opts["-pval"][i]
                        if opts["-p"][i]=='baslv3':
                            self.epscData.optData.voceFlag[0][2]=1
                            self.epscData.matParam[phase].voce[0][2] = opts["-pval"][i]
                        if opts["-p"][i]=='baslv4':
                            self.epscData.optData.voceFlag[0][3]=1
                            self.epscData.matParam[phase].voce[0][3] = opts["-pval"][i]
                        if opts["-p"][i]=='prs1v1':
                            self.epscData.optData.voceFlag[1][0]=1
                            self.epscData.matParam[phase].voce[1][0] = opts["-pval"][i]
                        if opts["-p"][i]=='prs1v2':
                            self.epscData.optData.voceFlag[1][1]=1
                            self.epscData.matParam[phase].voce[1][1] = opts["-pval"][i]
                        if opts["-p"][i]=='prs1v3':
                            self.epscData.optData.voceFlag[1][2]=1
                            self.epscData.matParam[phase].voce[1][2] = opts["-pval"][i]
                        if opts["-p"][i]=='prs1v4':
                            self.epscData.optData.voceFlag[1][3]=1
                            self.epscData.matParam[phase].voce[1][3] = opts["-pval"][i]
                        if opts["-p"][i]=='prs2v1':
                            self.epscData.optData.voceFlag[2][0]=1
                            self.epscData.matParam[phase].voce[2][0] = opts["-pval"][i]
                        if opts["-p"][i]=='prs2v2':
                            self.epscData.optData.voceFlag[2][1]=1
                            self.epscData.matParam[phase].voce[2][1] = opts["-pval"][i]
                        if opts["-p"][i]=='prs2v3':
                            self.epscData.optData.voceFlag[2][2]=1
                            self.epscData.matParam[phase].voce[2][2] = opts["-pval"][i]
                        if opts["-p"][i]=='prs2v4':
                            self.epscData.optData.voceFlag[2][3]=1
                            self.epscData.matParam[phase].voce[2][3] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr1v1':
                            self.epscData.optData.voceFlag[3][0]=1
                            self.epscData.matParam[phase].voce[3][0] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr1v2':
                            self.epscData.optData.voceFlag[3][1]=1
                            self.epscData.matParam[phase].voce[3][1] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr1v3':
                            self.epscData.optData.voceFlag[3][2]=1
                            self.epscData.matParam[phase].voce[3][2] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr1v4':
                            self.epscData.optData.voceFlag[3][3]=1
                            self.epscData.matParam[phase].voce[3][3] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr2v1':
                            self.epscData.optData.voceFlag[4][0]=1
                            self.epscData.matParam[phase].voce[4][0] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr2v2':
                            self.epscData.optData.voceFlag[4][1]=1
                            self.epscData.matParam[phase].voce[4][1] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr2v3':
                            self.epscData.optData.voceFlag[4][2]=1
                            self.epscData.matParam[phase].voce[4][2] = opts["-pval"][i]
                        if opts["-p"][i]=='pyr2v4':
                            self.epscData.optData.voceFlag[4][3]=1
                            self.epscData.matParam[phase].voce[4][3] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrcv1':
                            self.epscData.optData.voceFlag[5][0]=1
                            self.epscData.matParam[phase].voce[5][0] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrcv2':
                            self.epscData.optData.voceFlag[5][1]=1
                            self.epscData.matParam[phase].voce[5][1] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrcv3':
                            self.epscData.optData.voceFlag[5][2]=1
                            self.epscData.matParam[phase].voce[5][2] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrcv4':
                            self.epscData.optData.voceFlag[5][3]=1
                            self.epscData.matParam[phase].voce[5][3] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrtv1':
                            self.epscData.optData.voceFlag[6][0]=1
                            self.epscData.matParam[phase].voce[6][0] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrtv2':
                            self.epscData.optData.voceFlag[6][1]=1
                            self.epscData.matParam[phase].voce[6][1] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrtv3':
                            self.epscData.optData.voceFlag[6][2]=1
                            self.epscData.matParam[phase].voce[6][2] = opts["-pval"][i]
                        if opts["-p"][i]=='pyrtv4':
                            self.epscData.optData.voceFlag[6][3]=1
                            self.epscData.matParam[phase].voce[6][3] = opts["-pval"][i]
            self.runOptFromConsole()

    def setEpscDataDiffraction(self, typeCrystal):
        fid = open(epscComp.config.dirEpscCore + self.epscData.generalData.diffractionFile["Phase1"], 'r')
        line = fid.readline()
        while fid:
            line = fid.readline()
            if not line : break
            if line.find('Number of diffraction')>=0 :
                line =fid.readline().split()
                self.epscData.numDiffractionData["Phase1"] = int(line[0])
                line = fid.readline()
            if line.find('Plane type')>=0 :
                line = fid.readline()

                while 1 :
                    line = fid.readline()
                    if not line: break
                    data = line.split()

                    if typeCrystal == "HCP" :
                        # ex. if "crystalPhase1" is HCP
                        name = data[0] + data[1] + data[2] + data[3]
                        chi = data[4]
                        eta = data[5]
                    else :
                        name = data[0] + data[1] + data[2]
                        chi = data[3]
                        eta = data[4]
                    if float(chi) == 0 and float(eta) == 0  :
                        angle = "Long"
                        self.epscData.numDiffractionData[angle + "Phase1"] +=1
                    elif float(chi) == 90 and float(eta) == 0  :
                        angle = "Trans"
                        self.epscData.numDiffractionData[angle + "Phase1"] +=1
                    else :
                        angle = "Rolling"
                        self.epscData.numDiffractionData[angle + "Phase1"] +=1
                    diff = DiffractionData(name,chi,eta,angle)
                    self.epscData.listDiffractionData["Phase1"].append(diff)
                    self.epscData.listDiffractionData[angle + "Phase1"].append(diff)


    def getOpts(self, arg):
        """ Get arguments from scripting mode
        """
        opts = {}
        while arg:
            if arg[0][0] == '-':
                if arg[0] == "-p":
                    opts["-p"] = []
                    for i in range(int(opts["-np"])):
                        opts["-p"].append(arg[i+1])
                    arg = arg[int(opts["-np"])+1:]
                elif arg[0] == "-pval" :
                    i=0
                    opts["-pval"] = []
                    for i in range(int(opts["-np"])):
                        opts["-pval"].append(float(arg[i+1]))
                    arg = arg[int(opts["-np"])+1:]
                else :
                    opts[arg[0]] = arg[1]
                    arg = arg[2:]
            else:
                arg = arg[1:]
        return opts
    def makeOptTemplate(self):
        fid = open(epscComp.config.dirEpscCore+self.epscData.generalData.materialFile["Phase1"], "r")
        voce = ["$Voce_SS1_1 $Voce_SS1_2 $Voce_SS1_3 $Voce_SS1_4\n",
         "$Voce_SS2_1 $Voce_SS2_2 $Voce_SS2_3 $Voce_SS2_4\n",
        "$Voce_SS3_1 $Voce_SS3_2 $Voce_SS3_3 $Voce_SS3_4\n",
        "$Voce_SS4_1 $Voce_SS4_2 $Voce_SS4_3 $Voce_SS4_4\n",
        "$Voce_SS5_1 $Voce_SS5_2 $Voce_SS5_3 $Voce_SS5_4\n",
         "$Voce_SS6_1 $Voce_SS6_2 $Voce_SS6_3 $Voce_SS6_4\n",
        "$Voce_SS7_1 $Voce_SS7_2 $Voce_SS7_3 $Voce_SS7_4\n",
        "$Voce_SS8_1 $Voce_SS8_2 $Voce_SS8_3 $Voce_SS8_4\n"]
        strAll = ""
        i=0
        count=0
        while fid :
            line = fid.readline()
            if not line:
                break

            if line.find('*') <0 and (line.lower().find('slip')>=0 or line.lower().find('twin')>=0) :
                strAll += line
                line = fid.readline()
                strAll += line
                listVoce = fid.readline().split()
                for j in range(4):
                    self.epscData.matParam["Phase1"].voce[count][j] = float(listVoce[j])
                count +=1
                strAll += voce[i]
                i += 1
            else:
                strAll += line
        fid.close()
#        print strAll
        fid = open(epscComp.config.dirEpscCore + "template_MATERIAL_Phase1_opt.sx", 'w')
        fid.write(strAll)
        fid.close()

def f_run(argQueue,sigQueue):
    epscEngine = argQueue.get()
    epscEngine.callEngine("run",sigQueue)


def f_opt(argQueue,sigQueue):

    epscOpt = argQueue.get()

    optResult = epscOpt.callOptimizer2(sigQueue)
    sigQueue.put("Result")
    sigQueue.put(optResult)
    print "Optimization is now finished.\n"
    print "Result : "
    print optResult

class DrawThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)

class OptThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)


class MyApp(wx.App):
    def OnInit(self):
#        self.graph = epscComp.extendedplotframe.ExtendedPlotFrame(None)
#        self.graph.Show(True)
#        self.graph_hkl = epscComp.extendedplotframe.ExtendedPlotFrame(None)
#        self.graph_hkl.Show(True)
        return True

if __name__ == '__main__':
    appEpsc = EpscController(None)
#    old_signal = signal.signal(signal.SIGINT, handler)
#    sys.argv = ['-i','user\epscnp.in','-o','fmin','-np','2','-p','110v1','110v2','-pval','0.3','0.3','-x','BCC','-e','Exp_Example_BCC.dat']
#    sys.argv = ['-i','user\epscnp.in']
    appEpsc.start_file(sys.argv)


