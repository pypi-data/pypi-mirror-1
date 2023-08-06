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

import os,string
import sys
import config
import signal
import subprocess
import ctypes


class EpscEngine:

    """ EpscEngine class
        To do :
        1. To check out condition for running Epsc Engine
        2. Call Engine according to OS type
    """

    def engineNamesDat(self):
        """ dictionary : key => OS name
                         value => epsc engine name according to OS
        """
        return {"cygwin":"./epscVM3_Win.exe", "nt":"epscVM3_Win.exe", "posix":"./epscVM3_Mac"}

    def engineNamesDat_p1(self):
        """ dictionary : key => OS name
                         value => epsc engine name according to OS
        """
        return {"cygwin":"./EpscNp.exe", "nt":"EpscNp.exe", "posix":"./EpscNpwc_linux"}

#    def updateModelParameters(self):
#        """ Update model parameters according to user input
#        """
#        self.modlPar.selectPars()
#        self.modlPar.updateFiles()

    def deleteOutputs(self):
        for i in range(11):
            if os.path.exists(config.dirEpscCore + "epsc" + str(i+1) + ".out")==True:
                os.remove(config.dirEpscCore + "epsc" + str(i+1) + ".out")

    def callEngine(self,mode, tempQueue=None):
        """ Call epsc engine
        """
#        self.deleteOutputs()

        os.chdir(config.dirEpscCore_phase1)
        if sys.platform == "cygwin" :
            if mode=="opt":
                os.system(self.engineNamesDat_p1()[sys.platform])
            else :
                self.process = os.spawnl(os.P_NOWAIT, self.engineNamesDat_p1()[os.name])
            #fid = os.popen(self.engineNamesDat()[os.name] + " < enter.txt")

        else :
#                print self.engineNamesDat_p1()[os.name]
            ret = subprocess.call(self.engineNamesDat_p1()[os.name])
            if mode == 'run' :
                tempQueue.put('RunDraw')

    def killProcess(self):

        """kill function for Win32"""
        print "Stop running EPSC engine."
        if os.name == 'nt' :
            ctypes.windll.kernel32.TerminateProcess(int(self.process._handle), -1)
        else :
            os.kill(int(self.pid),signal.SIGHUP)
