#!/usr/bin/env python

import sys
from math import *

if sys.argv[1] == '-h':
  print './std.py op filter raw_mag_file'
  print 'if op = -s use Stone stds'
  sys.exit()

k={'U':0.30,'B':0.20,'V':0.14,'R':0.10,'I':0.05,'1563':0.10,'1564':0.10,'1565':0.10,'1566':0.10,'1391':0.10,'1494':0.10}

filter=sys.argv[-2]

if sys.argv[1] == '-s':
  file=open(filter+'.stone','r')
else:
  file=open(filter+'.stds','r')
stds={}
while 1:
  line=file.readline()
  if not line: break
  stds[line.split()[0]]=[float(line.split()[1]),float(line.split()[-1])]
file.close()

file=open(sys.argv[-1],'r')
while 1:
  line=file.readline()
  if not line: break
  std=line.split()[0]
  directory=line.split()[-1].split('/')[-2]
  try:
    stds[std]
  except:
    continue
  fil=line.split()[1]
  if fil != filter: continue
  xmag=10.**(float(line.split()[7])/-2.5)
  exptime=float(line.split()[2])
  airmass=float(line.split()[3])
  cons=-2.5*log10(xmag/exptime)-k[fil]*airmass
  if sys.argv[1] == '-k':
    print airmass,stds[std][0]+2.5*log10(xmag/exptime),std
  elif sys.argv[1] == '-x':
    print stds[std][0]-cons,std
  else:
    print '%7.3f' % cons,stds[std][0],std+'_'+directory
