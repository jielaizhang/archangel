#!/usr/bin/env python

import sys
#try:
#  import numpy.numarray as numarray
#except:
#  import numarray
import numarray

# strings
data=[tmp for tmp in open(sys.argv[-1],'r').readlines()]
print 'strings',data

# strings, leave off \n
data=[tmp[:-1] for tmp in open(sys.argv[-1],'r').readlines()]
print 'strings',data

# broken strings
data=[tmp.split() for tmp in open(sys.argv[-1],'r').readlines()]
print 'broken strings',data

# floats
data=[(map(float, tmp.split())) for tmp in open(sys.argv[-1],'r').readlines()]
print 'floats',data
for x in data:
  print 'x',x
  xs=numarray.array(x)
  print 'numarray',xs
  print 'print',
  for y in x: print y,
  print

# individual strings
data=[(tmp.split()[0],tmp.split()[4]) for tmp in open(sys.argv[-1],'r').readlines()]
print 'individual strings',data

data=[map(float,(tmp.split()[0],tmp.split()[4])) for tmp in open(sys.argv[-1],'r').readlines()]
print 'individual floats',data

# make a dictionary, junk is empty

d={}
junk=[d.update({tmp.split()[0]:tmp.split()[-1]}) for tmp in open(sys.argv[-1],'r').readlines()]

