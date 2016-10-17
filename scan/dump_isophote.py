#!/usr/bin/env python

import sys
import astropy.io.fits as pyfits
try:
  import numpy.numarray as numarray
except:
  import numarray
from math import *

def xits(x,xsig):
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  xmean1=xmean1/len(x)
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  sig1=(sig1/(len(x)-1))**0.5
  xmean2=xmean1 ; sig2=sig1
  xold=xmean2+0.001*sig2
  its=0 
  while (xold != xmean2 and its < 100):
    xold=xmean2
    its+=1
    dum=0.
    npts=0
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        npts+=1
        dum=dum+tmp
    xmean2=dum/npts
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    sig2=(dum/(npts-1))**0.5
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
aspect=float(ny)/nx
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()


file=open(sys.argv[2],'r')
while 1:
  tmp=file.readline()
  if not tmp: break
  line=tmp.split()
  a=float(line[3])
  eps=1.-float(line[12])
  d=-pi*float(line[13])/180.
  xc=float(line[14])
  yc=float(line[15])

  x=[]
  for j in xrange(ny):
    for i in xrange(nx):
      try:
        t=atan((yc-j)/(xc-i))
      except ZeroDivisionError:
        t=pi/2.
      r=((i-xc)**2+(j-yc)**2)**0.5
      if abs(findr(t,eps,a,d,xc,yc)-r) < 2. and \
         str(pix[j][i]) != 'nan': x.append(pix[j][i])
  tmp=xits(x,5.)
  print '%15.8e' % tmp[2],
  for tmp in line[1:]: print tmp,
  print
