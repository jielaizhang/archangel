#!/usr/bin/env python

import sys, pyfits
import numpy.numarray as numarray
#import numarray


#data=numarray.resize([0.,1.], (10,10))
data=numarray.resize([0.], (10,10))

print data

for i in range(10):
  for j in range(10):
    data[i][j]=float(i*j)

print data

#fitsobj=pyfits.HDUList()
#hdu=pyfits.PrimaryHDU()
#hdu.data=data
#fitsobj.append(hdu)
#fitsobj.writeto('tmp.fits')

fitsobj = pyfits.HDUList()
# create Primary HDU with minimal header keywords
hdu = pyfits.PrimaryHDU()
# add a 10x5 array of zeros
hdu.data = numarray.zeros((10,10), type= numarray.Float32)
hdu.data[5][5]=10.
hdu.data[4][5]=5.
hdu.data[6][5]=5.
hdu.data[5][4]=5.
hdu.data[5][6]=5.
print hdu.data
fitsobj.append(hdu)
# save to a file, the writeto method will make sure the required
# keywords are conforming to the data
fitsobj.writeto('tmp.fits')
