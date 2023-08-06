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

from superData import SuperData
import config

class ExpData(SuperData):
    """ data class having file names of experimental data and list of it.
    """
    def __init__(self):
        SuperData.__init__(self)
        self.expFile = ""
        self.expPh2File = ""
        self.flags["expData"] = False
        self.macroExpX = []
        self.macroExpY = []
        self.HKLExpX = {"Phase1":[],"Phase2":[],"TransPhase1":[],"LongPhase1":[],"RollingPhase1":[],"TransPhase2":[],"LongPhase2":[],"RollingPhase2":[]}
        self.HKLExpX_error = {"Phase1":[],"Phase2":[],"TransPhase1":[],"LongPhase1":[],"RollingPhase1":[],"TransPhase2":[],"LongPhase2":[],"RollingPhase2":[]}
        self.HKLExpY  = []





