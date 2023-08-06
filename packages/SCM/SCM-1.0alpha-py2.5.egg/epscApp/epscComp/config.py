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

import os

#flag = "release"
flag = ""
voce = [["tauZero1P","tauOne1P","thetaZero1P","thetaOne1P"],
        ["tauZero2P","tauOne2P","thetaZero2P","thetaOne2P"],\
        ["tauZero3P","tauOne3P","thetaZero3P","thetaOne3P"],\
        ["tauZero4P","tauOne4P","thetaZero4P","thetaOne4P"],
        ["tauZero5P","tauOne5P","thetaZero5P","thetaOne5P"],
        ["tauZero6P","tauOne6P","thetaZero6P","thetaOne6P"],\
        ["tauZero7P","tauOne7P","thetaZero7P","thetaOne7P"],\
        ["tauZero8P","tauOne8P","thetaZero8P","thetaOne8P"]]
file_Texture = ["Random_1000.tex","Random_2916.tex","Random_23328.tex","Extruded_Mg_1944.tex","Extruded_Mg_15548.tex"]
file_Diffraction = ["BCC.dif","FCC.dif","HCP.dif"]
if os.name == 'nt' and flag=='release':
    import _winreg
    handle = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
    key = _winreg.OpenKey(handle,"SOFTWARE\\EngDiff\\EPSC\\Settings")
    dirEpsc = _winreg.QueryValueEx(key,"Path")[0]
    dirImages = dirEpsc + "\\epscApp\\images\\"
    dirEpscCore = dirEpsc + "\\epscApp\\epscCore\\"
    dirEpscCore_phase1 = dirEpsc + "\\epscApp\\epscCore\\"
    dirEshelbyCore = dirEpsc + "\\epscApp\\eshelbyCore\\"
    dirTemp = dirEpsc + "\\epscApp\\Temp\\"
else :
    dirImages = os.path.dirname(os.path.abspath(__file__)) + os.sep +'images' + os.sep
    dirEpscCore = os.path.dirname(os.path.abspath(__file__))  + os.sep +'epscCore' + os.sep
    dirEpscCore_phase1 = os.path.dirname(os.path.abspath(__file__)) + os.sep +'epscCore' + os.sep
    dirEshelbyCore = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'eshelbyCore' + os.sep
    dirTemp = os.path.dirname(os.path.abspath(__file__))  + os.sep +'Temp' + os.sep