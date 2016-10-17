#!/usr/bin/env python

import sys, numarray, math, os
from ppgplot import *
import pyfits

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
pix=fitsobj[0].data
#print 'file opened'

tmp=os.popen('sky_box -t '+sys.argv[-1]).read()
sky=float(tmp.split()[2])
skysig=float(tmp.split()[3])
#print 'sky,skysig',sky,skysig

x=[]
for line in pix:
  for dot in line:
    x.append(dot)
#print 'data read in'

xbin=skysig
xstep=10.*skysig/2.
step=sky-2.*skysig+2.*xstep
i=0
while 1:
  i+=1
  step=step-2.*xstep
  xstep=xstep/10.
  if xstep < 0.001: break
  last=0.
  while 1:
    step=step+xstep
    xsum=0.
    for m in x:
      z=(step-m)/(xbin/2.)
      xsum=xsum+math.exp(-0.5*z**2)
    if xsum < last: break
#    print '%.2f' % step,'%.2f' % xsum,'%.2f' % xstep
    last=xsum
#  print '>>',i,'%.2f' % step,'%.2f' % xsum
print '%.2f' % step
