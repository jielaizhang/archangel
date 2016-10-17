#!/usr/bin/env python

import sys,os
try:
  import numpy.numarray as numarray
except:
  import numarray
from math import *

def overlap(bot,top,dx,step):              # test for overlaping ellipses
  iprint=0               # debug if
  if step < 0:
    step=abs(step)
    iprint=1
  if bot[3] < 10 and dx > 0: dx=0.0               # dx is fudge for around ellipse test
  bsq=((1.-bot[12])*bot[3])**2        # ellipse parameters bottom and top, test bottom against top
  asq=bot[3]**2
  d=-bot[13]*pi/180.
  bsq2=((1.-top[12])*top[3])**2
  asq2=top[3]**2
  d2=-top[13]*pi/180.
  th=0.
  istep=int(360./step)+1
  for i in range(istep):              # test loop
    th=th+step
    t=th*pi/180.
    c1=bsq*(cos(t))**2+asq*(sin(t))**2
    c2=(asq-bsq)*2*sin(t)*cos(t)
    c3=bsq*(sin(t))**2+asq*(cos(t))**2
    c4=asq*bsq
    r=(c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**.5
    x1=r*cos(t)+bot[14]
    y1=r*sin(t)+bot[15]
    thold=t
    if (x1-top[14]) != 0:            # need to test radius vectors at same angle
      t=atan((y1-top[15])/(x1-top[14]))
    else:
      t=pi/2.
    xt=t
    if abs(t-thold)*180./pi > 90:    # test for bad atan's, bring angles together
      fact=int(round((thold-t)/pi))
      t=t+fact*pi
    if abs(t-thold) > pi/2.:
      print 'warning t/thold mismatch in overlap',
      print '%2.2i %7.1f %7.1f %7.1f' % (i,thold*180./pi,t*180./pi,xt*180./pi)
    c1=bsq2*(cos(t))**2+asq2*(sin(t))**2
    c2=(asq2-bsq2)*2*sin(t)*cos(t)
    c3=bsq2*(sin(t))**2+asq2*(cos(t))**2
    c4=asq2*bsq2
    r=(c4/(c1*(cos(d2))**2+c2*sin(d2)*cos(d2)+c3*(sin(d2))**2))**.5
    x2=r*cos(t)+top[14]
    y2=r*sin(t)+top[15]
    if (((x1-bot[14])**2+(y1-bot[15])**2)**0.5)+dx >= ((x2-bot[14])**2+(y2-bot[15])**2)**0.5: 
      if iprint:
        print (((x1-bot[14])**2+(y1-bot[15])**2)**0.5)+dx,((x2-bot[14])**2+(y2-bot[15])**2)**0.5
        print x1,y1
        print x2,y2
        print t*180./pi,thold*180./pi,xt*180./pi
      return 1
  return 0                 # return 1 if overlap found, 0 if not

def clean(prf,ibot,n,itop):

# linear interp for ellipse parameters of overlap ellipse

  k=(prf[n][3]-prf[ibot][3])/(prf[itop][3]-prf[ibot][3])
  xtop=prf[itop][13]
  xbot=prf[ibot][13]
  if abs(xtop-xbot) > 90:
    if xtop > xbot:
      xbot=xbot+180.
    else:
      xtop=xtop+180.
  xang=(xtop-xbot)*k+xbot
  prf[n][13]=xang
  for i in [12,14,15,16]:
    prf[n][i]=(prf[itop][i]-prf[ibot][i])*k+prf[ibot][i]
#  print n,xbot,xtop,xang,k,ibot,itop
  return

def xits(x,xsig):
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  xmean1=xmean1/len(x)
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  sig1=(sig1/(len(x)-1.))**0.5
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
    sig2=(dum/(npts-1.))**0.5
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

# main

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: prf_smooth option prf_file_name'
  print
  print 'parameter #6 set to -1 for cleaned ellipse, 0 for unfixable ones'
  print
  print 'Options: -x = delete unfixable ones'
  print '         -s = spiral, low smooth'
  print '         -d = neutral smooth'
  print '         -q = quick smooth'
  sys.exit()

if '.prf' not in sys.argv[1]:
  file=open(sys.argv[2],'r')
else:
  file=open(sys.argv[1],'r')

prf=[]
while 1:
  line=file.readline()
  if not line: break
  tmp=[]
  for x in line.split(): tmp.append(float(x))
#  if abs(tmp[13]) > 120.:
#    fact=int(round(tmp[13]/180.))
#    dum=tmp[13]-fact*180.
  if tmp[13] >= 270: tmp[13]=tmp[13]-360.
  if tmp[13] > 90: tmp[13]=tmp[13]-180.
  if tmp[13] <= -270: tmp[13]=tmp[13]+360.
  if tmp[13] < -90: tmp[13]=tmp[13]+180.
  if tmp[13] < 0: tmp[13]=tmp[13]+180.
  if tmp[6] == -1: tmp[6]=abs(tmp[6])
  tmp.append(0) # set overlap index to zero
  prf.append(tmp)
file.close()

if sys.argv[1] == '-s':
#  xfact=-2.5
  xfact=-0.5
  xlast=2.
  elast=0.5
  clast=0.5
else:
  xfact=0.0
  xlast=2.
  elast=0.02
  clast=0.5

# clean wild pos angle shifts 1st

last=prf[0][13]
for x in prf[1:]:
  n=prf.index(x)
#    print n,'%5.1f'% x[3],'%5.2f' % x[13],'%5.2f' % pavg,'%5.2f' % abs(x[13]-pavg)
  if abs(prf[n][13]-last) > 50 and abs(prf[n][13]-last) < 130 and prf[n][3] > 5:
    prf[n][6]=-1.
  else:
    last=prf[n][13]
for x in prf[1:]:
  n=prf.index(x)
  if x[6] == -1.:
    low=0
    for low in xrange(n-1,-1,-1):
      if prf[low][6] != -1.: break
    high=len(prf)
    for high in xrange(n+1,len(prf),1):
      if prf[high][6] != -1.: break
    if low == 0:
      for i in [12,13,14,15,16]: prf[n][i]=prf[high][i]
    elif high == len(prf):
      for i in [12,13,14,15,16]: prf[n][i]=prf[low][i]
    else:
      clean(prf,low,n,high)

if sys.argv[1] != '-q':
  m=0.
  eavg=0.
  pavg=0.
  for x in prf[1:]:
    n=prf.index(x)
    if prf[n][6] != 1.:
      m=m+1.
      eavg=eavg+prf[n][12]
      pavg=pavg+prf[n][13]
  eavg=eavg/m
  pavg=pavg/m
  for x in prf[1:]:
    n=prf.index(x)
#    print n,'%5.1f'% x[3],'%5.2f' % x[13],'%5.2f' % pavg,'%5.2f' % abs(x[13]-pavg)
    if abs(x[12]-eavg) > 0.2 and abs(x[13]-pavg) > 30.:
      prf[n][6]=-1.
  for x in prf[1:]:
    n=prf.index(x)
    if x[6] == -1.:
      low=0
      for low in xrange(n-1,-1,-1):
        if prf[low][6] != -1.: break
      high=len(prf)
      for high in xrange(n+1,len(prf),1):
        if prf[high][6] != -1.: break
      if low == 0:
        for i in [12,13,14,15,16]: prf[n][i]=prf[high][i]
      elif high == len(prf):
        for i in [12,13,14,15,16]: prf[n][i]=prf[low][i]
      else:
        clean(prf,low,n,high)

imax=0
for x in prf[1:]:
  n=prf.index(x)
  a1=max(0,n-3) # check if ellipse is wildly different from nearby ones
  a2=a1+7
  if a2 > len(prf):
    a2=len(prf)
    a1=a2-7
  m=1.
  eavg=prf[a1][12]
  pavg=prf[a1][13]
  xavg=prf[a1][14]
  yavg=prf[a1][15]
  for i in xrange(a1,a2):
    if i != n:
      m=m+1.
      eavg=eavg+prf[i][12]
      pavg=pavg+prf[i][13]
      xavg=xavg+prf[i][14]
      yavg=yavg+prf[i][15]
  eavg=eavg/m
  pavg=pavg/m 
  xavg=xavg/m 
  yavg=yavg/m 
  rr=((x[14]-xavg)**2+(x[15]-yavg)**2)**0.5

  if prf[n][12] < 0.06:
    xtest=180.
  else:
    xtest=xlast

#  print '%2.2i' % n,'%5.1f' % x[3],'%3.0i' % int(x[6]),'%5.2f' % (abs(prf[n][12]-eavg)), \
#        '%7.2f' % (abs(prf[n][13]-pavg)),'%5.2f' % rr

  if abs(prf[n][13]-pavg) < xtest and abs(prf[n][12]-eavg) < elast and rr < clast and x[6] > 0: continue

  if x[3] > 25: xfact=+0.1
  for i in xrange(n-1,0,-1):
    if overlap(prf[i],x,xfact,10.0):
      prf[n][18]+=1
    else:
      break
  for i in xrange(n+1,len(prf),1):
    if overlap(x,prf[i],xfact,10.0):
      prf[n][18]+=1
    else:
      break
  if prf[n][18] > imax: 
    imax=prf[n][18]
#  print '%2.2i' % n,'%5.1f' % x[3],'%3.0i' % int(x[6]),'%5.2f' % x[12],prf[n][18],imax

for loop in xrange(imax,0,-1):
  for x in prf:
    if x[18] == loop:
      n=prf.index(x)
      low=0
      for low in xrange(n-1,-1,-1):
        if prf[low][18] < loop: break
      high=len(prf)
      for high in xrange(n+1,len(prf),1):
        if prf[high][18] < loop: break
      if low == 0:
        for i in [12,13,14,15,16]: prf[n][i]=prf[high][i]
      elif high == len(prf):
        for i in [12,13,14,15,16]: prf[n][i]=prf[low][i]
      else:
        clean(prf,low,n,high)
#      print n,x[18],x[3],n,low,high
      prf[n][6]=-1.

if sys.argv[1] == '-q':
  for x in prf:
    for y in x[:18]: print '%15.8e' % y,
    print '\n',
  sys.exit()

for x in prf[1:-1]:
  n=prf.index(x)
  if overlap(x,prf[n+1],-0.5,4.0) or overlap(prf[n-1],x,-0.5,4.0): 
    prf[n][6]=0.

if sys.argv[1] != '-s':
  for x in prf[1:-1]:
    n=prf.index(x)
    if  prf[n][6] == 0.:
      low=0
      for low in xrange(n-1,-1,-1):
        if prf[low][6] != 0: break
      high=len(prf)
      for high in xrange(n+1,len(prf),1):
        if prf[high][6] != 0: break
      if low == 0:
        for i in [12,13,14,15,16]: prf[n][i]=prf[high][i]
      elif high == len(prf):
        for i in [12,13,14,15,16]: prf[n][i]=prf[low][i]
      else:
        clean(prf,low,n,high)
      prf[n][6]=-1.

  for x in prf[1:-1]:
    n=prf.index(x)
    if overlap(x,prf[n+1],-0.5,4.0) or overlap(prf[n-1],x,-0.5,4.0): 
      prf[n][6]=0.

for x in prf:
  if sys.argv[1] == '-x' and x[6] == 0.:
    pass
  else:
    for y in x[:18]: print '%15.8e' % y,
    print '\n',
