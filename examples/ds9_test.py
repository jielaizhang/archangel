#!/usr/bin/env python

import numdisplay, numpy
import astropy.io.fits as pyfits

fitsobj=pyfits.open('ned_test.fits',"readonly")
pix=fitsobj[0].data
numdisplay.display(pix,z1=5.,z2=25.)
