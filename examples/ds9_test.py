#!/usr/bin/env python

import pyfits, numdisplay, numpy

fitsobj=pyfits.open('ned_test.fits',"readonly")
pix=fitsobj[0].data
numdisplay.display(pix,z1=5.,z2=25.)
