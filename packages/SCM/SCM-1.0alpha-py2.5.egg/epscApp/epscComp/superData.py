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

class SuperData:
    """ parent class for all the data class in EPSC
    It has default functions to process data.
    """
    def __init__(self):
        self.data={}
        self.flags={}

    def setData(self,target,data):
        """ Set value to the dictionary
        """
        self.data[target] = data

    def getData(self,target):
        """ Get value from the dictionary
        """
        return self.data[target]

    def turnOnFlag(self,target):
        """ Turn the flag on
        """
        self.flags[target] = True

    def turnOffFlag(self,target):
        """ Turn the flag off
        """
        self.flags[target] = False

    def checkFlagOn(self,target):
        """ Check if the flag is on or not
        """
        return self.flags[target]

