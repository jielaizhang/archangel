#!/usr/bin/env python

import sys

if __name__ == '__main__':

  if '-h' in sys.argv:
    print './polydump filename coefficients'
    print
    print 'take file of numbers and applies fit to them'
    sys.exit()

  data=[(map(float, tmp.split())) for tmp in open(sys.argv[1],'r').readlines()]

  a=[]
  for z in sys.argv[2:]:
    a.append(float(z))

  for t in data:
    print t[0],
    out=0.
    for n,r in enumerate(a):
       out=out+r*t[0]**(len(a)-n-1)
    print out
