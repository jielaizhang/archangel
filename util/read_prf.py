#!/usr/bin/env python

import sys,os,math

if len(sys.argv) < 3 or sys.argv[1] == '-h':
  print 'Usage: read_prf options file_name'
  print ' '
  print 'options: -p = print only photometric values'
  print '         n,m = print columns n,m'
  sys.exit(0)

file=open(sys.argv[-1],'r')

while 1:
  data=file.readline().split()
  if not data: break
  if sys.argv[1] == '-p':
    print '%9.2f' % float(data[0]),
    print '%7.2f' % float(data[3]),
    print '%6.0i' % int(float(data[6])),
    print '%6.0i' % int(float(data[7])),
    print '%6.3f' % float(data[12]),
    print '%7.1f' % float(data[13]),
    print '%6.1f' % float(data[14]),
    print '%6.1f' % float(data[15])
  else:
    for x in sys.argv[1].split(','):
      print data[int(x)],
    print
