#!/usr/bin/env python

import sys, os
from math import *
try:
  import numpy.numarray as numarray
except:
  import numarray
import pyfits
from xml_archangel import *

def ellipse(axis,x,r,s,xc,yc,th):

# routine to solve coeffients of elliptical equation
# of form Ax^2 + By^2 + Cx + Dy + Exy + F = 0
# r = major axis, s = minor axis

  m=cos(th)
  n=sin(th)
  xo=0.
  yo=0.
  a=(s**2)*(m**2)+(r**2)*(n**2)
  b=(s**2)*(n**2)+(r**2)*(m**2)
  c=-2.*((s**2)*m*xo+(r**2)*n*yo)
  d=-2.*((s**2)*n*xo+(r**2)*m*yo)
  e=2.*((s**2)*m*n-(r**2)*m*n)
  f=(s**2)*(xo**2)+(r**2)*(yo**2)-(r**2)*(s**2)

# for given x value, find two y values on ellipse
  if axis == 'x':
    x=x-xc
    t1=(d+e*x)
    t2=t1**2
    t3=4.*b*(a*(x**2)+c*x+f)
    t4=2.*b
    try:
      return yc+(-t1+(t2-t3)**0.5)/t4,yc+(-t1-(t2-t3)**0.5)/t4
    except:
      return 'nan','nan'
# for given y value, find two x values on ellipse
  else:
    x=x-yc
    t1=(c+e*x)
    t2=t1**2
    t3=4.*a*(b*(x**2)+d*x+f)
    t4=2.*a
    try:
      return xc+(-t1+(t2-t3)**0.5)/t4,xc+(-t1-(t2-t3)**0.5)/t4
    except:
      return 'nan','nan'

def piece(vert):
  det=0.
  for i in range(len(vert)):
    j=i+1
    if j >= len(vert): j=0
    det=det+(vert[i][0]*vert[j][1]-vert[j][0]*vert[i][1])
  return abs(det/2.)

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

def inside(x,y,eps,a,d,xc,yc):
  edge=[]
  for i in [x-0.5,x+0.5]:
    for j in [y-0.5,y+0.5]:
      if i-xc == 0:
        t=pi/2.
      else:
        t=atan((j-yc)/(i-xc))
      if ((i-xc)**2+(j-yc)**2)**0.5 < findr(t,eps,a,d,xc,yc):
        edge.append((i,j))
  return edge

def xits(xx,xsig):
  xmean1=0. ; sig1=0.
  for t in xx:
    xmean1=xmean1+t
  try:
    xmean1=xmean1/len(xx)
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  for t in xx:
    sig1=sig1+(t-xmean1)**2
  try:
    sig1=(sig1/(len(xx)-1))**0.5
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
    for t in xx:
      if abs(t-xold) < xsig*sig2:
        npts+=1
        dum=dum+t
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'NaN','NaN',len(xx),'NaN','NaN'
    dum=0.
    for t in xx:
      if abs(t-xold) < xsig*sig2:
        dum=dum+(t-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
      if sig2 == 0.: return xmean1,sig1,xmean2,sig2,len(xx),npts,its
    except:
      return xmean1,sig1,'NaN','NaN',len(xx),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(xx),npts,its

# main

try:
  if sys.argv[1] == '-h': raise
except:
  print 'circle_growth fits_file xc yc rstop'
  print
  print 'makes circle apertures to rstop, calibrates'
  print
  print 'output = radius, mag, area (pixels)'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
nx=fitsobj[0].header['NAXIS1']
ny=fitsobj[0].header['NAXIS2']
hdr=fitsobj[0].header
pix=fitsobj[0].data
fitsobj.close()

doc = minidom.parse(sys.argv[1].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)
xsky=float(elements['sky'][0][1])
cons=float(elements['zeropoint'][0][1])
scale=float(elements['scale'][0][1])
xc=float(sys.argv[-3])
yc=float(sys.argv[-2])
rstop=float(sys.argv[-1])/scale
data=[]
old_area=0.
rstart=2.

for rr in numarray.arange(rstart,rstop,1.):
  try:
    left=max(0,int(xc-rr-5))
    right=min(int(xc+rr+5),nx)
    bottom=max(0,int(yc-rr-5))
    top=min(int(yc+rr+5),ny)

    sum=0.
    tsum=0.
    npts=0.
    tot_npts=0.
    sky=[]

    for x in numarray.arange(left,right,1):
      for y in numarray.arange(bottom,top,1):
        area=0.
        tmp=inside(x,y,1.,rr,0.,xc,yc)
        tmp2=inside(x,y,1.,rr-2.,0.,xc,yc)

        if tmp and not tmp2 and str(pix[y-1][x-1]) != 'nan':
          sky.append(pix[y-1][x-1])
        vert=[]
        if tmp and len(tmp) < 4:
          y1,y2=ellipse('x',x-0.5,rr,rr,xc,yc,0.)
          if str(y1) != 'nan' and str(y2) != 'nan':
            if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y1))
            if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x-0.5,y2))
          y1,y2=ellipse('x',x+0.5,rr,rr,xc,yc,0.)
          if str(y1) != 'nan' and str(y2) != 'nan':
            if ((y-y1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y1))
            if ((y-y2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x+0.5,y2))
          x1,x2=ellipse('y',y-0.5,rr,rr,xc,yc,0.)
          if str(x1) != 'nan' and str(x2) != 'nan':
            if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y-0.5))
            if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y-0.5))
          x1,x2=ellipse('y',y+0.5,rr,rr,xc,yc,0.)
          if str(x1) != 'nan' and str(x2) != 'nan':
            if ((x-x1)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x1,y+0.5))
            if ((x-x2)**2+(0.5)**2)**0.5 <= (0.5)**0.5: vert.append((x2,y+0.5))

          if vert:
            x0=vert[-1][0]
            y0=vert[-1][1]
            for i in range(len(tmp)):
              dmin=1.e33
              for r,s in tmp:
                dd=((x0-r)**2+(y0-s)**2)**0.5
                if dd < dmin:
                  t=(r,s)
                  dmin=dd
              try:
                x0=t[0]
                y0=t[1]
                vert.append(t)
                tmp.remove(t)
              except:
                pass
            area=piece(vert)
        elif len(tmp) == 4:
          area=1.
        if str(pix[y-1][x-1]) != 'nan':
          if area > 1.0: area=1.
          sum=sum+area*(pix[y-1][x-1]-xsky)
#          print x,y,area,pix[y-1][x-1],sum
          tsum=tsum+area*pix[y-1][x-1]
          npts=npts+area
        tot_npts=tot_npts+area

  except:
    raise

  print '%.1f' % (rr*scale),
  print '%.3f' % (-2.5*log10(sum)+cons),
  print '%.8e' % npts
