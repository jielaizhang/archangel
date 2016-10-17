#!/usr/bin/env python

import sys, math

file=open(sys.argv[1]+'.sfb','r')
line=file.readline().split()
file.close()
sstore=1.0857/float(line[1])
cstore=float(line[0])
file=open(sys.argv[1]+'.cal','r')
line=file.readline().split()
file.close()
scale=float(line[0])
zpt=float(line[1])
file=open(sys.argv[1]+'.sky','r')
line=file.readline().split()
file.close()
sky=float(line[0])
file=open(sys.argv[1]+'.prf','r')
print cstore,sstore,scale,zpt
while 1:
  line=file.readline()
  if not line: break
  r=float(line.split()[3])
  xint=r*scale*sstore+cstore
  i=scale*scale*(10.**((xint-zpt)/-2.5))+sky
#  print '%6.2f' % math.log10(r),
  print '%6.2f' % (r),
  print '%6.2f' % float(line.split()[0]),
  print '%6.2f' % i
