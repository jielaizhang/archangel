#!/usr/bin/env python

import sys

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if sys.argv[1] == '-h':
  print 'linear interpolation, x1,x2,y1,y2,z1 -> z2'
  print '-m gives slope and y intercept'
  sys.exit()

if '-m' in sys.argv:
  x1=float(sys.argv[-4])
  x2=float(sys.argv[-3])
  y1=float(sys.argv[-2])
  y2=float(sys.argv[-1])
  print 'm =',(y2-y1)/(x2-x1),' ; b =',y1-x1*(y2-y1)/(x2-x1)
else:
  print interp(float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]))
