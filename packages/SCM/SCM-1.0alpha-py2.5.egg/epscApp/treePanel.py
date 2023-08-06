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

import wx

class TreePanel(wx.Panel):
    """Tree Control which has multiple roots
        -- Model
        -- Experiment
        -- Optimization

    """
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self, *args, **kwds)

        self.phase1Nodes = []
        self.phase2Nodes = []
        self.phase1Flags = [False,False,False,False,False,False]
        self.phase2Flags = [False,False,False,False,False,False]
        self.optNodes = []
        self.optFlags = [False,False]
        self.tree =wx.TreeCtrl(self, -1, style=wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HAS_BUTTONS|wx.SUNKEN_BORDER)
        self.root = self.tree.AddRoot("Properties")
        self.modelItem = self.tree.AppendItem(self.root,"Model")
        self.expItem = self.tree.AppendItem(self.root,"Experiment")
        self.optItem = self.tree.AppendItem(self.root,"Optimization")
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnSelChanged, self.tree)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
        self.flag = False
        self.doLayout()

    def doLayout(self):
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.tree, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)

    def treeData (self):
        return(["General","Material","Deformation","Texture","Diffraction","Process"])

    def treeOptData(self):
        return(["Algorithms","Parameters"])

    def phaseData(self):
        return({201:"ntphase1", 2021:"nt2phase1", 2022:"nt2phase2", 2031:"nt2phase1_BMG", 2032:"nt2phase2_BMG"})

    def clearTree(self):
        """ delete children of the tree
        """
        self.tree.DeleteChildren(self.modelItem)
        self.tree.DeleteChildren(self.expItem)
        self.tree.DeleteChildren(self.optItem)
        self.phase1Flags = [False,False,False,False,False,False]
        self.phase1Nodes = []
        self.phase2Flags = [False,False,False,False,False,False]
        self.phase2Nodes = []
        self.optFlags = [False,False]
        self.optNodes = []
        self.flag = False

    def setTree(self,phaseNum):
        if self.flag == False :
            self.phase1Item = self.tree.AppendItem(self.modelItem, "Phase1")
            self.phase1Nodes.append(self.tree.AppendItem(self.phase1Item,"General : Off"))
            self.phase1Nodes.append(self.tree.AppendItem(self.phase1Item,"Material : Off"))
            self.phase1Nodes.append(self.tree.AppendItem(self.phase1Item,"Deformation : Off"))
            self.phase1Nodes.append(self.tree.AppendItem(self.phase1Item,"Texture : Off"))
            self.phase1Nodes.append(self.tree.AppendItem(self.phase1Item,"Diffraction : Off"))
            self.phase1Nodes.append(self.tree.AppendItem(self.phase1Item,"Process : Off"))
            self.tree.Expand(self.modelItem)
            self.tree.Expand(self.phase1Item)
            self.optNodes.append(self.tree.AppendItem(self.optItem, "Algorithms : Off"))
            self.optNodes.append(self.tree.AppendItem(self.optItem, "Parameters : Off"))
            self.tree.Expand(self.optItem)
            if phaseNum!=201 :
                self.phase2Item = self.tree.AppendItem(self.modelItem, "Phase2")
                self.phase2Nodes.append(self.tree.AppendItem(self.phase2Item,"General : Off"))
                self.phase2Nodes.append(self.tree.AppendItem(self.phase2Item,"Material : Off"))
                self.phase2Nodes.append(self.tree.AppendItem(self.phase2Item,"Deformation : Off"))
                self.phase2Nodes.append(self.tree.AppendItem(self.phase2Item,"Texture : Off"))
                self.phase2Nodes.append(self.tree.AppendItem(self.phase2Item,"Diffraction : Off"))
                self.phase2Nodes.append(self.tree.AppendItem(self.phase2Item,"Process : Off"))
                self.tree.Expand(self.phase2Item)
            self.expNode = self.tree.AppendItem(self.expItem,"File : Off")
            self.tree.Expand(self.expItem)
            self.flag = True

    def turnOnNode(self,phaseNum, nodeNum):
        self.phaseNum = phaseNum
        if str(phaseNum).endswith("1") :
            self.tree.SetItemText(self.phase1Nodes[nodeNum],self.treeData()[nodeNum] + " : On")
            self.phase1Flags[nodeNum] = True
            self.tree.SetItemTextColour(self.phase1Nodes[nodeNum],wx.BLUE)

        else :
            self.tree.SetItemText(self.phase2Nodes[nodeNum],self.treeData()[nodeNum] + " : On")
            self.phase2Flags[nodeNum] = True
            self.tree.SetItemTextColour(self.phase2Nodes[nodeNum],wx.BLUE)

    def turnOffNode(self, phaseNum, nodeNum):
        self.phaseNum = phaseNum
        if str(phaseNum).endswith("1") :
            self.tree.SetItemText(self.phase1Nodes[nodeNum],self.treeData()[nodeNum] + " : Off")
            self.phase1Flags[nodeNum] = False
            self.tree.SetItemTextColour(self.phase1Nodes[nodeNum],wx.BLACK)

        else :
            self.tree.SetItemText(self.phase2Nodes[nodeNum],self.treeData()[nodeNum] + " : Off")
            self.phase2Flags[nodeNum] = False
            self.tree.SetItemTextColour(self.phase2Nodes[nodeNum],wx.BLACK)

    def turnOnExpNode(self):
        self.tree.SetItemText(self.expNode, "File : On")
        self.tree.SetItemTextColour(self.expNode,wx.BLUE)

    def turnOffExpNode(self):
        self.tree.SetItemText(self.expNode, "File : Off")
        self.tree.SetItemTextColour(self.expNode,wx.BLACK)

    def turnOnOptNode(self, nodeNum):
        self.tree.SetItemText(self.optNodes[nodeNum], self.treeOptData()[nodeNum] + " : On")
        self.optFlags[nodeNum] = True
        self.tree.SetItemTextColour(self.optNodes[nodeNum],wx.BLUE)

    def turnOffOptNode(self, nodeNum):
        self.tree.SetItemText(self.optNodes[nodeNum], self.treeOptData()[nodeNum] + " : Off")
        self.optFlags[nodeNum] = False
        self.tree.SetItemTextColour(self.optNodes[nodeNum],wx.BLACK)

    def OnSelChanged(self, event):
        item = event.GetItem()
        parent = self.tree.GetItemParent(item)
        item_text = self.tree.GetItemText(item)

        if item_text.find("On")>-1 :
            if item_text.find("File")>-1:
                self.Parent.showPanel(self.Parent.panelsData()[self.Parent.controller.epscData.phaseNum])
                self.Parent.centerPanels[self.Parent.panelsData()[self.Parent.controller.epscData.phaseNum]].nb.SetSelection(self.Parent.centerPanels[self.Parent.panelsData()[self.Parent.controller.epscData.phaseNum]].nb.GetPageCount()-1)
            else :
                item_text_front = item_text.replace(" : On","")
                if parent :
                    if self.tree.GetItemText(parent)=="Phase1" :
                        self.Parent.showPanel(self.Parent.panelsData()[self.Parent.controller.epscData.phaseNum])
                        self.Parent.centerPanels[self.Parent.panelsData()[self.Parent.controller.epscData.phaseNum]].nb.SetSelection(self.treeData().index(item_text_front))
                    elif self.tree.GetItemText(parent) == "Phase2" :
                        self.Parent.centerPanels[self.Parent.panelsData()[self.Parent.controller.epscData.phaseNum]].nb.SetSelection(self.treeData().index(item_text_front))
                    elif self.tree.GetItemText(parent) == "Optimization" :
                        self.Parent.showPanel("Opt")
                        self.Parent.centerPanels["Opt"].nb.SetSelection(self.treeOptData().index(item_text_front))

if __name__ == "__main__":
    app = wx.PySimpleApp()
    wx.InitAllImageHandlers()
    frame = wx.Frame(None, -1, 'dynamic test', size=(800,600))
    panel=TreePanel(frame)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()