#!/usr/bin/env python

import sys, os, os.path, math, numpy
import astropy.io.fits as pyfits

if '-h' in sys.argv:
  print 'dump all pixels in circle: xc, yc, rstart, rend, dx, filename'
  sys.exit()

file=pyfits.open(sys.argv[-1])
data=file[0].data
nx=file[0].header['NAXIS1']
ny=file[0].header['NAXIS2']

xc=float(sys.argv[-6])
yc=float(sys.argv[-5])
rstart=float(sys.argv[-4])
rend=float(sys.argv[-3])
dx=float(sys.argv[-2])

for r1 in numpy.arange(rstart,rend,dx):
  r2=r1+dx
  pix=[] ; rad=[] ; n=0.
  for j in range(0,ny):
    for i in range(0,nx):
      if ((i-xc)**2+(j-yc)**2)**0.5 > r1 and \
         ((i-xc)**2+(j-yc)**2)**0.5 < r2:
        if '-d' in sys.argv:
          print ((i-xc)**2+(j-yc)**2)**0.5,i,j,data[j][i]
        else:
          n=n+1.
          pix.append(data[j][i])
          rad.append(((i-xc)**2+(j-yc)**2)**0.5)
  print sum(rad)/n,sum(pix)/n
