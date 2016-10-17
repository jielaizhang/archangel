#!/usr/bin/env python

# experiment to fit curves of growth

import sys,os
try:
  import numpy.numarray as numarray
except:
  import numarray
from ppgplot import *
from math import *

def plot():
  pgeras()
  pgswin(xmin,xmax,ymax,ymin)
  pgbox('bcnst',0.,0,'bcnst',0.,0)
  xs=numarray.array(x) ; ys=numarray.array(y)
  pgpt(xs,ys,3)
  xs=numarray.array(w) ; ys=numarray.array(z3)
  pgline(xs,ys)

pgbeg('/xs',1,1)
pgask(0)
pgscr(0,1.,1.,1.)
pgscr(1,0.,0.,0.)
pgscf(2)
pgpap(11.0,1.0)

w=[-.5, -.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, .5, .6, .7, .8, .9]
#exp curve of growth
z1=[1.68, 1.46, 1.26, 1.08, .91, .75, .62, .49 , .39, .30, .23, .17, .13, .09, .06]
#deV curve of growth
z2=[2.52, 2.12, 1.74, 1.38, 1.05, .75, .51, .31, .18, .10, .05, .02, .01, .00, .00]
z3=[2.52, 2.12, 1.74, 1.38, 1.05, .75, .51, .31, .18, .10, .05, .02, .01, .00, .00]

file=open(sys.argv[-1],'r')
x=[] ; y=[]
while 1:
  line=file.readline()
  if not line: break
  x.append(float(line.split()[0]))
  y.append(float(line.split()[1]))
lum=-2.5*log10((10.**(y[-1]/-2.5)/2.))
for tmp in y:
  if tmp < lum:
    mid=x[y.index(tmp)]
    break

file.close()
for tmp in y:
   y[y.index(tmp)]=tmp-y[-1]
sum=0.
for tmp in x:
  sum=sum+tmp
sum=sum/len(x)
for tmp in x:
   x[x.index(tmp)]=tmp-mid

xs=numarray.array(x)
ys=numarray.array(y)
xmin=min(x)-0.10*(max(x)-min(x))
ymin=min(y)-0.10*(max(y)-min(y))
xmax=max(x)+0.10*(max(x)-min(x))
ymax=max(y)+0.10*(max(y)-min(y))
label=1
scale=1.
pgswin(xmin,xmax,ymax,ymin)
pgbox('bcnst',0.,0,'bcnst',0.,0)
pgpt(xs,ys,3)
plot()

while 1:

  d=pgband(0)

  if d[2] == '?':
    print '/ = exit        b = change borders'
    print 'r = reset       t = toggle labels'
    print 'f = linear fit  x,1,2,3,4 = delete points'

  if d[2] == '/':
    break

  if d[2] == 'b':
    xmin=float(d[0])
    ymin=float(d[1])
    d=pgband(0)
    xmax=float(d[0])
    ymax=float(d[1])
    plot()

  if d[2] == 'r':
    xmin=min(x)-0.10*(max(z)-min(z))
    ymin=min(y)-0.10*(max(y)-min(y))
    xmax=max(z)+0.10*(max(z)-min(z))
    ymax=max(y)+0.10*(max(y)-min(y))
    label=1
    scale=1.
    plot()

  if d[2] == 's':
    scale=scale*(d[0]*1.5/(xmax-xmin)+0.5-1.5*xmin/(xmax-xmin))
    plot()

  if d[2] == 'x':
    center=(xmax-xmin)/2.+xmin
    xoff=(float(d[0])-center)/(xmax-xmin)
    for tmp in x:
       x[x.index(tmp)]=tmp-xoff

  if d[2] == 'y':
    center=(xmax-xmin)/2.+xmin
    yoff=(float(d[0])-center)/(xmax-xmin)
    for tmp in y:
       y[y.index(tmp)]=tmp-yoff

  if d[2] == 't':
    center=(xmax-xmin)/2.+xmin
    off=(float(d[0])-xmin)/(xmax-xmin)
    for i in range(len(z3)):
      z3[i]=(z2[i]-z1[i])*off+z1[i]

  plot()

