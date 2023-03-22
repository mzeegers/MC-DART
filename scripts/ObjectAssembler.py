#The phantom class for loading and using phantoms

#Author,
#   Mathé Zeegers, 
#       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

import numpy as np
import operator
import os
import tifffile


class Phantom(object):

   def __init__(self, Filename = None):
      self.PhantomName = None #File containing phantom of interest
      self.M = None #Vertical size of phantom
      self.N = None #Horizontal size of phantom
      self.MatArr = None #Array containing the positions of every label
      self.Labels = [] #Label-material combinations
   
      self.AttenuationSpectra = [] #List containing all relevant attenuation spectrum functions (constructed on the fly)
                           #Contains tuples of the form (AtomicNumber, Name, EnergyData, AttenuationData, InterpolationFunction) 
      if Filename is not None:
         self.PhantomName = Filename

#Reads in a txt file and places the information in obj file
def readtxt(obj, fullname):
   #Read the file
   InFile = open(fullname, "r")
   #Read dimensions
   obj.M = int(InFile.readline())
   obj.N = int(InFile.readline())
   #Read label array
   obj.MatArr = np.zeros((obj.M, obj.N),dtype=np.int)
   for i in range(0,obj.M):
      content = InFile.readline()
      content = [int(x) for x in content.split()]
      obj.MatArr[i,:] = content
   #Read material label list
   del obj.Labels[:]
   for content in InFile:
      content = content.split()
      obj.Labels.append((int(content[0]), content[1]))
   obj.Labels.sort(key = operator.itemgetter(0))
   print(obj.Labels)
   #Close file
   InFile.close()

#Reads in a tiff file and places the information in the obj file
def readtiff(obj, fullname):
   I = tifffile.imread(fullname)
   s = np.shape(I)
   obj.M = s[0]
   obj.N = s[1]
   obj.MatArr = I
   
#Loads a phantom file and places sizes, values and contained material in obj
def loadPhantomFile(obj):
   #Create path and filename to load from
   standardpath = "../data/"
   print("Current loading directory:", standardpath)
   fullname = ""
   fullname = fullname + standardpath
   if os.path.isdir(fullname) == False: #Check if path exists
      print("Path not existent")
      return
   fullname = fullname + obj.PhantomName #Full path including Phantom file
   if os.path.isfile(fullname) == False: #Check if file exists
      print("File not existent")
      return
   if fullname.endswith('.txt'):
      readtxt(obj, fullname)
   elif fullname.endswith('tiff'):
      readtiff(obj, fullname)
