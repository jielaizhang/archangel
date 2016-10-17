#!/usr/bin/env python

import os, time, sys

out=open('out.tmp','w')
file=open(sys.argv[-1],'r')
while 1:
  time.sleep(1)
  line=file.readline()
  if not line: break
  tmp=os.popen('./query_sdss.py '+line.split()[1]+' '+line.split()[2]).read()
  print tmp
  max_mag=99.
  for z in tmp.split('\n'):
    if 'No object' in z: break
    if 'objid' in z or len(z) == 0: continue
    if max_mag > float(z.split(',')[2]):
      max_mag=float(z.split(',')[2])
      sdss=map(float,z.split(',')[1:-1])

  if 'No object' not in z:
    print >> out,line[:-1],
    for z in sdss:
      print >> out,'%5.2f' % z,
    print >> out
