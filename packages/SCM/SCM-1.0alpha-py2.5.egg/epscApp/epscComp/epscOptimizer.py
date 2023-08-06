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
from scipy import optimize
from scipy import *
import time
import sys

from epscEngine import EpscEngine
from setParameters import SetParameters
from collectData import CollectData
from plotEngine import PlotEngine
import config
import optimize as optimize2

from mystic.differential_evolution import DifferentialEvolutionSolver
from mystic.termination import ChangeOverGeneration, VTR
from mystic.strategy import Best1Exp, Rand1Exp, Best2Exp, Best2Exp
from mystic import getch, random_seed, VerboseSow
from mystic.scipy_optimize import NelderMeadSimplexSolver
from mystic.tools import Sow
from mystic.termination import CandidateRelativeTolerance as CRT

class EpscOptimizer:
    """ class which configure optimization and call optimizer
    """
    def __init__(self,epscData):

        self.epscData = epscData
#        self.controller = controller
        self.modlPar = SetParameters()
        self.colData = CollectData(self.epscData)
        self.epscEngine = EpscEngine()
        self.firstDraw = True
        self.flagKill = False
        self.flagConsole = False
        self.parNameList = []
        self.resultList = []
        self.errorList = []


    def setModelParameters(self):

        """ function which set up model parameters for optimization
        """
#        if self.epscData.phaseName == "1Phase" :
        for i in range(8) :
            for j in range(4) :
                self.modlPar.addPar(config.voce[i][j],0,self.epscData.matParam["Phase1"].voce[i][j],comment='Voce parameter for slip systems #' + str(i))
                self.modlPar.parDict[config.voce[i][j]].setActive(self.epscData.optData.voceFlag[i][j])

#            print "voce particle" + name + str(self.epscData.matParam.getMatrix("voceParticle",0,i))
#        if self.epscData.phaseNum != 201 :
#            i = 0
#            for name in self.vocePhase2Names() :
#                self.modlPar.addPar(name,0,float(self.epscData.matParam.getMatrix("voce2Phase2",0,i)),comment='Voce parameter for all slip systems')
#                self.modlPar.parDict[name].setActive(self.epscData.optData.getData(name))
#                i = i+1

    def collectData(self,typeOptimizer):
        """ Collect both the experimental data and model data and compare them
        """
#        count = 0
#        for i in range(8):
#            for j in range(4):
#                if self.epscData.optData.voceFlag[i][j]==1 :
#                    self.epscData.matParam.setMatrix("vocePhase1",i,j,p0[count])
#                    count+=1

        if self.epscData.optData.getData("expData") == 'macro' :
            if self.colData.collectMacroData()== -1:
                if not self.flagConsole :
                    self.tempQueue.put('Kill')
                    self.flagKill = True
#                print "in collectData"
            self.colData.collectMacroData()
            listError = self.colData.getErrorMacro(typeOptimizer)

        elif self.epscData.optData.getData("expData") == 'hkl'  :
            self.colData.collectHKLData()
            listError = self.colData.getErrorHKL(typeOptimizer)
        else :
            self.colData.collectMacroData()
            self.colData.collectHKLData()
            listError = self.colData.getErrorBoth(typeOptimizer)
        self.error = listError[0]


#        self.Parent.plotEngine.plotOptMacroTop(self.Parent.Parent,2)
#        self.Parent.plotEngine.plotOptHKLTop(self.Parent.Parent,2)
        self.tempQueue.put('error')
        self.tempQueue.put(listError[1])
        if not self.flagConsole :
            if self.flagKill == False :
                if self.firstDraw == True :
                    self.tempQueue.put('FirstDraw')
                    self.firstDraw = False
                else :
                    self.tempQueue.put('Draw')
                self.tempQueue.put(self.resultList.pop())
            time.sleep(1)
