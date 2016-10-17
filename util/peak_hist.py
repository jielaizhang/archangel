#!/usr/bin/env python

import sys, math

def xits(x,xsig):                      # clipping mean subroutine
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  try:
    xmean1=xmean1/len(x)
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  try:
    sig1=(sig1/(len(x)-1))**0.5
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
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
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

# main

if '-h' in sys.argv or len(sys.argv) <= 1:
  print 'peak filename column_1 column_2 xmin xmax bin_size'
  sys.exit()

junk=[tmp.split() for tmp in open(sys.argv[1],'r').readlines()]
raw=[]
for x in junk:
  try:
    raw.append([ float(x[int(sys.argv[2])]), float(x[int(sys.argv[3])])])
#    if float(x[int(sys.argv[2])]) > data_max: data_max=float(x[int(sys.argv[2])])
  except:
    pass

bin=float(sys.argv[-1])
xmin=float(sys.argv[-3])-bin
xmax=float(sys.argv[-2])

while 1:
  xmin=xmin+bin
  if xmin > xmax: break
  x=[]
  for y in raw:
    if y[0] > xmin-bin/2. and y[0] <= xmin+bin/2.:
      x.append(y[1])

  if len(x) == 0: continue

  try:
    xstep=(max(x)-min(x))/1000.
    step=min(x)
    sig=xits(x,5.)[1]
    xbin=sig/5.
  except:
    continue

  yhi=0.

  for tmp in range(1000):
    xsum=0. ; cnt=0
    for m in x:
      z=(step-m)/(xbin/2.)
      cnt=cnt+1
      xsum=xsum+math.exp(-0.5*z**2)
    if xsum > yhi:
      yhi=xsum
      xpeak1=step
      xcnt=cnt
    step=step+xstep

  print xmin,xpeak1
