#!/usr/bin/env python

import sys, os, os.path
try:
  import numpy.numarray as numarray
except:
  import numarray
import astropy.io.fits as pyfits

if '-h' in sys.argv:
  print 'imshift in_file out_file x_shift y_shift'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

try:
  xs=float(sys.argv[-2])
  ys=float(sys.argv[-1])
except:
  print 'error in shift values'
  sys.exit()

xf=xs-int(xs)
xs=int(xs)
yf=ys-int(ys)
ys=int(ys)

out=numarray.zeros((ny,nx),'Float32')
for j in range(ny):
  for i in range(nx):
    out[j][i]=float('nan')

for j in range(max(0,ys),min(ny,ny+ys)):
  for i in range(max(0,xs),min(nx,nx+xs)):
    out[j][i]=(1.-xf)*(1.-yf)*pix[j-ys][i-xs]
    out[j][i]=out[j][i]+xf*(1.-yf)*pix[j-ys][i-xs-1]
    out[j][i]=out[j][i]+(1.-xf)*yf*pix[j-ys-1][i-xs]
    out[j][i]=out[j][i]+xf*yf*pix[j-ys-1][i-xs-1]

fitsobj = pyfits.HDUList()
hdu = pyfits.PrimaryHDU()
hdu.data = out
fitsobj.append(hdu)
if os.path.isfile(sys.argv[2]): os.remove(sys.argv[2])
fitsobj.writeto(sys.argv[2])
