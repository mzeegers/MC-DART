# <a href="https://link.springer.com/chapter/10.1007/978-3-030-05288-1_13" style="color: black;">MC-DART</a>: Multi-channel tomographic reconstruction with Multi-Channel DART

   <p align="center">
   <img src="./images/FlowChartMCDARTv5.svg" style="width: 90%" >
    </p>
    
## Introduction

MC-DART (Multi-Channel Discrete Algebraic Reconstruction Technique) is a tomographic reconstruction algorithm for multi-channel data. The algorithm is a generalization of DART to multi-channel data and alternately applies channel reconstructions and multi-channel segmentation to yield a final reconstructed segmentation. 

This package provides scripts for applying MC-DART with simulated X-ray data. In addition, the package provides scripts to reproduce the results of the experiments in the associated paper titled '[A Multi-Channel DART Algorithm](https://link.springer.com/chapter/10.1007/978-3-030-05288-1_13)', in which the reconstruction mathod is demonstrated and analyzed on numerical 2D X-ray phantoms.

## Requirements

The code requires Python and MATLAB (r2020 and above recommended) to run. It also requires the following packages:

**Major**:
ASTRA Toolbox:
https://github.com/astra-toolbox/astra-toolbox

Minor (but essential):
numpy, pylab, scipy, tifffile

The code has been tested with Python version 3.6.10 on Fedora 36, with Intel(R) Core(TM) i7-7700K CPU, GeForce GTX 1070 GPU, CUDA version 11.8 and CUDA toolkit 10.1.243.


## Scripts

The package contains code to apply the MC-DART method, as well as scripts to carry out experiments in the associated conference [paper](https://link.springer.com/chapter/10.1007/978-3-030-05288-1_13). The first experiment explores the performance of MC-DART when the number of materials and number of channels are varied. The second experiment investigates the performance (in pixel error per material class over number of iterations) of MC-DART compared to straightforward multi-channel reconstruction. The scripts folder is organized in the following manner:

```
├── scripts
    ├── HelperFunctions.py
    ├── MCDART.py
    ├── MCDARTExp1.py
    ├── MCDARTExp1PostProc.m
    ├── MCDARTExp1Runs.sh
    ├── MCDARTExp2.py
    ├── MCDARTExp2DARTRuns.sh
    ├── MCDARTExp2NoDARTRuns.sh
    ├── MCDARTExp2PostProc.m
    ├── MCDARTHelpFunctions.py
    ├── NonDARTRecs.py
    └── ObjectAssembler.py
```    

To reproduce the results in the [paper](https://link.springer.com/chapter/10.1007/978-3-030-05288-1_13), follow the following scripts:
- **Section 4, Fig. 4 and 5:** Run the MCDARTExp1Runs.sh scripts to generate the results and MCDARTExp1PostProc.m to generate the plots.
- **Section 4, Fig. 6**: Run the MCDARTExp2DARTRuns.sh and MCDARTExp2NoDARTRuns.sh scripts to generate the results and MCDARTExp2PostProc.m to generate the plots.

The resulting plots (see examples below) will be located /results/plots folder. The results may differ slightly since in the original scripts no fixed seeds were used.

## Example results

Below are data samples and the results of the MC-DART experiments. On the left are two phantoms (with two and ten materials respectively) are used. The plots on the upper right show the relative pixel classification errors in the final segmentations of MC-DART as the number of channels and materials are varied. The plot on the lower right show the pixel classification error over the number of reconstruction algorithm iterations.

   <p align="center">
   <img align=center src="./images/Nx128Nclass50Nchan1run1CONVERTEDmat2.png" style="width: 25%">
   <img align=center src="./images/EXP1PixelErrorOverMaterialsandChannels.png" style="width: 50%">
   </p>
   <p align="center">
   <img align=center src="./images/Nx128Nclass50Nchan1run1CONVERTEDmat10.png" style="width: 25%">
   <img align=center src="./images/EXP2PixelErrorOverTime.png" style="width: 50%">
   </p>

## References

The algorithms and routines implemented in this package are described in the following [conference paper](https://link.springer.com/chapter/10.1007/978-3-030-05288-1_13) published in the proceedings of the 19th International Workshop on Combinatorial Image Analysis (IWCIA 2018). If you use (parts of) this code in a publication, we would appreciate it if you would refer to:

```
@inproceedings{
  title={A Multi-Channel DART Algorithm},
  author={Zeegers, Math{\'e} and Lucka, Felix and Batenburg, Kees Joost},
  booktitle={Combinatorial Image Analysis: 19th International Workshop, IWCIA 2018, Porto, Portugal, November 22--24, 2018, Proceedings 19},
  pages={164--178},
  year={2018},
  organization={Springer}
}
```

## Authors

Code written by:
- Mathé Zeegers (m [dot] t [dot] zeegers [at] cwi [dot] nl).

Spatial 2D configurations created with help from [Felix Lucka](https://github.com/FelixLucka). 