#        if self.firstDraw == True :
#            self.line = self.plotEngine.plotOptMacroTop(2,self.graph,None)
#            self.line_hkl = self.plotEngine.plotOptHKLTop(2,self.graph_hkl,None)
#            self.firstDraw = False
#        else :
#            if self.graph :
#                self.plotEngine.plotOptMacroTop(3,self.graph,self.line)
#            if self.graph_hkl :
#                self.plotEngine.plotOptHKLTop(3,self.graph_hkl,self.line_hkl)


    def func_leastsq(self,p0,opt):

        """ function which is required for optimizer
            what 'func' do is :
            1. setting up model parameters for optimization
            2. run epsc engine
            3. collect experimental data and modeling result and calculate error

            return : error between exp. and modeling data
        """

        self.parNameList = self.modlPar.setParVals(p0)
        print p0
        self.resultList.append(p0)
        self.modlPar.updateFiles()
        self.epscEngine.callEngine(mode="opt")
        self.collectData(0)
        print "Error:",self.error
        self.errorList.append(self.error)
        return self.error


    def func_fmin(self,p0):

        """ function which is required for optimizer
            what 'func' do is :
            1. setting up model parameters for optimization
            2. run epsc engine
            3. collect experimental data and modeling result and calculate error

            return : error between exp. and modeling data
        """

        self.parNameList = self.modlPar.setParVals(p0)
        print p0
        self.resultList.append(p0)
        self.modlPar.updateFiles()
        self.epscEngine.callEngine(mode="opt")
        self.collectData(1)
        print "Error:",self.error
        self.errorList.append(self.error)
        return self.error

    def func_mystic(self,p0):

        """ function which is required for optimizer
            what 'func' do is :
            1. setting up model parameters for optimization
            2. run epsc engine
            3. collect experimental data and modeling result and calculate error

            return : error between exp. and modeling data
        """

        self.modlPar.setParVals(array(p0))
        print p0
        self.resultList.append(p0)
        self.modlPar.updateFiles()
        self.epscEngine.callEngine(mode="opt")
        self.collectData(1)
        print "Error:",self.error
        self.errorList.append(self.error)
        return self.error


    def callOptimizer(self):
        """ function:
            1. select model parameters for optimization
            2. prepare parameters for calling optimizer
            3. call optimization function from scipy
        """

        self.setModelParameters()
        self.modlPar.selectPars()
        p0 = self.modlPar.getParVals()
        print p0
        lo = []
        hi = []
        for i in range(8):
            for j in range(4):
                if self.epscData.optData.voceFlag[i][j]==1 :
                    lo.append(float(self.epscData.optData.lowVoce[i][j]))
                    hi.append(float(self.epscData.optData.highVoce[i][j]))
        if self.epscData.optData.nameAlgorithm == "leastsq" :
            self.optResult = optimize.leastsq(self.func_leastsq,p0,self.epscData.optData.getData("expData"),epsfcn = 0.001 , ftol = 0.2)

        elif self.epscData.optData.nameAlgorithm == "fmin" :
            self.optResult = optimize.fmin(self.func_fmin,p0)
        elif self.epscData.optData.nameAlgorithm == "boxmin" :

            if self.epscData.optData.checkFlagOn("range") == False :
                return
            else :
                self.optResult = optimize2.simplex(self.func_fmin, p0, (lo,hi), ftol=1e-4)
        elif self.epscData.optData.nameAlgorithm == "fmin-mystic" :
#            solver = DifferentialEvolutionSolver(self.ND, self.NP)
#            stepmon = Sow()
#            solver.SetRandomInitialPoints(min = self.minrange, max = self.maxrange)
#            # set constraints of parameters
#            solver.Solve(self.func_mystic, Best1Exp,\
#                 termination = ChangeOverGeneration(generations=100),\
#                 maxiter= self.MAX_GENERATIONS, CrossProbability=0.5,\
#                 ScalingFactor=0.5, StepMonitor = stepmon)


            stepmon = Sow()
            evalmon = Sow()
            solver = NelderMeadSimplexSolver(len(p0))
            solver.SetInitialPoints(p0)
            solver.SetStrictRanges(lo,hi)
            solver.enable_signal_handler()
#            solver.SetEvaluationLimits(maxiter,maxfun)
            xtol = 0.0001
            ftol = 0.0001
            disp = 1
            solver.Solve(self.func_mystic,termination=CRT(xtol,ftol),\
                         EvaluationMonitor=evalmon,StepMonitor=stepmon,\
                         disp=disp, ExtraArgs=(), callback=None)
            solution = solver.Solution()

            self.optResult = solution


        elif self.epscData.optData.nameAlgorithm == "de" :
            xtol = 0.0001
            ftol = 0.0001
            NP =50    # dimension, population size
            MAX_GENERATIONS = 2500
            solver = DifferentialEvolutionSolver(len(p0),NP)
            stepmon = Sow()
            solver.SetInitialPoints(p0)
            # set constraints of parameters
