#!/usr/bin/env python

import sys

# take a list of x and y's, find the middle x, interpolate the y

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if sys.argv[1] == '-h':
  print 'linear interpolation, file of x&y and x_o, output y_o'
  sys.exit()

d={}
junk=[d.update({float(tmp.split()[0]):float(tmp.split()[-1])}) for tmp in open(sys.argv[-2],'r').readlines()]
xo=float(sys.argv[-1])

x=d.keys()
x.sort()

for t in x:
  if t > xo:
    print interp(lastx,t,lasty,d[t],xo)
    break
  lastx=t ; lasty=d[t]
