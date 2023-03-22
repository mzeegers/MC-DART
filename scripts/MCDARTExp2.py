#Script for the second experiments of the multi-channel DART paper
#In this experiment, the performance of MC-DART is compared to straighforward extensions of standard reconstruction algorithms (e.g. SIRT) to multi-channel input
# in terms of pixel errors over number of ARM invocations.

#Note: Turn off DetRed (deterministic reduction of materials in the phantoms) and change line 72 (loading of the phantom) for more robust results
#      For this experiment in the paper the first phantom with deterministic material reduction is inverstigated

#Author,
#   Mathé Zeegers, 
#       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

import astra
import numpy as np
import random
import pylab
import sys
import scipy.io

from ObjectAssembler import *
import MCDART
import NonDARTRecs

from HelperFunctions import *

from matplotlib.colors import ListedColormap

#Set random seed given by 'run' argument
if(len(sys.argv)>0):
    np.random.seed(int(sys.argv[1]))
    random.seed(int(sys.argv[1]))

#Path to folder to save the results
RESPATHPREFIX = "../results/MCDARTMaterialClassConvExp" 

def main(): 

    NAngles = 8          #Number of projection angles
    ARM = 'SIRT_CUDA'    #Name of Algebraic Reconstruction Method to use
    Startit = 2          #Iterations of the start reconstruction algorithm
    MCDARTit = 10        #Number of MCDART iterations
    ARMit = 10           #Iterations of the reconstruction algorithm in each MCDART iteration for each channel
    FixProb = 0.99       #Fix probability - probability of 1-p of becoming a free pixel
    diskOnly = True      #Only let pixels inside the disk contribute to pixel error
    smoothing = False    #Use of smoothing in MCDART
    r = 1                #Smoothing radius
    b = 0.2              #Smoothing intensity
    saveSpectrum = True  #Save the material spectra
    saveResults = True   #Save the results
    Evalit = 10          #Evaluate results after this number of iterations in non MC-DART approach
    DetRed = True        #Determines whether reduction of materials in phantom should be deterministic or random (set to False for exact paper results reproduction)
    
    #Take care of parameter changes by input: when no MCDART iterations set ARMit to ARM iterations per MCDART iterations times the total number of MCDART iterations
    if(len(sys.argv)>1):
        if(int(sys.argv[2]) == 0):
            Startit = 2
            ARMit = ARMit*MCDARTit
            MCDARTit = 0         

    #Print settings
    print("NAngles: ", NAngles, "\nStartit: ", Startit,"\nMCDARTit: ", MCDARTit,"\nARMit: ", ARMit,"\nFixProb: ", FixProb,"\ndiskOnly: ")   

    #Set (and create) specific saving folder
    if(saveResults == True):
        RESPATH = RESPATHPREFIX + "/ExpNAngles" + str(NAngles) + "ARM" + ARM + "Start" + str(Startit) + "MCDART" + str(MCDARTit) + "ARM" + str(ARMit) + "Fix" + str(FixProb)
        if not os.path.exists(RESPATH):
            os.makedirs(RESPATH)

    #Set number of channels and materials (to reduce the phantom to)
    noMaterials = 4
    noChannels = 10
    print(noMaterials, noChannels)

    #Load the phantom
    TPh = Phantom("Nx128Nclass50Nchan1run1.tiff") #TPh = Phantom("Nx128Nclass50Nchan1run" + str(sys.argv[1]) + ".tiff")
    loadPhantomFile(TPh)

    #Compute region of interest for pixel error
    ROI = np.copy(TPh.MatArr)
    if(diskOnly):
        ROI[ROI > 1] = 1
    else:
        ROI.fill(1)
    
    #Reduce the number of materials in the phantom (deterministically or randomly)
    TPh.MatArr = reduceMaterials(TPh.MatArr, noMaterials, DetRed)

    #Save the resulting phantom
    if(len(sys.argv)>0 and int(sys.argv[1]) == 1):
        cmap = ListedColormap(['red', 'blue', 'yellow', 'green', 'orange'], 'indexed')
        filename = 'Nx128Nclass50Nchan1run1.tiff'
        pylab.imsave(RESPATHPREFIX + '/' + filename + '.png', TPh.MatArr, dpi=600, cmap=cmap)
        pylab.imsave(RESPATHPREFIX + '/' + filename + '.eps', TPh.MatArr, cmap=cmap)

    #Show number of pixels for each material
    materials, counts = np.unique(TPh.MatArr, return_counts=True)
    print(counts)
    
    #Get number of materials (including background)
    nomaterials = len(materials)
    
    #Make random but fixed discrete spectra (one value per bin-material combination)
    DiscMaterialSpectra = np.zeros((nomaterials, noChannels))
    DiscMaterialSpectra[1,:] = [0.97718604, 0.09288675, 0.72963461, 0.10690311, 0.88904522, 0.0272893,  0.56618286, 0.25852052, 0.66600122, 0.52848547]
    DiscMaterialSpectra[2,:] = [0.67754312, 0.52846766, 0.61163974, 0.14342075, 0.16250126, 0.99679752, 0.36737503, 0.4067152,  0.5165028,  0.40504674]
    DiscMaterialSpectra[3,:] = [0.12349219, 0.11580235, 0.79007257, 0.91368675, 0.04149563, 0.60380552, 0.55397012, 0.425518,   0.65890456, 0.35999777]
    DiscMaterialSpectra[4,:] = [0.2515548,  0.4794628,  0.16501473, 0.5780091,  0.76379541, 0.46253695, 0.73918345, 0.83717862, 0.28678573, 0.03503105]
    print("Spectra:", DiscMaterialSpectra)  
    
    #Save the material spectra defined above
    if(saveSpectrum):
        if(len(sys.argv) > 0):
            np.savetxt(RESPATH + "/RandomSpectrumRun" + sys.argv[1] + ".txt", DiscMaterialSpectra, fmt='%1.3f')
        else:
            np.savetxt(RESPATH + "/RandomSpectrum.txt", DiscMaterialSpectra, fmt='%1.3f')

    #Make material labels and attenuation spectra
    del TPh.Labels[:]
    for mat in materials:
        TPh.Labels.append((mat, mat))
    TPh.Labels.sort(key = operator.itemgetter(0))
    channels = np.arange(1,noChannels+1)
    for mat in TPh.Labels:
        if(mat[0] != 0 and mat[1] != 0): #Exclude background
            AtNo = mat[1]
            if (AtNo > 0): 
                if AtNo not in [i[0] for i in TPh.AttenuationSpectra]: #Check if material is not already there
                    x, y = channels, DiscMaterialSpectra[AtNo][:]
                    if(noChannels > 1):
                        spectrum = scipy.interpolate.interp1d(x, y)
                    else:
                        spectrum = scipy.poly1d([y[0]])
                    attData = (x, y, spectrum)
                    TPh.AttenuationSpectra.append((AtNo,)+(mat[1],) + attData)
        TPh.AttenuationSpectra.sort(key = operator.itemgetter(0)) #Keep sorted on number 

    #Run the MC-DART algorithm or regular ARM reconstruction
    if(MCDARTit > 0):
        pixelerror, seg, FullHisto, realHisto, PixelErrors = MCDART.MCDART(TPh, r, b, NAngles, ARM, Startit, MCDARTit, ARMit, FixProb, channels, materials, DiscMaterialSpectra, ROI = ROI, Statistics = True, Smoothing = smoothing)
    else:
        pixelerror, seg, FullHisto, realHisto, PixelErrors = NonDARTRecs.NonDartRec(TPh, NAngles, ARM, Startit, Evalit, ARMit, channels, materials, DiscMaterialSpectra, ROI = ROI, Statistics = True)
    
    #Save the results (pixel class histograms over time, groundtruth histogram and pixel errors over time)
    if(saveResults == True):
        np.savetxt(RESPATH + "/HistosRun" + str(sys.argv[1]) + "NoMat" + str(noMaterials) + "noChannels" + str(noChannels) + ".txt", FullHisto, fmt='%i')
        np.savetxt(RESPATH + "/RealHistoRun" + str(sys.argv[1]) + "NoMat" + str(noMaterials) + "noChannels" + str(noChannels) + ".txt", realHisto, fmt='%i')
        np.savetxt(RESPATH + "/PixelErrors" + str(sys.argv[1]) + "NoMat" + str(noMaterials) + "noChannels" + str(noChannels) + ".txt", PixelErrors, fmt='%i')       

    #Computed pixel class histograms over time
    print("Computed pixel class histograms over time\n", FullHisto)
    #Ground truth pixel class histogram of the phantom
    print("Ground truth pixel class histogram of the phantom\n", realHisto)
    #Final pixor error in the reconstruction
    print("Final pixor error in the reconstruction\n", pixelerror)
    #Pixel error after every 10 ARM invocations
    print("Pixel error after every 10 ARM invocations\n", PixelErrors)
    

if __name__ == "__main__":
    main()
