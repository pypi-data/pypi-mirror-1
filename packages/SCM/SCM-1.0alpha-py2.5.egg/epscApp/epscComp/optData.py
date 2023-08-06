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

from superData import *

class OptData(SuperData):
    """ data class for the optimization
    """
    def __init__(self):
        SuperData.__init__(self)
        self.nameAlgorithm = "leastsq"
        self.data["func"] = "default"
        self.data["xtol"] = 1.49e-8
        self.data["ftol"] = 1.49e-8
        self.data["maxFunc"] = 100
        self.data["fullOutput"] = 1
        self.data["expData"] = "macro"

#        self.data["modelParameters"] = []

        self.voceFlag = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],]
        self.lowVoce = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],]
        self.highVoce = [[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1],]

        self.flags["range"] = False
        self.flags["optData"] = False
        self.flags["optAlgorithm"] = False





