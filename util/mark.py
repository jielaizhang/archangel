#!/usr/bin/env python

import sys, math

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: mark data_file'
  print
  print 'ouput skyview mark file from .ims or .prf files'
  print
  print 'options:  -h = this message'
  sys.exit(0)

try:
  file=open(sys.argv[1],'r')
except:
  print sys.argv[1],'file not found -- aborting'
  sys.exit(0)

array=file.readline().split()
if not (len(array) == 18 or len(array) == 6):
  print 'file format unknown -- aborting'
  sys.exit(0)

if len(array) == 18:
  while 1:
    print 'mark ',float(array[14]),float(array[15]),
    print ' el blue ',('%1.2f' % (2.*float(array[3]))),
    print '%1.2f' % (2.*float(array[3])*(1.-float(array[12]))),
    print '%1.1f' % float(array[13])
    array=file.readline().split()
    if not array: break

else:
  while 1:
    print 'mark ',float(array[0]),float(array[1]),
    print ' el blue ',
# note that this is semi-major axis, i.e. 2*radius a and b
# a and b from area, which is 1/2 normal definitions, so when
# a=b it is a circle
    eps=1.-float(array[3])
    if eps == 0: eps=0.001
    area=float(array[2])
    a=2.*(area/(eps*math.pi))**0.5
    b=eps*a
    print '%1.2f' % a,
    print '%1.2f' % b,
    print '%1.1f' % float(array[4])
    array=file.readline().split()
    if not array: break
