#!/usr/bin/env python

import pyfits,sys

fitsobj=pyfits.open('ngc3193_j.fits','readonly')
hdr=fitsobj[0].header
pix=fitsobj[0].data
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
sum=0.
dx=float(sys.argv[-1])
for j in range(ny):
  for i in range(nx):
    if j+1 >= 110-dx and j+1 <= 110+dx and \
       i+1 >= 110-dx and i+1 <= 110+dx:
      sum=sum+pix[j][i]

print sum

