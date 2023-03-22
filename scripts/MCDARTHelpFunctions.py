#Supporting functions for the MC-DART algorithm

#Author,
#   Mathé Zeegers, 
#       Centrum Wiskunde & Informatica, Amsterdam (m.t.zeegers@cwi.nl)

import numpy as np


#Determine which elements in A are part of a boundary (of radius 1)
def determine_boundary(A):
  #Determine A shifted resp. left, right, up and down
  #Pad undefined values with same values as A
  Al = np.roll(A, -1, axis=1)
  Al[:,-1] = A[:,-1]
  Ar = np.roll(A, 1, axis=1)
  Ar[:,0] = A[:,0]
  Au = np.roll(A, -1, axis=0)
  Au[-1,:] = A[-1,:]
  Ad = np.roll(A, 1, axis=0)
  Ad[0,:] = A[0,:]
 
  #Determine A shifted resp. leftup, leftdown, rightup and rightdown
  #Pad undefined values with same values as A
  Alu = np.roll(Al, -1, axis=0)
  Alu[-1,:] = A[-1,:]
  Alu[:,-1] = A[:,-1]
  Ald = np.roll(Al, 1, axis=0)
  Ald[0,:] = A[0,:]
  Ald[:,-1] = A[:,-1]
  Aru = np.roll(Ar, -1, axis=0)
  Aru[-1,:] = A[-1,:]
  Aru[:,0] = A[:,0]
  Ard = np.roll(Ar, 1, axis=0)
  Ard[0,:] = A[0,:]
  Aru[:,0] = A[:,0]
  
  #Determine which entries in the shifted arrays are equal to those of A
  #An entry determines that the neighbor in the corresponding direction is equal or not
  At = np.zeros((8, A.shape[0], A.shape[1]), dtype=np.bool)
  At[0] = np.equal(A, Al)
  At[1] = np.equal(A, Ar)
  At[2] = np.equal(A, Au)
  At[3] = np.equal(A, Ad)
  At[4] = np.equal(A, Alu)
  At[5] = np.equal(A, Ald)
  At[6] = np.equal(A, Aru)
  At[7] = np.equal(A, Ard)
  At = np.all(At,axis=0)==False

  return At

  #Return true if any neighbor is not equal: !(...AND...AND...)
  return np.logical_not(np.logical_and(Acl, np.logical_and(Acr,np.logical_and(Acu, \
  np.logical_and(Acd, np.logical_and(Aclu, np.logical_and(Acld, Acru, Acrd)))))))

#Precomputations for smoothing operator
def computeSmoothingFilter(r,b):
  w = r*2+1                                   #length of square kernel
  K = np.ones((w,w))*(b/(w*w-1))              #values of kernel edges
  K[r, r] = 1 - b                             #value of kernel center
  return K
