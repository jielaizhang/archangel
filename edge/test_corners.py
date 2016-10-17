#!/usr/bin/env python

import sys
from math import *
import numarray
from ppgplot import *

def perp(m,b,x,y):
  if m != 0.:
    c=y+x/m
    r=(c-b)/(m+1./m)
  else:
    r=x
  s=m*r+b
  d=((r-x)**2+(s-y)**2)**0.5
  if r <= x:
    return d
  else:
    return -d

r=float(sys.argv[1])
s=float(sys.argv[2])
print perp((0.-1.)/(-1.-0.),0.--1.*(0.-1.)/(-1.-0.),r,s)
print perp((-1.-0.)/(0.--1.),-1.-0.*(-1.-0.)/(0.--1.),r,s)
print perp((0.--1.)/(1.-0.),0.-1.*(0.--1.)/(1.-0.),r,s)
print perp((1.-0.)/(0.-1.),1.-0.*(1.-0.)/(1.-0.),r,s)
print perp((0.-1.)/(-1.-0.),0.--1.*(0.-1.)/(-1.-0.),r,s)* \
perp((-1.-0.)/(0.--1.),-1.-0.*(-1.-0.)/(0.--1.),r,s)* \
perp((0.--1.)/(1.-0.),0.-1.*(0.--1.)/(1.-0.),r,s)* \
perp((1.-0.)/(0.-1.),1.-0.*(1.-0.)/(1.-0.),r,s)
