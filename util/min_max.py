#!/usr/bin/env python

# python version of fortran min_max, its 6x slower (!)

import sys
import astropy.io.fits as pyfits

if len(sys.argv) == 1 or sys.argv[1] =='-h':
  print ' '
  print 'Usage: min_max data_file x y r'
  print ' '
  print 'find the location of the min and max pixels'
  print 'if specified, from x and y for radius r'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
pix=fitsobj[0].data

if len(sys.argv) < 5:
  x=nx/2.
  y=ny/2.
  r=nx*ny
else:
  x=float(sys.argv[2])
  y=float(sys.argv[3])
  r=float(sys.argv[4])

xmin=+1.e33
xmax=-1.e33
nan=0
j=0
for line in pix:
  j=j+1
  i=0
  for dot in line:
    i=i+1
    if ((i-x)**2+(j-y)**2)**0.5 < r and dot > xmax: 
      xmax=dot
      imax=i
      jmax=j
    if ((i-x)**2+(j-y)**2)**0.5 < r and dot < xmin: 
      xmin=dot
      imin=i
      jmin=j
    if str(dot) == 'nan': nan=nan+1

print 'Minimum of ',xmin,' at x = ',imin,' and y = ',jmin
print 'Maximum of ',xmax,' at x = ',imax,' and y = ',jmax
print 'Number of NaN pixels ',nan

sys.exit()

# 2nd way to do this takes 2 mins of CPU (!)

xmin=+1.e33
xmax=-1.e33
nan=0
for j in range(ny):
  for i in range(nx):
    if ((i-x)**2+(j-y)**2)**0.5 < r and str(pix[j][i]) != 'nan':
      if pix[j][i] >= xmax:
        xmax=pix[j][i]
        imax=i+1
        jmax=j+1
      if pix[j][i] <= xmin:
        xmin=pix[j][i]
        imin=i+1
        jmin=j+1
    if ((i-x)**2+(j-y)**2)**0.5 < r and str(pix[j][i]) == 'nan': nan=nan+1

print 'Minimum of ',xmin,' at x = ',imin,' and y = ',jmin
print 'Maximum of ',xmax,' at x = ',imax,' and y = ',jmax
print 'Number of NaN pixels ',nan
