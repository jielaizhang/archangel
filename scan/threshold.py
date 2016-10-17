#!/usr/bin/env python

# much slower than fortran verison

import pyfits,sys,os
from optparse import OptionParser

if '-h' in sys.argv:
  print 'threshold filename x1,x2,y1,y2 threshold'
  print
  print 'dump all the peaks above threshold intensity'
  print 'x1,x2,y1,y2 do a sub-raster'
  sys.exit()

filename=sys.argv[1].split('[')[0]
fitsobj=pyfits.open(filename,"readonly")
hdr=fitsobj[0].header
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']

if ',' in sys.argv[2]:
  ix1=int(sys.argv[2].split(',')[0])
  ix2=int(sys.argv[2].split(',')[1])
  iy1=int(sys.argv[2].split(',')[2])
  iy2=int(sys.argv[2].split(',')[3])
else:
  ix1=1 ; ix2=nx-1 ; iy1=1 ; iy2=ny-1

pix=fitsobj[0].data

for j in range(iy1,iy2,1):
  for i in range(ix1,ix2,1):
    if pix[j][i] > float(sys.argv[-1]): print i+1,j+1,pix[j][i]
