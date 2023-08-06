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

##### Common module of data input both for Experiment and Model
##### Modified from fileReadTools.py

import numpy
import os
import config
from scipy import size

def getDataArray(matrixString,**args):
    """ Read data and save as array."""

    tmpFname = "tempMat.dat"
    tmpFile = open(tmpFname,'w+')
    tmpFile.write(matrixString)
    tmpFile.close()
#    tmpFile = open(tmpFname, 'r+')
#    matrix = io.read_array(tmpFile)
#    tmpFile.close()
    try :
        matrix = numpy.loadtxt(tmpFname)
    except:
        return [0]
#    os.remove(tmpFname)
    return matrix

def getLabelAndDataArray(str,**args):
    """ Read label as list and data as array to save them as dictionary."""

    firstReturn = str.find('\n')
    line1 = str[:firstReturn]
    rest = str[(firstReturn+1):]
    labels = line1.split()
    matrix = getDataArray(rest)
    if matrix.any() == 0 :
        return 0
    numCol = size(matrix,1)
    if numCol != len(labels):
        raise 'Number of coloumns=%d is not equal to number of labels=%d.'%(numCol,len(labels))
    dict={}
    for i in range(len(labels)):
        dict[labels[i]] = matrix[:,i]
    return dict,labels

#### Post processing of Neutron Experiment
#### Retrieve data from Extensometer data and Reitveld redined diffraction data


def readExp(fpath):

    fid = open(fpath, 'r')
    strAll = fid.read()

    D = getLabelAndDataArray(strAll)

    return D

#### Post processing of EPSC Model
#### Retrieve data from epsc3.out and epsc9.out

def readModelMacro(fpath='epsc3.out'):
    """ Read macro model result(array) with labels(lists) as dictionary."""

    fid = open(fpath,'r')
    strAll=fid.read()
    ind = strAll.find('EPS1')
    str=strAll[ind:]
    print str
    D = getLabelAndDataArray(str)
    fid.close()

    return D

def readModelHKL(fpath='epsc9.out'):
    """ Read hkl model result(array) with labels(lists) as dictionary."""

    fid = open(fpath,'r')
    strAll=fid.read()

    ind1 = strAll.find('angle_eta')
    if ind1 == -1 :
        return -1
    #find the first newline after ind1
    ind2 = strAll.find('\n',ind1)
    #find the next word after hkl section
    ind3 = strAll.find('SET',ind2)
    hklString = strAll[ind2+1:ind3].strip()
    hklLines = hklString.split('\n')
    ind4 = strAll.find('control',ind3)
    valueString = strAll[ind4:]
    D,labels = getLabelAndDataArray(valueString)
    fid.close()

    return D

def readModelHKL_phase1(fpath='epsc9.out'):
    """ Read hkl model result(array) with labels(lists) as dictionary."""

    fid = open(fpath,'r')
    strAll=fid.read()

    ind1 = strAll.find('angle_eta')
    #find the first newline after ind1
    ind2 = strAll.find('\n',ind1)
    #find the next word after hkl section
    ind3 = strAll.find('SET',ind2)
    hklString = strAll[ind2+1:ind3].strip()
    hklLines = hklString.split('\n')
    ind4 = strAll.find('control',ind3)
    valueString = strAll[ind4:]
    D,labels = getLabelAndDataArray(valueString)
    fid.close()

    return D

def checkExp(fpath, names):
    """ function which check the file(fpath) have properties with name in 'names'
    """
    try:
        fid = open(fpath, 'r')
        strAll = fid.read()
        labels,data = getLabelAndDataArray(strAll)
        for name in names:
            if(labels.has_key(name) == False):
                return False
    except:
        return False
    return True