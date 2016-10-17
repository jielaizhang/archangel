#!/usr/bin/env python

def xits(x,xsig):
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
      if sig2 == 0.: return xmean1,sig1,xmean2,sig2,len(x),npts,its
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its

if __name__ == '__main__':

  import sys, math

  if len(sys.argv) < 2 or '-h' in sys.argv:
    print 'moving_avg filename column_1 column_1 xmin bin_size'
    sys.exit()

  junk=[tmp.split() for tmp in open(sys.argv[1],'r').readlines()]
  data=[] ; data_max=0.
  for x in junk:
    try:
      data.append([ float(x[int(sys.argv[2])]), float(x[int(sys.argv[3])])])
      if float(x[int(sys.argv[2])]) > data_max: data_max=float(x[int(sys.argv[2])])
    except:
      pass

  bin=float(sys.argv[-1])
  xmin=float(sys.argv[-2])-bin/2.-bin

  while 1:
    xmin=xmin+bin
    if xmin > data_max: break
    x=[]
    for y in data:
      if y[0] > xmin and y[0] <= xmin+bin:
        x.append(y[1])
#        if xmin > 1199 and xmin < 1201: print y[1]
    avg=xits(x,5.)
    if len(x) > 1:
      pass
      print 3*' %8.2f' % (xmin+bin/2.,avg[2],avg[3]),
      print '%5.0i' % len(x),
    else:
      continue

    sig=xits(x,5.)[1]
    xstep=(max(x)-min(x))/1000.
    step=min(x)
    xbin=sig
    yhi=0.

    for tmp in range(1000):
      xsum=0. ; cnt=0
      for m in x:
        z=(step-m)/(xbin/2.)
        xsum=xsum+math.exp(-0.5*z**2)
      if xsum > yhi:
        yhi=xsum
        xpeak1=step
#      if xmin > 1199 and xmin < 1201: print step,xsum
      step=step+xstep

    print '%8.2f' % xpeak1
