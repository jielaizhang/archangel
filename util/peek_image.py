#!/usr/bin/env python

import pyfits,sys

if len(sys.argv) == 1 or sys.argv[1] == '-h':
  print 'Usage: peek data_file x y range'
  print ' '
  print 'examine the raw pixels in data_file'
  print ' '
  print 'Options: -h = this mesage'
  sys.exit()

fitsobj=pyfits.open(sys.argv[1],"readonly")
pix=fitsobj[0].data

nx=pix.shape[0]
ny=pix.shape[1]
x=int(sys.argv[2])
y=int(sys.argv[3])
rr=int(sys.argv[-1])
if rr == y:
  rr=5

if rr > 1:
  print '    ',
  for i in xrange(x-rr,x+rr-1): print '%7.1i' % (i+1),
  print ' '
  for j in xrange(y-rr,y+rr-1):
    print '%5.1i' % (j+1),
    for i in xrange(x-rr,x+rr-1):
      print '%7.1f' % pix[j,i],
    print ' '

else:
  print pix[y][x]
