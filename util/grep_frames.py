#!/usr/bin/env python

import os, sys

if 'k0308' in sys.argv:
  filters={1:'U',2:'B',3:'V',4:'1495',5:'1566',6:'1565',7:'1564',8:'1563'}
if 'k0309' in sys.argv:
  filters={1:'V',2:'B',3:'1563',4:'1564',5:'1565',6:'1566'}
if 'k1007' in sys.argv:
  filters={1:'1566',2:'R',3:'1494',4:'1495',5:'V',6:'B',7:'1563',8:'1391'}

tmp=os.popen('ls *.fits').read()

files=tmp.split('\n')[:-1]
for file in files:
  tmp=os.popen('keys -p '+file).read()
  print file.ljust(25),
  for z in tmp.split('\n'):
    if 'OBJECT' in z: print z.split('\'')[1].ljust(20),
#    if 'TELFILTE' in z: print filters[int(z.split('\'')[1])].ljust(5),
    if 'FILTERS' in z: print filters[int(z.split('\'')[1])].ljust(5),
    if 'EXPTIME' in z: print str(int(float(z.split()[2]))).ljust(5),
  print
