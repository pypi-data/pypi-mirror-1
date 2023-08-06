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

class DiffractionData:
    """ data class which represents diffraction planes and diffraction angles
    """
    def __init__(self,name,eta,chi,angle):
        self.name = name
        self.chi = chi
        self.eta = eta
        self.angle = angle
        self.flagOn = False

    def turnOnFlag(self):
        self.flagOn = True

    def turnOffFlag(self):
        self.flagOn = False