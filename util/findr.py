#!/usr/bin/env python

import sys
try:
  import numpy.numarray as numarray
except:
  import numarray
from math import *

def findr(t,eps,a,d,xc,yc):
  bsq=(eps*a)**2
  asq=a**2
  c1=bsq*(cos(t))**2+asq*(sin(t))**2
  c2=(asq-bsq)*2*sin(t)*cos(t)
  c3=bsq*(sin(t))**2+asq*(cos(t))**2
  c4=asq*bsq
  return (c4/(c1*(cos(d))**2+c2*sin(d)*cos(d)+c3*(sin(d))**2))**0.5

def finda(eps,d,xc,yc,x0,y0):
# d=-pi*float(sys.argv[5])/180.
  xp = x0*cos(-d) + y0*sin(-d) # note inverse sign to
  yp = y0*cos(-d) - x0*sin(-d) # match astro definition
  return (xp**2+(yp/eps)**2)**0.5

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print ' '
  print 'Usage: findr a ecc theta xc yc'
  print
  print 'outputs all the x&y inside ellipse or ellipse points'
  print
  print 'This is a small script to find the radius vector for given ellipse.  Demonstrates'
  print 'the same variables to draw ellipses in FITS files.'
  print
  print 'The current perscription places pixel (1,1) [or (0,0) in python] in the lower left corner.'
  print 'South is down, East is right.  The ellipses are draw with the semi-major axis as the distance'
  print 'from center to edge.  Position angle is measured from North to East, where zero is a horizontal'
  print 'ellipse.  Subroutine findr uses semi-major axis, axial ratio (b/a), position angle, xc, yc to'
  print 'find r, the distance from center to ellipse edge at that angle.'
  print
  print 'output from gasp_images uses area, calculate semi-major axis from area.  Note position angle is'
  print 'opposite sign from normal definition.'
  print
  print 'output from prof (.prf file) uses eccentricity (1-b/a), and the opposite sign for position angle'
  print
  print 'Options: -h = this message'
  print '         -e = output ellipse'
  print '        -xy = output x&y inside ellipse'
  print '         -a = radius vector (x0, y0, eps, theta, xc, yc)'
  print '         -i = use a line from gasp_images'
  print '         -p = use a line from .prf file'
  sys.exit()

if sys.argv[1] == '-i':
  area=float(sys.argv[-3])
  eps=1.-float(sys.argv[-2])
  a=(area/(eps*pi))**0.5
  d=-pi*float(sys.argv[-1])/180.
  xc=float(sys.argv[-5])
  yc=float(sys.argv[-4])
  i1=xc-1.5*a ; i2=xc+1.5*a
  j1=yc-1.5*a ; j2=yc+1.5*a

elif sys.argv[1] == '-a':
  x0=float(sys.argv[-6])
  y0=float(sys.argv[-5])
  eps=float(sys.argv[-4])
  d=-pi*float(sys.argv[-3])/180.
  xc=float(sys.argv[-2])
  yc=float(sys.argv[-1])
  xp = (x0-xc)*cos(-d) + (y0-yc)*sin(-d) # note inverse sign to
  yp = (y0-yc)*cos(-d) - (x0-xc)*sin(-d) # match astro definition
  a=(xp**2+(yp/eps)**2)**0.5
  print 'a=',a
  i1=xc-1.5*a ; i2=xc+1.5*a
  j1=yc-1.5*a ; j2=yc+1.5*a

elif sys.argv[1] == '-p':
  a=float(sys.argv[6])
  eps=1.-float(sys.argv[15])
  d=-pi*float(sys.argv[16])/180.
  xc=float(sys.argv[17])
  yc=float(sys.argv[18])
  i1=xc-1.5*a ; i2=xc+1.5*a
  j1=yc-1.5*a ; j2=yc+1.5*a

else:
  a=float(sys.argv[-5])
  eps=float(sys.argv[-4])
  d=pi*float(sys.argv[-3])/180.
  xc=float(sys.argv[-2])
  yc=float(sys.argv[-1])
  i1=xc-1.5*a ; i2=xc+1.5*a
  j1=yc-1.5*a ; j2=yc+1.5*a

#edraw(eps,a,d,xc,yc):
#edraw(1.-line[12],line[3],-line[13]*pi/180.,line[14],line[15])

if '-e' in sys.argv:
  th=0.
  step=1.
  istep=int(360./step)+1
  for i in range(istep):
    th=th+step
    t=th*pi/180.
    r=findr(t,eps,a,d,xc,yc)
    if th == step:
      print r*cos(t)+xc,r*sin(t)+yc
    else:
      print r*cos(t)+xc,r*sin(t)+yc

if '-xy' in sys.argv:
  x=[] ; y=[]
  for j in xrange(int(j2)):
    for i in xrange(int(i2)):
      if i-xc == 0:
        t=pi/2.
      else:
        t=atan((j-yc)/(i-xc))
      if ((i-xc)**2+(j-yc)**2)**0.5 < findr(t,eps,a,d,xc,yc):
        x.append(i)
        y.append(j)
        print i,j
