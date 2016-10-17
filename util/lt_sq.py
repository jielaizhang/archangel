#!/usr/bin/env python

import sys
from math import *

def airy(x,a):
  xnt = a[0] + 8.325*((x/a[1])**0.25 - 1.0)
  xnt = -0.4*xnt
  xnt1 = 10.**xnt
  xnt =  a[2] + a[3]*x
  xnt = -0.4*xnt
  xnt2 = 10.**(xnt)
  xnt3 = xnt1 + xnt2
  return -2.5*log10(xnt3)

def fchisq(s,sigmay,npts,nfree,yfit):
  chisq=0.
  for j in range(npts):
    chisq=chisq+((s[j]-yfit[j])**2)/sigmay[j]**2
  return chisq/nfree

def gridls(x,y,sigmay,npts,nterms,a,deltaa,chisqr,edge):

  nfree = npts - nterms
  chisqr =0.
  if nfree < 1: return

  for j in range(nterms):    # evaluate chi square at first two seach points
    yfit=[]
    for i in range(npts):
      yfit.append(airy(x[i],a))
    chisq1=fchisq(y,sigmay,npts,nfree,yfit)
    fn=0.
    delta=deltaa[j]
    a[j]=a[j]+delta

    if a[j] < edge[j][0] or a[j] > edge[j][1]:
      pass
    else:
      yfit=[]
      for i in range(npts):
        yfit.append(airy(x[i],a))
      chisq2=fchisq(y,sigmay,npts,nfree,yfit)
      chisq3=0.

      if chisq1-chisq2 < 0:  # reverse direction of search if chi square is increasing
        delta=-delta
        a[j]=a[j]+delta
        yfit=[]
        for i in range(npts):
          yfit.append(airy(x[i],a))
        save=chisq1
        chisq1=chisq2
        chisq2=save

      while (1):
        fn=fn+1.0            # increment a(j) until chi square increases
        a[j]=a[j]+delta
        if a[j] < edge[j][0] or a[j] > edge[j][1]: break
        yfit=[]
        for i in range(npts):
          yfit.append(airy(x[i],a))
        chisq3=fchisq(y,sigmay,npts,nfree,yfit)
        if chisq3-chisq2 >= 0: break
        chisq1 = chisq2
        chisq2 = chisq3

      fix=chisq3-chisq2    # find minimum of parpbola defined by last three points
      if fix == 0: fix=1.e-8
      delta=delta*(1./(1.+(chisq1-chisq2)/fix)+0.5)
      fix=nfree*(chisq3-2.*chisq2+chisq1)
      if fix == 0: fix=1.e-8

    a[j]=a[j]-delta
    deltaa[j]=deltaa[j]*fn/3.

  yfit=[]              # evaluate fit an chi square for final parameters
  for i in range(npts):
    yfit.append(airy(x[i],a))
  chisqr=fchisq(y,sigmay,npts,nfree,yfit)
  return a,chisqr

def fitx(npts,r,s,ie,re,sstore,cstore,nt):

#   r,s = arrays of radius and surface brightness
#   npts = number of points
#   ie = eff. surface brightness
#   re = eff. radius
#   sstore = disk scale length
#   cstore = disk surface brightness (see format below for conversion
#            to astrophysically meaningful values)
#   nt = number of parameters to fit (2 for r^1/4, 4 for B+D)
#   program would like some first guess to speed things up

  sigmay=[]
  for j in range(npts):
    sigmay.append(1.)

  nitlt=500
  if nt == 3 and sstore == 0:
#    xrint 'Disk slope required for three parameter fits'
    return

  if ie == 0: # computer guess if no input
    a=[22.,10.,22.,3.e-2]
    if nt == 2:
      a[2]=cstore
      a[3]=sstore
  else:
    a=[ie,re,cstore,sstore]

  dela=[0.1,0.1,0.1,1.e-4]
  edge=[[5.,35.],[.5,200.],[10.,30.],[1.e-8,.5]] # set edges of fit
  nit=0

#     xrint npts,r(1),r(npts)
#     xrint '              -- Initial guess --'
  alpha = 1.0857/a[3]
  xbm = a[0] - 5.*log10(a[1]) - 40.0
  xdm = a[2] - 5.*log10(alpha) - 38.6
  bdratio = 10.**(-0.4*(xbm - xdm))
#     xrint nit,bdratio,(a(i),i=1,3),alpha,chsqr

  chsqr=0.
  old=a[:]
  while (nit < nitlt):
    a,chsqr=gridls(r,s,sigmay,npts,nt,a,dela,chsqr,edge)
    if nt == 3: chsqr=chsqr*(npts-3)/(npts-4)
    nit=nit+1
    alpha = 1.0857/a[3]
    if nit > 5:
      xbm = a[0] - 5.*log10(a[1]) - 40.0
      xdm = a[2] - 5.*log10(alpha) - 38.6
      bdratio = 10.**(-0.4*(xbm - xdm))

    dif1=abs(a[0]-old[0]) # compare to old fit for convergence test
    dif2=abs(a[1]-old[1])
    dif3=abs(a[2]-old[2])
    dif=dif1+dif2+dif3
    if nt == 4:
      dif=(dif+10.*abs(a[3]-old[3]))/4
    else:
      dif=dif/3
    if (dif < 1e-7) and (nit > 50): break
    old=a[:]

#      if(mod(nit,20).eq.0: # ever 20th step - reset step size
#         dela(1)=0.1
#         dela(2)=0.1
#         dela(3)=0.1
#         dela(4)=1.e-4

  xbm = a[0] - 5.*log10(a[1]) - 40.0
  xdm = a[2] - 5.*log10(alpha) - 38.6
  bdratio = 10.**(-0.4*(xbm - xdm))

#      ie=a(1)
#      re=a(2)
#      cstore=a(3)
#      sstore=a(4)

  return a,chsqr

init=open(sys.argv[1],'r').readline().split()

data=[map(float,(tmp.split()[0],tmp.split()[1],tmp.split()[2])) for tmp in open(sys.argv[1],'r').readlines()]
r=[] ; s=[]
for tmp in data[1:]:
  if tmp[2] != 1:
    r.append(tmp[0])
    s.append(tmp[1])

print fitx(len(r),r,s,float(init[2]),float(init[3]),1.0857/float(init[1]),float(init[0]),4)