#            solver.SetStrictRanges(lo,hi)
            solver.Solve(self.func_mystic, termination = CRT(xtol,ftol),\
                 maxiter= MAX_GENERATIONS, CrossProbability=0.5,\
                 ScalingFactor=0.5, StepMonitor = stepmon)
            self.optResult = solver.Solution()
        self.printResultFile()
        return self.optResult

    def callOptimizer2(self, tempQueue):
        """ function:
            1. select model parameters for optimization
            2. prepare parameters for calling optimizer
            3. call optimization function from scipy
        """
#        if tempQueue == None :
#            self.flagConsole = True
#        else :
        self.tempQueue = tempQueue
        self.firstDraw = True

        self.setModelParameters()
        self.modlPar.selectPars()
        p0 = self.modlPar.getParVals()
        print p0
        lo = []
        hi = []
        for i in range(8):
            for j in range(4):
                if self.epscData.optData.voceFlag[i][j]==1 :
                    lo.append(float(self.epscData.optData.lowVoce[i][j]))
                    hi.append(float(self.epscData.optData.highVoce[i][j]))
        if self.epscData.optData.nameAlgorithm == "leastsq" :
            self.optResult = optimize.leastsq(self.func_leastsq,p0,self.epscData.optData.getData("expData"),epsfcn = 0.001 , ftol = 0.2)

        elif self.epscData.optData.nameAlgorithm == "fmin" :
            self.optResult = optimize.fmin(self.func_fmin,p0)
        elif self.epscData.optData.nameAlgorithm == "boxmin" :

            if self.epscData.optData.checkFlagOn("range") == False :
                return
            else :
                self.optResult = optimize2.simplex(self.func_fmin, p0, (lo,hi), ftol=1e-4)
        elif self.epscData.optData.nameAlgorithm == "fmin-mystic" :
#            solver = DifferentialEvolutionSolver(self.ND, self.NP)
#            stepmon = Sow()
#            solver.SetRandomInitialPoints(min = self.minrange, max = self.maxrange)
#            # set constraints of parameters
#            solver.Solve(self.func_mystic, Best1Exp,\
#                 termination = ChangeOverGeneration(generations=100),\
#                 maxiter= self.MAX_GENERATIONS, CrossProbability=0.5,\
#                 ScalingFactor=0.5, StepMonitor = stepmon)


            stepmon = Sow()
            evalmon = Sow()
            solver = NelderMeadSimplexSolver(len(p0))
            solver.SetInitialPoints(p0)
            solver.SetStrictRanges(lo,hi)
            solver.enable_signal_handler()
#            solver.SetEvaluationLimits(maxiter,maxfun)
            xtol = 0.0001
            ftol = 0.0001
            disp = 1
            solver.Solve(self.func_mystic,termination=CRT(xtol,ftol),\
                         EvaluationMonitor=evalmon,StepMonitor=stepmon,\
                         disp=disp, ExtraArgs=(), callback=None)
            solution = solver.Solution()

            self.optResult = solution


        elif self.epscData.optData.nameAlgorithm == "de" :
            xtol = 0.0001
            ftol = 0.0001
            NP =50    # dimension, population size
            MAX_GENERATIONS = 2500
            solver = DifferentialEvolutionSolver(len(p0),NP)
            stepmon = Sow()
            solver.SetInitialPoints(p0)
            # set constraints of parameters
#            solver.SetStrictRanges(lo,hi)
            solver.Solve(self.func_mystic, termination = CRT(xtol,ftol),\
                 maxiter= MAX_GENERATIONS, CrossProbability=0.5,\
                 ScalingFactor=0.5, StepMonitor = stepmon)
            self.optResult = solver.Solution()
        self.printResultFile()
        return self.optResult

    def printResultFile(self):
        fid = open(config.dirTemp +"optLog.txt", "w")
        fid.write(' '.join(self.parNameList))
        fid.write('\n')
        for i in range(len(self.resultList)):
            fid.write(str(i+1) + " ")
            fid.write(str(self.resultList[i]))
            fid.write('\n')

        fid.write("Error:\n")
        for i in range(len(self.errorList)):
            fid.write(str(i+1) + " ")
            fid.write(str(self.errorList[i]))
            fid.write('\n')
        fid.write("Final result:")
        fid.write("\n")
#        fid.write(str(self.optResult))
        fid.close()