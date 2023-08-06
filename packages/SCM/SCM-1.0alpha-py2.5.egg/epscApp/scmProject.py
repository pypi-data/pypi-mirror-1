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

import cPickle

class ScmProject :
	"""  save current working data to the specified file and restore it when user open

	"""
	def __init__(self, parent):
		self.parent = parent
		self.flag = False
		self.fullPath = ""

	def open(self, prjFile):

		inf = open(prjFile)
		self.parent.controller.epscData = cPickle.load(inf)
		self.parent.controller.epscOpt.epscData = self.parent.controller.epscData
		self.parent.controller.epscOpt.colData.epscData = self.parent.controller.epscData
		self.fullPath = prjFile
		self.flag = True


	def saveAs(self, prjFile):

		outf = open(prjFile,"w")
		cPickle.dump(self.parent.controller.epscData,outf)
		outf.close()
		self.fullPath = prjFile
		self.flag = True

	def save(self):

		outf = open(self.fullPath,"w")
		cPickle.dump(self.parent.controller.epscData,outf)
		outf.close()

	def close(self):
		self.flag = False
