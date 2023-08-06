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

#from pylab import *
from scipy import *

import interpolateFunction
import utility
import config
import string
import os
import sys
import wx


class CollectData:

    """ data preparation for optimization
        get experimental data and model data
    """
    def __init__(self, epscData):
        self.epscData = epscData
        self.flagEpsc3 = False
        self.flagEpsc9 = False
        self.omega = 1
        self.prefixPh1 = "ph1ref0"
        self.prefixPh2 = "ph2ref0"
        self.HKLMdlX = []

    def collectMacroData(self):
        # opt points in macro is strain, then compare stress

        self.collectExpData()

        self.epscData.expData.macroExpX=self.epscData.expData.macroExpX[::-1]
        self.epscData.expData.macroExpY=self.epscData.expData.macroExpY[::-1]

        if self.collectMacroModelData()==-1 :
            return -1

           # reverse data order for correct interpolation

        self.macroMdlY = interpolateFunction.splineInterp1D(self.macroMdlX,self.macroMdlY,self.epscData.expData.macroExpX)
        self.macroMdlX = self.epscData.expData.macroExpX

    def collectMacroModelData(self):
        # opt points in macro is strain, then compare stress

        dataModelMacro = utility.readModelHKL(config.dirEpscCore + "epsc9.out")
        if dataModelMacro == -1 :
            return -1
        self.macroMdlX = dataModelMacro['eps33']*100
        self.macroMdlY = dataModelMacro['sig33']*1000

        self.macroMdlX=self.macroMdlX[::-1]
        self.macroMdlY=self.macroMdlY[::-1]
        return 1

    def collectHKLData(self):
        # opt points in macro is stress, then compare strain

        self.collectExpData()
        self.collectHKLModelData()

        orgHKLExpY = self.epscData.expData.HKLExpY
        self.epscData.expData.HKLExpY = self.epscData.expData.HKLExpY[::-1]
        j=0;k=0
        for i in range(self.epscData.numDiffractionData["Phase1"]) :
            HKLExpX = []
            HKLExpY = []
            m=0
            min = self.HKLMdlX["Phase1"][i][0]
            for m in range(len(self.HKLMdlX["Phase1"][i])):
                if min > self.HKLMdlX["Phase1"][i][m]:
                    min = self.HKLMdlX["Phase1"][i][m]
            m = 0
            for m in range(len(self.epscData.expData.HKLExpX["Phase1"][i])):
                if self.epscData.expData.HKLExpX["Phase1"][i][m]>=min:
                    HKLExpX.append(self.epscData.expData.HKLExpX["Phase1"][i][m])
                    HKLExpY.append(orgHKLExpY[m])
            self.epscData.expData.HKLExpX["Phase1"][i] = []
            self.epscData.expData.HKLExpY  = []
            self.epscData.expData.HKLExpX["Phase1"][i] = HKLExpX
            self.epscData.expData.HKLExpY  = HKLExpY
            self.epscData.expData.HKLExpX["Phase1"][i] = self.epscData.expData.HKLExpX["Phase1"][i][::-1]
            self.epscData.expData.HKLExpY = self.epscData.expData.HKLExpY[::-1]
            if i < self.epscData.numDiffractionData["Phase1_exp"]:
                self.epscData.expData.HKLExpX["Phase1"][i] = self.epscData.expData.HKLExpX["Phase1"][i][::-1]
                self.HKLMdlX["Phase1"][i] = interpolateFunction.splineInterp1D(self.HKLMdlY,self.HKLMdlX["Phase1"][i],self.epscData.expData.HKLExpY)
            if i < self.epscData.numDiffractionData["TransPhase1"]:
                if len(self.epscData.expData.HKLExpX["TransPhase1"])>i :
                    self.epscData.expData.HKLExpX["TransPhase1"][i] = self.epscData.expData.HKLExpX["TransPhase1"][i][::-1]
                    self.HKLMdlX["TransPhase1"][i] = self.HKLMdlX["Phase1"][i]
            elif i < self.epscData.numDiffractionData["TransPhase1"] + self.epscData.numDiffractionData["LongPhase1"]:
                if len(self.epscData.expData.HKLExpX["LongPhase1"])>j :
                    self.HKLMdlX["LongPhase1"][j] = self.HKLMdlX["Phase1"][i]
                    self.epscData.expData.HKLExpX["LongPhase1"][j] = self.epscData.expData.HKLExpX["Phase1"][i]

