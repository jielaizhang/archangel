#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits

if '-h' in sys.argv:
  print 'centroid filename xc yc side'
  print
  print 'find moment centriod'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
hdr=fitsobj[0].header
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
pix=fitsobj[0].data

xc=int(sys.argv[2])
yc=int(sys.argv[3])
side=int((float(sys.argv[-1])-1.)/2.)
sumx=0. ; sumy=0. ; sum=0.

pmin=1.e33
for j in range(yc-side,yc+side+1):
  for i in range(xc-side,xc+side+1):
    if pix[j-1][i-1] < pmin: pmin=pix[j-1][i-1]

sky=pmin-1.
for j in range(yc-side,yc+side+1):
  for i in range(xc-side,xc+side+1):
    sumx=sumx+i*(pix[j-1][i-1]-sky)
    sumy=sumy+j*(pix[j-1][i-1]-sky)
    sum=sum+(pix[j-1][i-1]-sky)

print sumx/sum,sumy/sum
