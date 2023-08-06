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

class GeneralData(SuperData):
    """ data class having general data.
    """
    def __init__(self):
        SuperData.__init__(self)
        self.saved = False
        self.volFracPhase1 = 0.0
        self.volFracPhase2 = 0.0
        self.materialFile = {"Phase1":"","2Phase1":"","2Phase2":""}
        self.textureFile = {"Phase1":"","2Phase1":"","2Phase2":""}
        self.diffractionFile = {"Phase1":"","2Phase1":"","2Phase2":""}
        self.processFiles = []
        self.numProcessFiles = 1