#                    print HKLExpX
                    j+=1
            else :
                if len(self.epscData.expData.HKLExpX["RollingPhase1"])>k :
                    self.epscData.expData.HKLExpX["RollingPhase1"][k] = self.epscData.expData.HKLExpX["RollingPhase1"][k][::-1]

                    self.HKLMdlX["RollingPhase1"][k] = self.HKLMdlX["Phase1"][i]
                    k+=1

        self.HKLMdlY  = self.epscData.expData.HKLExpY

    def collectHKLModelData(self):
        # opt points in macro is stress, then compare strain

        dataModelHKL = utility.readModelHKL_phase1(config.dirEpscCore + "epsc9.out")
        self.HKLMdlX = {"Phase1":[],"Phase2":[],"LongPhase1":[],"TransPhase1":[],"RollingPhase1":[],"LongPhase2":[],"TransPhase2":[],"RollingPhase2":[]}
        j=0; k=0
        for i in range(self.epscData.numDiffractionData["Phase1"]):
            if i<9 :
                postfix = "0" + str(i+1)
            else :
                postfix = str(i+1)
#            print self.prefixPh1 + postfix
#            print dataModelHKL[self.prefixPh1 + postfix]
            self.HKLMdlX["Phase1"].append(dataModelHKL[self.prefixPh1 + postfix]*100)

            self.HKLMdlX["Phase1"][i] = self.HKLMdlX["Phase1"][i][::-1]
            if i < self.epscData.numDiffractionData["TransPhase1"]:
                self.HKLMdlX["TransPhase1"].append(dataModelHKL[self.prefixPh1 + postfix]*100)
                self.HKLMdlX["TransPhase1"][i] = self.HKLMdlX["TransPhase1"][i][::-1]
            elif i < self.epscData.numDiffractionData["TransPhase1"] + self.epscData.numDiffractionData["LongPhase1"]:
                self.HKLMdlX["LongPhase1"].append(dataModelHKL[self.prefixPh1 + postfix]*100)
                self.HKLMdlX["LongPhase1"][j] = self.HKLMdlX["LongPhase1"][j][::-1]
                j+=1
            else :
                self.HKLMdlX["RollingPhase1"].append(dataModelHKL[self.prefixPh1 + postfix]*100)
                self.HKLMdlX["RollingPhase1"][k] = self.HKLMdlX["RollingPhase1"][k][::-1]
                k+=1

        self.HKLX2 = dataModelHKL['eps33']
        self.HKLMdlY = dataModelHKL['sig33']*1000
        self.HKLMdlY = self.HKLMdlY[::-1]

        if self.epscData.phaseNum != 201 :
            for i in range(self.epscData.numDiffractionData["Phase2"]):
                if i<9 :
                   postfix = "0" + str(i+1)
                else :
                    postfix = str(i+1)
                self.HKLMdlX["Phase2"].append(dataModelHKL[self.prefixPh2 + postfix])
                self.HKLMdlX["Phase2"][self.epscData.numDiffractionData["Phase1"]+i] = self.HKLMdlX["Phase2"][self.epscData.numDiffractionData["Phase1"]+i][::-1]

    def collectExpData(self):

        dataExp,labels = utility.readExp(self.epscData.expData.expFile)
#        print self.epscData.expData.expFile
#            print dataExp
#        print labels
        self.epscData.expData.macroExpX = dataExp["Macro_Strain"]
        self.epscData.expData.macroExpY = dataExp["Macro_Stress"]
        self.epscData.expData.macroExpY_error = dataExp["Macro_Stress_Error"]
        self.epscData.expData.HKLExpY  = self.epscData.expData.macroExpY
        countExp = 0
        self.epscData.numDiffractionData["LongPhase1_exp"] = 0
        self.epscData.numDiffractionData["TransPhase1_exp"] = 0
        self.epscData.numDiffractionData["RollingPhase1_exp"] = 0
        self.epscData.listDiffractionData["LongPhase1_exp"] = []
        self.epscData.listDiffractionData["TransPhase1_exp"] = []
        self.epscData.listDiffractionData["RollingPhase1_exp"] = []
        for i in range(self.epscData.numDiffractionData["Phase1"]) :
            diffraction = self.epscData.listDiffractionData["Phase1"][i]
#                print diffraction.name + "_" + diffraction.angle
            if dataExp.has_key(diffraction.name + "_" + diffraction.angle) :
                countExp +=1
                self.epscData.listDiffractionData["Phase1_exp"].append(diffraction)
                self.epscData.numDiffractionData[diffraction.angle + "Phase1_exp"] +=1
                self.epscData.listDiffractionData[diffraction.angle + "Phase1_exp"].append(diffraction)
                self.epscData.expData.HKLExpX["Phase1"].append(dataExp[diffraction.name + "_" + diffraction.angle]*0.0001)
                self.epscData.expData.HKLExpX_error["Phase1"].append(dataExp[diffraction.name + "_"+ diffraction.angle + "_Error"]*0.0001)
                self.epscData.expData.HKLExpX[diffraction.angle + "Phase1"].append(dataExp[diffraction.name + "_" + diffraction.angle]*0.0001)
                self.epscData.expData.HKLExpX_error[diffraction.angle + "Phase1"].append(dataExp[diffraction.name + "_"+ diffraction.angle + "_Error"]*0.0001)
        self.epscData.numDiffractionData["Phase1_exp"] = countExp

