#Script for the first experiment of the multi-channel DART paper
#In this experiment, the performance of MC-DART is investigated for different number of channels and materials in the phantom,
# all averaged over 100 runs.

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

from HelperFunctions import *

from matplotlib.colors import ListedColormap


#Set random seed given by 'run' argument
if(len(sys.argv)>0):
    np.random.seed(int(sys.argv[1]))
    random.seed(int(sys.argv[1]))

#Path to folder to save the results
RESPATHPREFIX = "../results/MCDARTMaterialChannelExp" 

def main(): 

    NAngles = 32         #Number of projection angles
    ARM = 'SIRT_CUDA'    #Name of Algebraic Reconstruction Method to use
    Startit = 10         #Iterations of the start reconstruction algorithm
    MCDARTit = 10        #Number of MCDART iterations      
    ARMit = 10           #Iterations of the reconstruction algorithm in each MCDART iteration for each channel
    FixProb = 0.99       #Fix probability - probability of 1-p of becoming a free pixel
    diskOnly = True      #Only let pixels inside the disk contribute to pixel error
    smoothing = False    #Use of smoothing in MCDART
    r = 1                #Smoothing radius
    b = 0.2              #Smoothing intensity
    saveSpectrum = True  #Save the material spectra
    saveResults = True   #Save the results
    DetRed = True        #Determines whether reduction of materials in phantom should be deterministic or random (set to False for exact paper results reproduction)

    #Print settings
    print("NAngles: ", NAngles, "\nStartit: ", Startit,"\nMCDARTit: ", MCDARTit,"\nARMit: ", ARMit,"\nFixProb: ", FixProb,"\ndiskOnly: ")   

    #Set (and create) specific saving folder
    if(saveResults == True):
        RESPATH = RESPATHPREFIX + "/ExpNAngles" + str(NAngles) + "ARM" + ARM + "Start" + str(Startit) + "MCDART" + str(MCDARTit) + "ARM" + str(ARMit) + "Fix" + str(FixProb)
        if not os.path.exists(RESPATH):
            os.makedirs(RESPATH)
    
    #Set ranges for channels and materials (to reduce the phantom to)
    minNoMaterials = 2
    maxNoMaterials = 10
    maxChannels = 10
    
    #Supporting arrays for copying attenuation values of existing materials when another one is added to the phantom
    temp = np.zeros((1,1))
    temp2 = np.zeros((1,1))

    #All pixel errors for this run
    AllPixelErrors = np.zeros((maxNoMaterials-minNoMaterials+1, maxChannels)) 

    if(saveSpectrum == True):
        if not os.path.exists(RESPATH + "/MaterialSpectra"):
            os.makedirs(RESPATH + "/MaterialSpectra")

    #Loop over all materials and channels
    for noMaterials in range(minNoMaterials, maxNoMaterials+1):        
        for noChannels in range(1,maxChannels+1):
            print("Run", sys.argv[1], "#Materials:", noMaterials, ", #Channels:", noChannels)

            #Load the phantom
            if(len(sys.argv)>1):
                TPh = Phantom("Nx128Nclass50Nchan1run" + str(sys.argv[1]) + ".tiff")
            else:
                TPh = Phantom("Nx128Nclass50Nchan1run1.tiff")
            loadPhantomFile(TPh)

            #Compute region of interest for pixel error
            ROI = np.copy(TPh.MatArr)
            if(diskOnly):
                ROI[ROI > 1] = 1
            else:
                ROI.fill(1)
            
            #Reduce the number of materials in the phantom (deterministically or randomly)
            TPh.MatArr = reduceMaterials(TPh.MatArr, noMaterials, DetRed)

            #Save reduced phantoms for a few configurations (run 1 and 2 or 10 materials)
            if(saveResults and int(sys.argv[1]) == 1):
                if(noMaterials == 2):
                    cmap = ListedColormap(['red', 'blue', 'yellow'], 'indexed')
                    FILEOUT = '../results/plots'
                    filename = 'Nx128Nclass50Nchan1run1CONVERTEDmat2'
                    pylab.imsave(FILEOUT + '/' + filename + '.png', TPh.MatArr, dpi=600, cmap=cmap)
                    pylab.imsave(FILEOUT + '/' + filename + '.eps', TPh.MatArr, cmap=cmap)
                elif(noMaterials == 10):
                    cmap = ListedColormap(['red', 'blue', 'yellow', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'white'], 'indexed')
                    FILEOUT = '../results/plots'
                    filename = 'Nx128Nclass50Nchan1run1CONVERTEDmat10'
                    pylab.imsave(FILEOUT + '/' + filename + '.png', TPh.MatArr, dpi=600, cmap=cmap)
                    pylab.imsave(FILEOUT + '/' + filename + '.eps', TPh.MatArr, cmap=cmap)

            #Define channels (1 to #noChannels)
            channels = np.arange(1,noChannels+1)

            #Get number of materials in the reduced phantom
            materials = np.unique(TPh.MatArr)
            nomaterials = len(materials)

            #Get number of channels and create random spectra
            Channels = len(channels)
            DiscMaterialSpectra = makeRandomDiscMaterialSpectra(nomaterials, Channels)
       
            #Copy spectra of previously used materials 
            DiscMaterialSpectra[0:temp2.shape[0],:] = temp2[:,0:DiscMaterialSpectra.shape[1]]
            DiscMaterialSpectra[0:temp.shape[0],0:temp.shape[1]] = temp 

            #Save the material spectra defined above
            if(saveSpectrum and noMaterials == maxNoMaterials and noChannels == maxChannels):
                if(len(sys.argv) > 0):
                    np.savetxt(RESPATH + "/MaterialSpectra/materialSpectraRun" + str(sys.argv[1]) + ".txt", DiscMaterialSpectra, fmt='%1.3f')
                else:
                    np.savetxt(RESPATH + "/MaterialSpectra/materialSpectra.txt", DiscMaterialSpectra, fmt='%1.3f')

            #Make material labels and attenuation spectra
            del TPh.Labels[:]
            for mat in materials:
                TPh.Labels.append((mat, mat))
            TPh.Labels.sort(key = operator.itemgetter(0))
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

            #Run the MC-DART algorithm
            pixelerror, seg = MCDART.MCDART(TPh, r, b, NAngles, ARM, Startit, MCDARTit, ARMit, FixProb, channels, materials, DiscMaterialSpectra, ROI = ROI, Smoothing = smoothing)

            #Save the final segmentation
            if(saveResults == True):
                if not os.path.exists(RESPATH + "/Reconstructions"):
                    os.makedirs(RESPATH + "/Reconstructions")
                colors = ['red', 'blue', 'yellow', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'white']
                cmap = ListedColormap(colors[0:nomaterials], 'indexed')
                pylab.imsave(RESPATH + "/Reconstructions/FinalSegRun" + str(sys.argv[1]) + "NoMat" + str(noMaterials) + "noChannels" + str(noChannels) + ".png", seg, dpi=600, cmap=cmap)
                pylab.imsave(RESPATH + "/Reconstructions/FinalSegRun" + str(sys.argv[1]) + "NoMat" + str(noMaterials) + "noChannels" + str(noChannels) + ".eps", seg, cmap=cmap)
               
            #Update the array with pixel errors
            AllPixelErrors[noMaterials-minNoMaterials][noChannels-1] = pixelerror
            
            #Saves the material attenuations for the next (channel) iteration
            temp = DiscMaterialSpectra

        #Saves the material attenuations for the next (material) iteration
        temp2 = DiscMaterialSpectra
        temp = np.zeros((1,1))

    #Pixel error for all material-channel combinations
    print("Pixel errors for all material-channel combinations\n", AllPixelErrors)
    
    #Save pixel error results
    if(saveResults == True):
        if not os.path.exists(RESPATH + "/PixelErrors"):
            os.makedirs(RESPATH + "/PixelErrors")
        np.savetxt(RESPATH + "/PixelErrors/pixelErrorRun" + str(sys.argv[1]) + ".txt", AllPixelErrors, fmt='%i')

if __name__ == "__main__":
    main()
