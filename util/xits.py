#!/usr/bin/env python

import sys

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

  if '-h' in sys.argv:
    print 'xits filename sigma'
    print
    print 'output: reg mean, sig, clipped mean, sig, npts, clipped npts, iters'
    sys.exit()

  if sys.argv[1].isdigit():
    data=[]
    while 1:
      try:
        data.append(float(raw_input()))
      except:
        break
    for z in xits(data,float(sys.argv[-1])):
      print z,
    print

  else:
    data=[float(tmp) for tmp in open(sys.argv[-2],'r').readlines()]
    for z in xits(data,float(sys.argv[-1])):
      print z,
    print
