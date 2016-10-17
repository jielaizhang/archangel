#!/usr/bin/env python

import sys

def interp(x1,x2,y1,y2,z1):
  return y1+(z1-x1)*(y2-y1)/(x2-x1)

if sys.argv[1] == '-h':
  print 'interpolation file #2 into x values from file #1'
  print 'output matches file #2 x values'
  sys.exit()

data1=[(map(float, tmp.split())) for tmp in open(sys.argv[-2],'r').readlines()]
data2=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()]

last_r=data2[0][0]
last_s=data2[0][1]
for t1 in data1:
  for t2 in data2[1:]:
    if t2[0] > t1[0]:
      print t1[0],interp(t2[0],last_r,t2[1],last_s,t1[0])
      break
    last_r=t2[0]
    last_s=t2[1]
