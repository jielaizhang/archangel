#!/usr/bin/env python

import sys
import astropy.io.fits as pyfits
from math import *
from xml_archangel import *

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: sfb_map data_file threshold box'
  print ' '
  print 'make a map x,y,sfb above thershold'
  print 'box must be odd'
  print ' '
  print 'Options: -h = this mesage'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
pix=fitsobj[0].data

nx=pix.shape[1]
ny=pix.shape[0]

doc = minidom.parse(sys.argv[1].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)
sky=float(elements['sky'][0][1])
scale=float(elements['scale'][0][1])
cons=float(elements['zeropoint'][0][1])
exptime=float(elements['exptime'][0][1])
airmass=float(elements['airmass'][0][1])
cons=2.5*log10(exptime)+cons
k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05,'1563':0.10,'1564':0.10,'1565':0.10,'1566':0.10,'1391':0.10,'1494':0.10}
cons=cons-k[elements['filter'][0][1]]*airmass

box=int(sys.argv[-1])-1

for j in range(box/2,ny-box/2-2*box,box+1):
  for i in range(box/2,nx-box/2-2*box,box+1):

    lum=0. ; npts=0
    for jj in range(j-box/2,j+box/2-1):
      for ii in range(i-box/2,i+box/2-1):
#        print i,ii
        if pix[jj][ii] != 'nan':
          npts=npts+1
          lum=lum+pix[jj][ii]-sky

    if npts > 3 and lum > 0.:
      if -2.5*log10((lum/npts)/scale**2)+cons < float(sys.argv[-2]):
        print i,j,-2.5*log10((lum/npts)/scale**2)+cons
