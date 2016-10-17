#!/usr/bin/env python

import sys, numpy
from math import *

def airy(x,a):
  return a[0]*exp(-0.5*((x-a[1])**2)/a[2]**2)

if __name__ == '__main__':

  if '-h' in sys.argv:
    print 'gauss_make height, center, sigma'
    sys.exit()

  a=[float(sys.argv[-3]),float(sys.argv[-2]),float(sys.argv[-1])]
  for x in numpy.arange(-5.*a[2],5.*a[2],10.*a[2]/100.):
    print x,airy(x,a)
