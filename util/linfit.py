#!/usr/bin/env python

import os, sys

def linfit(data):
  sum=0.0 ; sumx=0.0 ; sumy=0.0 ; sumxy=0.0 ; sumx2=0.0 ; sumy2=0.0 ; n=0
  for tmp in data:
    if not tmp: continue
    n=n+1
    try:
      sum=sum+(1./tmp[3]**2)
      sumx=sumx+(1./tmp[3]**2)*tmp[0]
      sumy=sumy+(1./tmp[3]**2)*tmp[1]
      sumxy=sumxy+(1./tmp[3]**2)*tmp[0]*tmp[1]
      sumx2=sumx2+(1./tmp[3]**2)*tmp[0]*tmp[0]
      sumy2=sumy2+(1./tmp[3]**2)*tmp[1]*tmp[1]
    except:
      sum=sum+1.
      sumx=sumx+tmp[0]
      sumy=sumy+tmp[1]
      sumxy=sumxy+tmp[0]*tmp[1]
      sumx2=sumx2+tmp[0]*tmp[0]
      sumy2=sumy2+tmp[1]*tmp[1]

  dl=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dl
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dl
# varience
  var=abs((sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2))
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dl*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dl)**0.5
# sigma m
  sigm=(var*sum/dl)**0.5
  sig=0.
  for tmp in data:
    if not tmp: continue
    z=a+b*tmp[0]
    sig=sig+(z-tmp[1])**2
  sig=(sig/(n-1))**.5
  return a,b,r,sigb,sigm,sig

# main

data=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()]
print linfit(data)

