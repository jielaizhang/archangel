#!/usr//bin/env python

import sys,math

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: find_target option ims_file xc yc limit'
  print ' '
  print '       options: -h = this message'
  print '       options: -q = quick look for profile script'
  print '       options: -s = build mark file for skyview'
  print '       options: -p = build a .prf file for iso_prf'
  sys.exit()
else:
  file=open(sys.argv[2],'r')
  nx=float(sys.argv[3])
  ny=float(sys.argv[4])
  if len(sys.argv) > 5: limit=int(sys.argv[5])

test=0.
while 1:
  line=file.readline()
  if not line: break
  area=float(line.split()[2])
  dr=((float(line.split()[0])-nx)**2+(float(line.split()[1])-ny)**2)**0.5
  if area/(dr+0.0001) > test and dr < limit:
    test=area/(dr+0.0001)
    xc=float(line.split()[0])
    yc=float(line.split()[1])
    rstop=(float(line.split()[2])/(math.pi*(1.-float(line.split()[3]))))**0.5
    eps=1.-float(line.split()[3])
    theta=float(line.split()[4])
    out=line[:-1]

if test == 0:
  print 'no target found',test
  sys.exit()

if sys.argv[1] == '-q':
  print '%8.1f' % xc,
  print '%8.1f' % yc,
  print '%8.1f' % rstop,
  print '%8.3f' % eps,
  print '%8.1f' % theta
else:
  print out
