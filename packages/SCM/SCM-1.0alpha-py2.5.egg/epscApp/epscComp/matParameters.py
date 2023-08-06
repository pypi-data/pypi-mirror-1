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

class MatParameters(SuperData):
    """ data class which has material parameters
    """
    def __init__(self):
        SuperData.__init__(self)
        self.saved = False
        self.nameMaterial = ""
        self.typeCrystal = 0
        self.elastic = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
        self.thermal = [0.000012,0.000012,0.000012,0.0,0.0,0.0]
        self.voce = [[0.3,0.3,1,0.01],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],
                     [0,0,0,0],[0,0,0,0],[0,0,0,0],]
        self.selectedSystems =[]
        self.numSystems = 0




