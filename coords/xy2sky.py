#!/usr/bin/env python

import sys,os
import astropy.io.fits as pyfits
import numpy as numarray
from math import *

if sys.argv[-1] == '-h':
  print './xy2sky op fits_file x y'
  print
  print 'convert coords from xy to sky, or'
  print 'reverse, using FITS header info'
  print
  print 'options: -xy = from pixel coords to RA/Dec'
  print '        -sky = from RA/Dec to pixels'
  print '          -f = use a file of coords'
  sys.exit()

# -xy from xy to sky, -sky from sky to xy

def xytosky(trans,x,y):
  if len(trans) < 7:
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1]),trans[3]+trans[5]*(y-trans[4]),
  else:
    corr=cos(pi*(trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5]))/180.)
    return trans[0]+(trans[2]/corr)*(x-trans[1])+(trans[3]/corr)*(y-trans[5]), \
           trans[4]+trans[6]*(x-trans[1])+trans[7]*(y-trans[5])

def skytoxy(trans,ra,dec):
  if len(trans) < 7:
    y=trans[4]+(dec-trans[3])/trans[5]
    corr=cos(pi*(trans[3]+trans[5]*(y-trans[4]))/180.)
    x=trans[1]+(ra-trans[0])*corr/trans[2]
    return x,y
  else:
    c=cos(pi*(trans[4]+trans[6]*(400.-trans[1])+trans[7]*(400.-trans[5]))/180.)
    t1=c*ra/trans[2]-c*trans[0]/trans[2]-trans[3]*dec/(trans[2]*trans[7])
    t1=t1+trans[3]*trans[4]/(trans[2]*trans[7])+trans[1]*(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t1=t1/(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t2=(dec-trans[4]-trans[6]*(t1-trans[1]))/trans[7]+trans[5]
    c=cos(pi*(trans[4]+trans[6]*(t1-trans[1])+trans[7]*(t2-trans[5]))/180.)
    t1=c*ra/trans[2]-c*trans[0]/trans[2]-trans[3]*dec/(trans[2]*trans[7])
    t1=t1+trans[3]*trans[4]/(trans[2]*trans[7])+trans[1]*(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t1=t1/(1.-trans[3]*trans[6]/(trans[2]*trans[7]))
    t2=(dec-trans[4]-trans[6]*(t1-trans[1]))/trans[7]+trans[5]
    return t1,t2

if '-f' in sys.argv:
  fitsobj=pyfits.open(sys.argv[-2],"readonly")
else:
  fitsobj=pyfits.open(sys.argv[2],"readonly")

nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header

try:
  trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CDELT1'], \
         hdr['CRVAL2'],hdr['CRPIX2'],hdr['CDELT2']]
  equinox=hdr['EQUINOX']
except:
  pass
try:
  trans=[hdr['CRVAL1'],hdr['CRPIX1'],hdr['CD1_1'],hdr['CD1_2'], \
         hdr['CRVAL2'],hdr['CRPIX2'],hdr['CD2_1'],hdr['CD2_2']]
  equinox=hdr['EQUINOX']
except:
  pass

#x=800.
#y=800.
#print xytosky(trans,x,y)
#print skytoxy(trans,xytosky(trans,x,y)[0],xytosky(trans,x,y)[1])

if '-f' in sys.argv:
  coords=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()]
  for co in coords:
    if sys.argv[1] == '-xy':
      print xytosky(trans,co[0],co[1])[0],
      print xytosky(trans,co[0],co[1])[1],
    else:
      print skytoxy(trans,co[0],co[1])[0],
      print skytoxy(trans,co[0],co[1])[1],
    for t in co[2:]:
      print t,
    print
else:
  x=float(sys.argv[-2])
  y=float(sys.argv[-1])
  if sys.argv[1] == '-xy':
    print xytosky(trans,x,y)[0],
    print xytosky(trans,x,y)[1]
  else:
    print skytoxy(trans,x,y)[0],
    print skytoxy(trans,x,y)[1]