#        except:
#            msg = "The diffraction Data you entered and experiment file do not match!"
#            dlg = wx.MessageDialog(None, msg, "Warning", wx.OK)
#            dlg.ShowModal()
#            dlg.Destroy()
#            return

    def getErrorMacro(self,typeOptimizer):

        errorMacroFmin = 0.
        i=0
        for exp in self.epscData.expData.macroExpY :
            mdl = self.macroMdlY[i]
            i +=1
            dy = exp - mdl
            errorMacroFmin += dy*dy
        mse = errorMacroFmin/i
        if typeOptimizer == 0 : # leastsq optimizer
            errorMacro = (self.epscData.expData.macroExpY - self.macroMdlY)/self.epscData.expData.macroExpY_error
        else :
            errorMacro = errorMacroFmin
        # fmin optimizer

#        fid = open("opt_result_macro.txt", "a")
#        origStdout = sys.stdout
#        sys.stdout = fid
#        fid.write("errorMacro:" )
#        print errorMacro
#        fid.close()
#        sys.stdout = origStdout
        return [errorMacro,mse]

    def getErrorHKL(self,typeOptimizer):
        tempExp = []
        tempMdl = []

        for i in range(self.epscData.numDiffractionData["Phase1"]) :
            if self.epscData.listDiffractionData["Phase1"][i].flagOn :
                tempExp += list(self.epscData.expData.HKLExpX["Phase1"][i])
                tempMdl += list(self.HKLMdlX["Phase1"][i])
        error_Exp_HKL_X = array(tempExp)
        error_Mdl_HKL_X = array(tempMdl)
        print tempExp
        print tempMdl
        errorHKLFmin = 0.
        for i in range(len(tempMdl)):
            dy = tempMdl[i] - tempExp[i]
            errorHKLFmin += dy * dy

        mse = errorHKLFmin/len(tempMdl)
        if typeOptimizer == 0 :
            errorHKL = error_Exp_HKL_X - error_Mdl_HKL_X
        else :
            errorHKL = mse

        return [errorHKL,mse]

    def getErrorHKL_new(self):

        errorHKL1 = self.epscData.expData.HKLExpX[1] - self.HKLMdlX[1]
        errorHKL1 = pow(errorHKL1/self.epscData.expData.HKLExpX_error[1],2) * self.omega
        errorHKL2 = self.epscData.expData.HKLExpX[2] - self.HKLMdlX[2]
        errorHKL2 = pow(errorHKL2/self.epscData.expData.HKLExpX_error[2],2) * self.omega
        errorHKL6 = self.epscData.expData.HKLExpX[6] - self.HKLMdlX[6]
        errorHKL6 = pow(errorHKL6/self.epscData.expData.HKLExpX_error[6],2) * self.omega
        errorHKL7 = self.epscData.expData.HKLExpX[7] - self.HKLMdlX[7]
        errorHKL7 = pow(errorHKL7/self.epscData.expData.HKLExpX_error[7],2) * self.omega
        errorHKL = errorHKL1 + errorHKL2

        fid = open("opt_result.txt", "a")
        origStdout = sys.stdout
        sys.stdout = fid

        fid.write("\nerrorHKL1:")
        print errorHKL1
        fid.write("\nerrorHKL2:")
        print errorHKL2
        fid.write("\nerrorHKL6:")
        print errorHKL6
        fid.write("\nerrorHKL7:")
        print errorHKL7
        fid.close()
        sys.stdout = origStdout

        return errorHKL

    def getErrorBoth(self, typeOptimizer):

        errorMacroFmin = 0.
        i=0
        for exp in self.epscData.expData.macroExpY :
            mdl = self.macroMdlY[i]
            i +=1
            dy = exp - mdl
            errorMacroFmin += dy*dy
        mse = errorMacroFmin/i
        if typeOptimizer == 0 : # leastsq optimizer
            errorMacro = (self.epscData.expData.macroExpY - self.macroMdlY)/self.epscData.expData.macroExpY_error
        else :
            errorMacro = errorMacroFmin

        tempExp = []
        tempMdl = []
        for i in range(self.epscData.numDiffractionData["Phase1"]) :
            if self.epscData.listDiffractionData["Phase1"][i].flagOn :
                tempExp += list(self.epscData.expData.HKLExpX["Phase1"][i])
                tempMdl += list(self.HKLMdlX["Phase1"][i])
        error_Exp_HKL_X = array(tempExp)
        error_Mdl_HKL_X = array(tempMdl)

        errorHKLFmin = 0.
        for i in range(len(tempMdl)):
            dy = tempMdl[i] - tempExp[i]
            errorHKLFmin += dy * dy
        mse = errorHKLFmin/i
        if typeOptimizer == 0 :
            errorHKL = error_Exp_HKL_X - error_Mdl_HKL_X
        else :
            errorHKL = errorHKLFmin
        return [errorHKL,mse]





