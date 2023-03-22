#The main MC-DART algorithm

#Author,
#   Mathé Zeegers, 
#       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

import astra
from MCDARTHelpFunctions import *
from HelperFunctions import *

np.set_printoptions(suppress=True)


def MCDART(Ph, r, b, NAngles, ARM, Startit, MCDARTit, ARMit, FixProb, channels, materials, DiscMaterialSpectr, addNoise = False, noiseInt = 100, ROI = None, Statistics = False, Smoothing = False):
    
    #Prepare arrays that track statistics
    if(Statistics):
        FullHisto = np.zeros((MCDARTit+1, len(materials)))    #Histogram with segmentation pixel class distribution over MCDART iterations
        PixelErrors = np.zeros(MCDARTit+1)                    #Number of misclassified pixels over MCDART iterations
    
    #Prepare smoothing filter in MCDART 
    if(Smoothing):
        K = computeSmoothingFilter(r,b)
   
    #Create angle distribution
    Angles = np.linspace(0,np.pi,NAngles,False)
    
    vol_geom = astra.create_vol_geom(Ph.M, Ph.N)
    proj_geom = astra.create_proj_geom('parallel', 1, Ph.M, Angles)
    proj_id = astra.create_projector('cuda', proj_geom, vol_geom)

    #Make initial (artificial) projection data and initial reconstructions at all channels
    projData = np.zeros((len(channels), NAngles, Ph.M))             #Contains the "real" (projection) data
    recs = np.zeros((len(channels), Ph.M, Ph.N))                    #Contains the initial reconstructions at all channels
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

        # Run Startit iterations of the chosen reconstruction algorithm ARM
        astra.algorithm.run(alg_id, Startit)

        # Get the result
        rec = astra.data2d.get(rec_id)

        recs[idx,:,:] = rec

    #Create a spectral segmentation
    seg = spectralSegmentation(Ph, recs, DiscMaterialSpectr)
    pixelerror = pixelError(Ph.MatArr, seg, ROI)
    print("PixelError 2D seg", pixelerror)

    if(Statistics):
        PixelErrors[0] = pixelerror
        #Calculate pixel distribution
        segwb = np.copy(seg)
        segwb[ROI == 0] = len(materials)
        Histo = np.bincount(segwb.ravel())
        FullHisto[0,0:len(materials)] = Histo[0:len(materials)]

    #Make mask object for in MCDART
    mask_id = astra.data2d.create('-vol', vol_geom, np.ones(shape=(Ph.M, Ph.N)))

    for mcdart in range(1, MCDARTit+1):

        #Determine boundaries of current segmentation
        B = determine_boundary(seg)
        
        #Determine free pixels
        Rand = np.random.random((Ph.M, Ph.N))
        Rand[Rand > FixProb] = 1
        Rand[Rand < FixProb] = 0

        #Exclude boundary pixels in set of random free pixels
        U = np.multiply(1*np.logical_not(B), Rand)
        
        #Merge boundary pixels and random free pixels
        Y = np.logical_or(U,B)

        #Create a data object for the mask
        astra.data2d.store(mask_id, Y)
        
        #Segmented image with all update pixels set to zero
        Fseg = np.multiply(np.logical_not(Y), seg)

        CurRecs = np.zeros((len(channels), Ph.M, Ph.N))     #Contains the current merged masked reconstructions and att values of fixed pixels
        for idx, channel in enumerate(channels):

            #Compute attenuation profile for fixed pixels
            F = createPhantomAtChannel(Ph, channel, materials, Fseg)

            #Compute forward projection of fixed pixels
            sinogram_idFixed, sinogramFixed = astra.create_sino(F, proj_id)
            astra.data2d.store(sinogram_idFixed, sinogramFixed)

            #Compute residual sinogram
            sinogramRes = projData[idx] - sinogramFixed
            sinogramRes_id = astra.data2d.create('-sino', proj_geom, sinogramRes)
            
            #Create a data object for the reconstruction
            newrec_id = astra.data2d.create('-vol', vol_geom)

            #Do the reconstruction routine
            newcfg = astra.astra_dict(ARM)
            newcfg['ReconstructionDataId'] = newrec_id
            newcfg['ProjectionDataId'] = sinogramRes_id
            newcfg['ProjectorId'] = proj_id
            newmask_id = astra.data2d.create('-vol', vol_geom, Y)
            newcfg['option'] = {}
            newcfg['option']['ReconstructionMaskId'] = newmask_id

            #Create the algorithm object from the configuration structure
            newalg_id = astra.algorithm.create(newcfg)

            #Run ARMit iterations of the chosen reconstruction algorithm ARM
            astra.algorithm.run(newalg_id, ARMit)

            #Get the resulting reconstruction
            newrec = astra.data2d.get(newrec_id)

            #Merge to obtain all attenuations at this channel for whole phantom
            M = np.multiply(newrec, Y) + np.multiply(F, np.logical_not(Y))

            #Smooth the result
            if(Smoothing):
                Mout = cv2.filter2D(M,-1,K)

            CurRecs[idx,:,:] = M
    
        #Segmentation
        seg = spectralSegmentation(Ph, CurRecs, DiscMaterialSpectr)
        
        pixelerror = pixelError(Ph.MatArr, seg, ROI)
        print("PixelError 2D seg after MC-DART iteration", mcdart, ":", pixelerror)

        if(Statistics):
            PixelErrors[mcdart] = pixelerror
            #Calculate pixel distribution
            segwb = np.copy(seg)
            segwb[ROI == 0] = len(materials)
            Histo = np.bincount(segwb.ravel())
            FullHisto[mcdart,0:len(materials)] = Histo[0:len(materials)]
    
    if(Statistics):
        #Compute real pixel distribution for reference
        segwb = np.copy(Ph.MatArr)
        segwb[ROI == 0] = len(materials)
        realHisto = (np.bincount(segwb.ravel()))[0:len(materials)]

    if(Statistics):
        return (pixelerror, seg, FullHisto, realHisto, PixelErrors)
    else:
        return (pixelerror, seg)
