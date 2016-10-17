#!/usr/bin/env python

import sys
from math import *
try:
  import numpy.numarray as numarray
except:
  import numarray

def lzprob(z):
    Z_MAX = 6.0    # maximum meaningful z-value
    if z == 0.0:
        x = 0.0
    else:
        y = 0.5 * fabs(z)
        if y >= (Z_MAX*0.5):
            x = 1.0
        elif (y < 1.0):
            w = y*y
            x = ((((((((0.000124818987 * w
                        -0.001075204047) * w +0.005198775019) * w
                      -0.019198292004) * w +0.059054035642) * w
                    -0.151968751364) * w +0.319152932694) * w
                  -0.531923007300) * w +0.797884560593) * y * 2.0
        else:
            y = y - 2.0
            x = (((((((((((((-0.000045255659 * y
                             +0.000152529290) * y -0.000019538132) * y
                           -0.000676904986) * y +0.001390604284) * y
                         -0.000794620820) * y -0.002034254874) * y
                       +0.006549791214) * y -0.010557625006) * y
                     +0.011630447319) * y -0.009279453341) * y
                   +0.005353579108) * y -0.002141268741) * y
                 +0.000535310849) * y +0.999936657524
    if z > 0.0:
        prob = ((x+1.0)*0.5)
    else:
        prob = ((1.0-x)*0.5)
    return prob

def slice(x,y):
  if x > y: return 0.
  if x < 0 and y >= 0:
    return (lzprob(y)-0.5)+(lzprob(abs(x))-0.5)
  else:
    return abs((lzprob(abs(y))-0.5)-(lzprob(abs(x))-0.5))

def min_max(x,y):
  return min(x)-0.10*(max(x)-min(x)),max(x)+0.10*(max(x)-min(x)), \
         min(y)-0.10*(max(y)-min(y)),max(y)+0.10*(max(y)-min(y))

data=[] ; x=[] ; y=[]
file=open(sys.argv[1],'r')
while 1:
  line=file.readline()
  if not line: break
  if len(line) <= 1: break
  if line.split()[0] != 'nan' and line.split()[1] != 'nan':
    data.append([float(line.split()[0]),float(line.split()[1])])
    x.append(float(line.split()[0]))
    y.append(float(line.split()[1]))
file.close()

box=int(sys.argv[-1])
xmin=float(sys.argv[-5])
xmax=float(sys.argv[-4])
ymin=float(sys.argv[-3])
ymax=float(sys.argv[-2])
dx=(xmax-xmin)/box
dy=(ymax-ymin)/box
y=ymin+dy/2.
for jj in range(box):
  y=ymin+jj*dy+dy/2.
  for ii in range(box):
    x=xmin+ii*dx+dx/2.
    n=0.
    for t in data:
#      print t[0],t[1],
#      print slice(-(t[0]-(x-dx/2.))/dx,-(t[0]-(x+dx/2.))/dx),
#      print slice(-(t[1]-(y-dy/2.))/dy,-(t[1]-(y+dy/2.))/dy)
      n1=slice(-(t[0]-(x-dx/2.))/dx,-(t[0]-(x+dx/2.))/dx)
      n2=slice(-(t[1]-(y-dy/2.))/dy,-(t[1]-(y+dy/2.))/dy)
      n=n+n1*n2
    print n,
  print
