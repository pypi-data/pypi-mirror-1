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

class ProcessParameters(SuperData):
    """ data class which has material parameters for both particle phase
    and matrix phase
    """
    def __init__(self):
        SuperData.__init__(self)
        self.saved = False
        self.numSteps = 0
        self.selectedProcess = 0
        self.tempStart = 0
        self.tempFinal = 0
        self.strain = 0
        self.stress = 0



