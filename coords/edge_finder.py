#!/usr/bin/env python

import sys, os
try:
  import numpy.numarray as numarray
except:
  import numarray
import pyfits
from math import *
from xml_archangel import *

if sys.argv[1] == '-h':
  print 'edge_finder file xc yc'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

edge=[]
i=int(sys.argv[-2])-1
j=int(sys.argv[-1])-1
while 1:
  j=j+1
  if pix[j][i] != pix[j][i]: break
iend=i
jend=j-1
j=j-1
print 'x y'
print i+1,j+1
edge.append((i,j))

o=[(0,1),(1,0),(0,-1),(-1,0)]
direction=0
while 1:
  for w in range(4):
    z=w+direction
    if z > 3: z=0
    try:
      if pix[j+o[z][1]][i+o[z][0]] == pix[j+o[z][1]][i+o[z][0]]: break
    except:
      print i,j,z
  direction=z-1
  i=i+o[z][0]
  j=j+o[z][1]
  if i == iend and j == jend: break
  print i+1,j+1
  edge.append((i,j))

xmin=ymin=1.e33 ; xmax=ymax=-1.e33
for x,y in edge:
  if x < xmin: xmin=x
  if x > xmax: xmax=x
  if y < ymin: ymin=y
  if y > ymax: ymax=y
print xmin,xmax,ymin,ymax

