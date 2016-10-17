#!/usr/bin/env python

import os, sys, pyfits
try:
  import numpy.numarray as numarray
except:
  import numarray

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: blend.py mask_data model_data'
  print ''
  print 'replaces masked areas with model fit from fake'
  print 'output = filename+.blend'
  sys.exit()

file=pyfits.open(sys.argv[1])
data1=file[0].data
file=pyfits.open(sys.argv[2])
data2=file[0].data

# note: pixel at x=99, y=101 is data[100][98]

nx=len(data1[0])
ny=len(data1)
for j in range(ny):
  for i in range(nx):
    if str(data1[j][i]) == 'nan': data1[j][i]=data2[j][i]

fitsobj=pyfits.HDUList()
hdu=pyfits.PrimaryHDU()
hdu.header=file[0].header
hdu.data=data1
fitsobj.append(hdu)
try:
  fitsobj.writeto(sys.argv[1].split('.')[0]+'.blend')
except IOError:
  os.system('rm '+sys.argv[1].split('.')[0]+'.blend')
  fitsobj.writeto(sys.argv[1].split('.')[0]+'.blend')
