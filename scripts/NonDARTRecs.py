#Standard ARM reconstructions for each channel
#The reconstructions are merged at the end using multi-channel segmentation

#Author,
#   Mathé Zeegers, 
#       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

import astra
from HelperFunctions import *

np.set_printoptions(suppress=True)

def NonDartRec(Ph, NAngles, ARM, Startit, Evalit, ARMit, channels, materials, DiscMaterialChannel, addNoise = False, noiseInt = 100, ROI = None, Statistics = False):
    
    #Number of evaluation points for statistics
    EvalMoments = int(ARMit/Evalit) + 1
    
    #Prepare arrays that track statistics
    if(Statistics):
        FullHisto = np.zeros((EvalMoments, len(materials)))     #Histogram with segmentation pixel class distribution over Evalit iterations
        PixelErrors = np.zeros(EvalMoments)                     #Number of misclassified pixels over Evalit iterations
   
    #Create angle distribution
    Angles = np.linspace(0,np.pi,NAngles,False)
    
    vol_geom = astra.create_vol_geom(Ph.M, Ph.N)
    proj_geom = astra.create_proj_geom('parallel', 1, Ph.M, Angles)
    proj_id = astra.create_projector('cuda', proj_geom, vol_geom)

    #Make initial (artificial) projection data and initial reconstructions at all channels
    projData = np.zeros((len(channels), NAngles, Ph.M))             #Contains the "real" (projection) data
    recs = np.zeros((len(channels), Ph.M, Ph.N))                    #Contains the initial reconstructions at all channels
    for evalit in range(0, EvalMoments):   
        for idx, channel in enumerate(channels):

            #Create phantom at channel
            P = createPhantomAtChannel(Ph, channel, materials, Ph.MatArr)
           
            #Compute forward projection and store the "data"
            sinogram_id, sinogram = astra.create_sino(P, proj_id)
            #Optional: add poisson noise to the projection data
            if(addNoise == True):
                print("Adding noise...")
                sinogram = astra.add_noise_to_sino(sinogram, noiseInt)
            projData[idx,:,:] = sinogram

            #Do reconstruction routine for each channel
            rec_id = astra.data2d.create('-vol', vol_geom)
            cfg = astra.astra_dict(ARM)
            cfg['ReconstructionDataId'] = rec_id
            cfg['ProjectionDataId'] = sinogram_id
            cfg['ProjectorId'] = proj_id
            cfg['option'] = {}
            cfg['option']['MinConstraint'] = 0

            # Create the algorithm object from the configuration structure
            alg_id = astra.algorithm.create(cfg)

            # Run Startit+Evalit*evalit iterations of the chosen reconstruction algorithm ARM
            astra.algorithm.run(alg_id, Startit+Evalit*evalit)
            
            # Get the result
            rec = astra.data2d.get(rec_id)

            recs[idx,:,:] = rec

        seg = channelSegmentation(Ph, recs, DiscMaterialChannel)
        pixelerror = pixelError(Ph.MatArr, seg, ROI)
        print("PixelError 2D seg in evaluation iteration", evalit, ":", pixelerror)
        
        if(Statistics):
            PixelErrors[evalit] = pixelerror
            #Calculate pixel distribution:
            segwb = np.copy(seg)
            segwb[ROI == 0] = len(materials)
            Histo = np.bincount(segwb.ravel())
            FullHisto[evalit,0:len(materials)] = Histo[0:len(materials)]
    
    if(Statistics):
        #Compute real pixel distribution for reference
        segwb = np.copy(Ph.MatArr)
        segwb[ROI == 0] = len(materials)
        realHisto = (np.bincount(segwb.ravel()))[0:len(materials)]

    if(Statistics):
        return (pixelerror, seg, FullHisto, realHisto, PixelErrors)
    else:
        return (pixelerror, seg)
