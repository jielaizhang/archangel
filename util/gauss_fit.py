#!/usr/bin/env python

import sys
import numarray
from math import *
from ppgplot import *

def airy(x,a):
  return a[0]*exp(-0.5*((x-a[1])**2)/a[2]**2)

def fchisq(s,sigmay,npts,nfree,yfit):
  chisq=0.
  for j in range(npts):
    chisq=chisq+((s[j]-yfit[j])**2)/sigmay[j]**2
  return chisq/nfree

def gridls(x,y,sigmay,npts,nterms,a,deltaa,chisqr,edge):

  nfree=npts-nterms
  chisqr=0.
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

def fitx(npts,r,s):

#   r,s = arrays of radius and surface brightness
#   npts = number of points
#   nt = number of terms
#   program would like some first guess to speed things up

  sigmay=[]
  for j in range(npts):
    sigmay.append(1.)

  nitlt=500
# computer guess if no input
  sum=0. ; area=0.
  for x,y in zip(r,s):
    sum=sum+x*y
    area=area+y
  sum1=0. ; area1=0.
  sum2=0. ; area2=0.
  for x,y in zip(r,s):
    if x < sum/area:
      sum1=sum1+x*y
      area1=area1+y
    else:
      sum2=sum2+x*y
      area2=area2+y
  a=[max(s),sum/area,abs(sum1/area1-sum2/area2)]

  dela=[0.1,0.1,0.1]
  edge=[[.01,50.],[-5.,5.],[0.01,10.]] # set edges of fit
  nit=0

  chsqr=0.
  old=a[:]
  while (nit < nitlt):
    a,chsqr=gridls(r,s,sigmay,npts,3,a,dela,chsqr,edge)
    nit=nit+1

    dif1=abs(a[0]-old[0]) # compare to old fit for convergence test
    dif2=abs(a[1]-old[1])
    dif3=abs(a[2]-old[2])
    dif=dif1+dif2+dif3
    dif=dif/3
#    if (dif < 1e-7) and (nit > 50): break
    old=a[:]

  return chsqr,a

def min_max(x,y):
  return min(x)-0.10*(max(x)-min(x)),max(x)+0.10*(max(x)-min(x)), \
         min(y)-0.10*(max(y)-min(y)),max(y)+0.10*(max(y)-min(y))

def plot():
# main plotting function
  pgeras()
  pgswin(xmin,xmax,ymin,ymax)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  pgpt(numarray.array(r),numarray.array(s),5)
  xstep=(xmax-xmin)/100.
  step=xmin
  pgmove(step,airy(step,a))
  for tmp in range(100):
    step=step+xstep
    pgdraw(step,airy(step,a))
  return

if __name__ == '__main__':
  data=[(map(float, tmp.split())) for tmp in open(sys.argv[1],'r').readlines()]
  r=[]
  s=[]
  npts=0
  for t in data:
    npts+=1
    r.append(t[0])
    s.append(t[1])

  pgbeg('/xs',1,1)
  pgask(0)
  pgscr(0,1.,1.,1.)
  pgscr(1,0.,0.,0.)
  pgscf(2)
  xmin,xmax,ymin,ymax=min_max(r,s)  # set boundaries

  chi,a=fitx(npts,r,s)
  for n,t in zip(['A','x_o','sigma'],(a)):
    print n.rjust(5),'=',
    print '%.2f' % t

  plot()
