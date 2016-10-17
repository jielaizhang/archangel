#!/usr/bin/env python

import sys, os

def linfit(fit):
# linear fit to array fit (x,y,sigmay)
  sum=0.0
  sumx=0.0
  sumy=0.0
  sumxy=0.0
  sumx2=0.0
  sumy2=0.0
  n=0
  for tmp in fit:
    n+=1
    sum=sum+(1./tmp[2]**2)
    sumx=sumx+(1./tmp[2]**2)*tmp[0]
    sumy=sumy+(1./tmp[2]**2)*tmp[1]
    sumxy=sumxy+(1./tmp[2]**2)*tmp[0]*tmp[1]
    sumx2=sumx2+(1./tmp[2]**2)*tmp[0]*tmp[0]
    sumy2=sumy2+(1./tmp[2]**2)*tmp[1]*tmp[1]
  dex=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dex
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dex
# varience
  var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
  if var < 0.: var=0.
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dex*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dex)**0.5
# sigma m
  sigm=(var*sum/dex)**0.5
  sigx=0.
  for tmp in fit:
    z=a+b*tmp[0]
    sigx=sigx+(z-tmp[1])**2
  sigx=(sigx/(n-1))**.5
  return a,b,r,sigb,sigm,sigx

if '-h' in sys.argv:
  print '''
Usage: big_transform master_coord transform_file mx bx my by

takes master ims file and matchs transform file, outputs matches,
assumes really big shift and different pixel scales
'''

scan1=[(map(float, tmp.split())) for tmp in open(sys.argv[1],'r').readlines()]
scan2=[(map(float, tmp.split())) for tmp in open(sys.argv[2],'r').readlines()]
mx=float(sys.argv[-4])
cx=float(sys.argv[-3])
my=float(sys.argv[-2])
cy=float(sys.argv[-1])

data1=[] ; data2=[]
for t in scan1:
  rmin=1.e33
  for z in scan2:
    dr=((z[0]-(mx*t[0]+cx))**2+(z[1]-(my*t[1]+cy))**2)**0.5
    if dr < min(10.,rmin):
      rmin=dr
      hold=[t,z]
  if rmin < 1.e33:
#    print 4*'%.1f ' % (hold[0][0],hold[0][1],hold[1][0],hold[1][1]),
#    print '%.2f' % rmin
    data1.append([hold[0][0],hold[1][0],1.])
    data2.append([hold[0][1],hold[1][1],1.])
print '%.2f %.3f' % linfit(data1)[0:2],
print '%.2f %.3f' % linfit(data2)[0:2]
