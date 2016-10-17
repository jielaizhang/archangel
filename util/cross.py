#!/usr/bin/env python

import sys, os

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print ' '
  print 'Usage: cross rmin file1 file2'
  print ' '
  print 'cross x and y coords'
  sys.exit()

data1=[(map(float, tmp.split())) for tmp in open(sys.argv[-2],'r').readlines()]
data2=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()]
rmin=float(sys.argv[-3])

for z1 in data1:
  rm=rmin
  for z2 in data2:
    rr=((z1[0]-z2[0])**2.+(z1[1]-z2[1])**2.)**0.5
    if rr < rm:
      hold=z1+z2
      rm=rr
  if rm < rmin:
    for z in hold:
      print str(z),
    print
