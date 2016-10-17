#!/usr/bin/env python

import sys
import astropy.io.fits as pyfits

#try:
#  import numpy.numarray as numarray
#except:
#  import numarray
import numarray

file=pyfits.open('2MASXJ01325190-0701535.fits')

#for j in range(3):
#  for i in range(3):
#    print '%5.1f' % (file[0].data[0,j,i]),
#  print ' '

# note this is for multi-dim data, first element is frame

data=file[0].data[0,:,:]

fitsobj=pyfits.HDUList()
hdu=pyfits.PrimaryHDU()
hdu.header=file[0].header
hdu.data=data
fitsobj.append(hdu)
fitsobj.writeto('tmp.fits')
