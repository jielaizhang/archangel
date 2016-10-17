#!/usr/bin/env python

import sys, math

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: convert_to_prf ims_file prf_file\n'
  print ' '
  print 'converts ims format into prf format'
  sys.exit(0)

file=open(sys.argv[1],'r')
out=open(sys.argv[2],'w')

while 1:
  line=file.readline()
  if not line: break
  array=line.split()
  eps=1.-float(array[3])
  area=float(array[2])
  a=(area/(eps*math.pi))**0.5
  print '0. 0. 0.',a,'0. 0. 0. 0. 0. 0. 0. 0.',1.-eps,array[4],array[0],array[1],'0. 0.'
