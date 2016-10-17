#!/usr/bin/env python

import sys, math

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: is_pixel_inside xc yc area eps theta x1 y1'
  sys.exit()

if len(sys.argv) < 7:
  print 'insufficient numbers'
  sys.exit()

eps=1.-float(sys.argv[4])
area=float(sys.argv[3])
a=(area/(eps*math.pi))**0.5
b=eps*a
a=a*a
b=b*b
d=-float(sys.argv[5])*math.pi/180.
x=float(sys.argv[1])-float(sys.argv[6])
y=float(sys.argv[2])-float(sys.argv[7])
if x != 0:
  t=math.atan(y/x)
else:
  t=math.pi/2.
c1=b*math.cos(t)*math.cos(t)+a*math.sin(t)*math.sin(t)
c2=(a-b)*2.*math.sin(t)*math.cos(t)
c3=b*math.sin(t)*math.sin(t)+a*math.cos(t)*math.cos(t)
c4=a*b
rr=(c4/(c1*math.cos(d)*math.cos(d)+c2*math.sin(d)*math.cos(d)+c3*math.sin(d)*math.sin(d)))**0.5
print (x*x+y*y)**0.5,rr

