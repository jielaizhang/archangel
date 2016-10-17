#!/usr/bin/env python

import sys, os
from xml_archangel import *
from numpy import *

if '-h' in sys.argv:
  print 'extract_isophote op file_prefix value'
  print 
  print 'options: -i = closest in intensity to value'
  print '         -r = closest in radius to value'
  sys.exit()

if sys.argv[1] == '-i':
  ii=0
else:
  ii=3

value=float(sys.argv[-1])

doc = minidom.parse(sys.argv[-2].split('.')[0]+'.xml')
rootNode = doc.documentElement
elements=xml_read(rootNode).walk(rootNode)

try:
  for t in elements['array']:
    if t[0]['name'] == 'prf':
      prf=[]
      for z in t[2]['axis']:
        prf.append(map(float,z[1].split('\n')))
      tmp=array(prf)
      prf=swapaxes(tmp,1,0)
      break
  else:
    print 'no prf data in .xml file - aborting'
    sys.exit()
except:
  raise
  print 'problem with data in .xml file - aborting'
  sys.exit()

rmin=1.e33
for n,t in enumerate(prf):
  if abs(t[ii]-value) <= rmin:
    rmin=abs(t[ii]-value)
    imin=n
for t in prf[imin]: print t,
print
