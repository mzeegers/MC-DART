#Supporting functions for the multi-channel experiments with MC-DART

#Author,
#   Mathé Zeegers, 
#       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

import numpy as np
import random

#Assigns for every channel a random attenuation value to a material between 0 and 1
def makeRandomDiscMaterialSpectra(materials, channels):
    DiscMaterialSpectra = np.random.rand(materials, channels)     #Random between 0 and 1
    DiscMaterialSpectra[0,:] = np.zeros(channels)
    return DiscMaterialSpectra

def pixelError(Ground, Res, ROI = None):
    if(ROI is None):
        return np.sum(np.logical_not(np.isclose(Ground, Res)))
    else:
        return np.sum(np.logical_and(np.logical_not(np.isclose(Ground, Res)), ROI))

def createPhantomAtChannel(Ph, channel, materials, SegArray):
    AttProf = np.zeros((Ph.M, Ph.N))
    for i in range(1,len(materials)):
        if [tup for tup in Ph.AttenuationSpectra if tup[0] == i]:
            ConcProfile = np.zeros((Ph.M, Ph.N))
            ConcProfile[SegArray == i] = 1
            AttProf += ConcProfile*[tup for tup in Ph.AttenuationSpectra if tup[0] == i][0][4](channel)
    return AttProf

def channelSegmentation(Ph, recs, DiscMaterialSpectra):
    nomaterials = DiscMaterialSpectra.shape[0]
    mDiff = np.zeros((nomaterials, Ph.M, Ph.N))
    for i, m in enumerate(DiscMaterialSpectra): 
        temp = recs
        temp = temp.swapaxes(0,2)
        temp = temp.swapaxes(0,1)
        temp = np.subtract(temp,m)
        temp = np.linalg.norm(temp, axis = 2)
        mDiff[i,:,:] = temp
    seg = np.argmin(mDiff, axis=0)
    return seg

#Reduces the number of materials in field A down to m materials, by randomly relabeling
def reduceMaterials(A, m, deterministic):

    if(deterministic == True):                                 #Deterministic relabeling, 50->1, 49->2, etc.
        remainingLabels = np.unique(A).tolist()
        remainingLabelsLen = len(remainingLabels)
        
        targetCount = 1
        for i in reversed(range(m+1, remainingLabelsLen)):
            detLabel = remainingLabels[-1]
            remainingLabels.remove(detLabel)
            
            A[A == detLabel] = targetCount            
    
            targetCount += 1
            if targetCount > m:
                targetCount = 1

    else:                                                       #Random relabeling
        remainingLabels = np.unique(A).tolist()
        remainingLabelsLen = len(remainingLabels)
        for i in range(1,remainingLabelsLen-m):
            randLabel = random.choice(remainingLabels[1:])
            remainingLabels.remove(randLabel)

            targetLabel = random.choice(remainingLabels[1:])
            A[A == randLabel] = targetLabel

        #Relabeling from 0 to m
        for idx, label in enumerate(remainingLabels):
            A[A == label] = idx

    return A
