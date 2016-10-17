#!/usr/bin/env python

import sys, pyfits, os

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print ' '
  print 'Usage: zero file_name '
  print ' '
  print 'sets all zeros to nan'
  sys.exit()


fitsobj=pyfits.open(sys.argv[-1],"readonly")
hdr=fitsobj[0].header
pix=fitsobj[0].data
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
for j in range(ny):
  for i in range(nx):
    if pix[j][i] == 0.0: pix[j][i]='nan'

os.remove(sys.argv[-1])
fitsobj=pyfits.HDUList()
hdu=pyfits.PrimaryHDU()
hdu.header=hdr
hdu.data=pix
fitsobj.append(hdu)
fitsobj.writeto(sys.argv[-1])
