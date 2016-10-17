#!/usr/bin/env python

import urllib, sys, os, os.path, time
import astropy.io.fits as pyfits
import numpy.numarray as numarray
from math import *

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

if __name__ == "__main__":

  if '-h' in sys.argv or len(sys.argv) < 2:
    print './stitch_frames op left_file right_file xc yc'
    print
    print 'options: -n = no display'
    sys.exit()

  fitsobj=pyfits.open(sys.argv[-4],"readonly")
  hdr=fitsobj[0].header
  pix1=fitsobj[0].data
  print pix1.shape

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

  xc=int(sys.argv[-2]) ; yc=int(sys.argv[-1])
  nx=2000
  ny=int(200.*round((1400-yc)/100.))
  print nx,ny
  data=numarray.resize([float('nan')], (ny,nx))

  ra,dec=xytosky(trans,xc,yc)
  print xc,yc,ra,dec,

  fitsobj=pyfits.open(sys.argv[-3],"readonly")
  hdr=fitsobj[0].header
  pix2=fitsobj[0].data

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

  x,y=skytoxy(trans,ra,dec)
  ix=int(round(x)) ; iy=int(round(y))
  print ix,iy

#  sum1=0. ; npts=0
#  for j in range(yc-10,yc+10,1):
#    for i in range(xc-10,xc+10,1):
#      sum1=sum1+pix1[j][i]-1057.91779974
#
#  sum2=0.
#  for j in range(iy-10,iy+10,1):
#    for i in range(ix-10,ix+10,1):
#      sum2=sum2+pix2[j][i]-1052.50981916
#
#  print sum1,sum2,(sum1-sum2),sum1/sum2

  for j in range(0,1000,1):
    for i in range(0,1000,1):
      data[j][i]=pix1[yc-500+j][i+1041]-1052.30+1000.

  xd=2040-xc
  yd=yc-iy
  print xd,yd
  for j in range(0,1000,1):
    for i in range(1000,2000,1):
      data[j][i]=pix2[iy-500+j][ix+1+xd+i-1000]-1057.92+1000.

  hdu=pyfits.PrimaryHDU(data)
  hdr=hdu.header
  hdu.writeto('junk.fits')
