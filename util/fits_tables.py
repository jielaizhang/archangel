#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits

tab=pyfits.open(sys.argv[-1])
tabhdu=tab[1]
tabdat=tabhdu.data

for n in range(len(tabdat)):
  print str(tabdat[n]).replace('(','').replace(')','').replace(',','')
