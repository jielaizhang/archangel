#!/usr/bin/env python

import pyfits, sys, random, os, os.path
from xml_archangel import *
from math import *

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

def point_inside_polygon(x,y,poly):

  n = len(poly)
  inside = False

  p1x,p1y = poly[0]
  for i in range(n+1):
    p2x,p2y = poly[i % n]
    if y > min(p1y,p2y):
      if y <= max(p1y,p2y):
        if x <= max(p1x,p2x):
          if p1y != p2y:
            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
          if p1x == p2x or x <= xinters:
            inside = not inside
    p1x,p1y = p2x,p2y

  return inside

if '-h' in sys.argv:
  print './pie_cut filename xc yc pos_ang ang_width'
  print 'make a cut sfb profile, uses efit angle and center'
  print
  print 'options: -r = output all raw pixels'
  sys.exit()

filename=sys.argv[-5]
xc=float(sys.argv[-4])
yc=float(sys.argv[-3])
angle=float(sys.argv[-2])
width=float(sys.argv[-1])/2.

m1=tan(pi*(angle+width)/180.)
m2=tan(pi*(angle-width)/180.)
b1=yc-m1*xc
b2=yc-m2*xc
#print m1,b1,m2,b2
#sys.exit()

file=pyfits.open(filename)
pix=file[0].data

#doc = minidom.parse(filename.split('.')[0]+'.xml')
#rootNode = doc.documentElement
#elements=xml_read(rootNode).walk(rootNode)
#sky=float(elements['sky'][0][1])

nx=file[0].header['NAXIS1']
ny=file[0].header['NAXIS2']
data=[]

if (angle-width <= 0. and angle+width >= 0.) or \
   (angle-width <= 180. and angle+width >= 180.):

  poly=[[xc,yc]]
  poly.append([nx,m1*nx+b1])
  poly.append([nx,m2*nx+b2])
  poly.append([xc,yc])

  for j in range(ny):
    for i in range(nx):
      if pix[j][i] != pix[j][i]: continue
      if point_inside_polygon(i,j,poly):
        if '-r' in sys.argv:
          print i,j,((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]
        else:
          data.append([((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]])

  poly=[[xc,yc]]
  poly.append([0.,b1])
  poly.append([0.,b2])
  poly.append([xc,yc])

  for j in range(ny):
    for i in range(nx):
      if pix[j][i] != pix[j][i]: continue
      if point_inside_polygon(i,j,poly):
        if '-r' in sys.argv:
          print i,j,((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]
        else:
          data.append([((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]])

else:

  poly=[[xc,yc]]
  poly.append([(ny-b1)/m1,ny])
  poly.append([(ny-b2)/m2,ny])
  poly.append([xc,yc])

  for j in range(ny):
    for i in range(nx):
      if pix[j][i] != pix[j][i]: continue
      if point_inside_polygon(i,j,poly):
        if '-r' in sys.argv:
          print i,j,((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]
        else:
          data.append([((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]])

  poly=[[xc,yc]]
  poly.append([(-b1)/m1,0.])
  poly.append([(-b2)/m2,0.])
  poly.append([xc,yc])

  for j in range(ny):
    for i in range(nx):
      if pix[j][i] != pix[j][i]: continue
      if point_inside_polygon(i,j,poly):
        if '-r' in sys.argv:
          print i,j,((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]
        else:
          data.append([((i-xc)**2.+(j-yc)**2.)**0.5,pix[j][i]])

if '-r' in sys.argv: sys.exit()

rmax=0.
for z in data:
  if z[0] > rmax: rmax=z[0]

rr=1.
while (1):
  if rr > rmax: break
  x=[]
  for z in data:
    if z[0] > rr-0.1*rr and z[0] <= rr+0.1*rr:
      x.append(z[1])

  if len(x) > 5: print rr,xits(x,2.)[2]
  rr=0.1*rr+rr
