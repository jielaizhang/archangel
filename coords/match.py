#!/usr/bin/env python

import sys, os

if '-h' in sys.argv:
  print '''
Usage: match option master_coord transform_file

takes maste ims file and matchs transform file, outputs master or transform

options: -1 = shift transform to master coords
         -2 = shift master to transform coords
'''

scan1=[(map(float, tmp.split())) for tmp in open(sys.argv[-2],'r').readlines()]
scan2=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()]

for t in scan1:
  rmin=1.e33
  for z in scan2:
    dr=((z[0]-t[0])**2+(z[1]-t[1])**2)**0.5
    if dr/z[2] < rmin:
      rmin=dr/z[2]
      hold=z
  print '%7.1f%7.1f' % (hold[0],hold[1]),
  print '%8.0f%7.3f%7.1f%11.4f' % tuple(t[2:]),
  print
