#!/usr/bin/env python

import sys
import astropy.io.fits as pyfits

fitsobj=pyfits.open(sys.argv[-1],"readonly")
nx=fitsobj[0].header['NAXIS1']
print nx
hdr=fitsobj[0].header
#print hdr.items()

#pix=fitsobj[0].data
#xmax=-1.e99
#xmean=0
#for j in range(ny):
#  for i in range(nx):
#    xmean=xmean+pix[i][j]
#    if pix[i][j] > xmax: xmax=pix[i][j]
#
#print xmean/(nx*ny),xmax
