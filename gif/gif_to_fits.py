#!/usr/bin/env python

import sys, pyfits
import numarray

lines=[tmp for tmp in open(sys.argv[-1],'r').readlines()]
nx=int(lines[0].split()[4].split(',')[0])
ny=int(lines[0].split()[4].split(',')[1])
data=numarray.zeros((ny,nx))

for z in lines[1:]:
  if z.split()[-1] == 'black':
    j=int(z.split()[0].split(',')[0])
    i=int(z.split()[0].split(',')[1].replace(':',''))
    data[ny-i][j]=1

fitsobj=pyfits.HDUList()
hdu=pyfits.PrimaryHDU()
hdu.data=data
fitsobj.append(hdu)
fitsobj.writeto('tmp.fits')
