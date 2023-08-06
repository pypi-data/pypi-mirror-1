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

class SCMPanel(object):
    """ all panels in SCM inherits this class so that they can share common data.
    """
    def __init__(self, *args,**kwds):
        # data class which contains all the information from user
        self.controller = None
        #left tree panel
        self.treePanel = None
        self.type = None

