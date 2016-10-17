#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits

fitsobj=pyfits.open(sys.argv[-3],"readonly")
hdr=fitsobj[0].header
pix=fitsobj[0].data

thres=os.popen('threshold '+sys.argv[-3]+' '+sys.argv[-2]+' '+sys.argv[-1]).read()

for z in thres[:-1]:
  print z
  xc=float(z.split()[0])
  yc=float(z.split()[1])

  try:
    for j in [yc-1,yc,yc+1]:
      for i in [xc-1,xc,xc+1]:
        if pix[j-1][i-1] > pix[yc-1][xc-1]: raise
      enddo
    enddo
    print xc,yc
  except:
    pass

