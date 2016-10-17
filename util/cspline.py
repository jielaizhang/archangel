#!/usr/bin/env python

# takes a .ept file and does a cubic spline

import sys,os
from math import *
from pylab import *

"""
Cubic spline approximation class.

Last Modified 9/9/97 by Johann Hibschman <johann@physics.berkeley.edu>

To create a default ("natural") spline, simply use sp = Spline(x,y).
To specify the slope of the function at either of the endpoints,
use the "low_slope" and "high_slope" keywords.

Example usage:
>>> x = arange(10, typecode=Float) * 0.3
>>> y = cos(x)
>>> sp = Spline(x, y)
>>> print sp(0.5), cos(0.5)
0.878364380585 0.87758256189

Uses "searchsorted" from the Numeric module, aka "binarysearch" in older
versions.

"""

import func
#from Numeric import *
import numpy as Numeric
from numpy import *

BadInput = "Bad xa input to routine splint."

class Spline(func.FuncOps):
    def __init__(self, x_array, y_array, low_slope=None, high_slope=None):
	self.x_vals = x_array
	self.y_vals = y_array
	self.low_slope  = low_slope
	self.high_slope = high_slope
	# must be careful, so that a slope of 0 still works...
	if low_slope is not None:
	    self.use_low_slope  = 1
	else:
	    self.use_low_slope  = 0   # i.e. false
	if high_slope is not None:
	    self.use_high_slope = 1
	else:
	    self.use_high_slope = 0
	self.calc_ypp()
   
    def calc_ypp(self):
	x_vals = self.x_vals
	y_vals = self.y_vals
	n = len(x_vals)
	y2_vals  = zeros(n, float)
	u        = zeros(n-1, float)
	
	if self.use_low_slope:
	    u[0] = (3.0/(x_vals[1]-x_vals[0])) * \
		   ((y_vals[1]-y_vals[0])/
		    (x_vals[1]-x_vals[0])-self.low_slope)
	    y2_vals[0] = -0.5
	else:
	    u[0] = 0.0
	    y2_vals[0] = 0.0   # natural spline
	    
	for i in range(1, n-1):
	    sig = (x_vals[i]-x_vals[i-1]) / \
		  (x_vals[i+1]-x_vals[i-1])
	    p   = sig*y2_vals[i-1]+2.0
	    y2_vals[i] = (sig-1.0)/p
	    u[i] = (y_vals[i+1]-y_vals[i]) / \
		   (x_vals[i+1]-x_vals[i]) - \
		   (y_vals[i]-y_vals[i-1])/ \
		   (x_vals[i]-x_vals[i-1])
	    u[i] = (6.0*u[i]/(x_vals[i+1]-x_vals[i-1]) - 
		    sig*u[i-1]) / p
	    
	if self.use_high_slope:
	    qn = 0.5
	    un = (3.0/(x_vals[n-1]-x_vals[n-2])) * \
		 (self.high_slope - (y_vals[n-1]-y_vals[n-2]) /
		  (x_vals[n-1]-x_vals[n-2]))
	else:
	    qn = 0.0
	    un = 0.0    # natural spline
      
	y2_vals[n-1] = (un-qn*u[n-2])/(qn*y2_vals[n-1]+1.0)

	rng = range(n-1)
	rng.reverse()
	for k in rng:         # backsubstitution step
	    y2_vals[k] = y2_vals[k]*y2_vals[k+1]+u[k]
	self.y2_vals = y2_vals
      
      
    # compute approximation
    def __call__(self, arg):
	"Simulate a ufunc; handle being called on an array."
	if type(arg) == func.ArrayType:
	    return func.array_map(self.call, arg)
	else:
	    return self.call(arg)

    def call(self, x):
	"Evaluate the spline, assuming x is a scalar."

	# if out of range, return endpoint
	if x <= self.x_vals[0]:
	    return self.y_vals[0]
	if x >= self.x_vals[-1]:
	    return self.y_vals[-1]

	pos = searchsorted(self.x_vals, x)
      
	h = self.x_vals[pos]-self.x_vals[pos-1]
	if h == 0.0:
	    raise BadInput
      
	a = (self.x_vals[pos] - x) / h
	b = (x - self.x_vals[pos-1]) / h
	return (a*self.y_vals[pos-1] + b*self.y_vals[pos] + \
		((a*a*a - a)*self.y2_vals[pos-1] + \
		 (b*b*b - b)*self.y2_vals[pos]) * h*h/6.0)


class LinInt(func.FuncOps):
    def __init__(self, x_array, y_array):
	self.x_vals = x_array
	self.y_vals = y_array
      
    # compute approximation
    def __call__(self, arg):
	"Simulate a ufunc; handle being called on an array."
	if type(arg) == func.ArrayType:
	    return func.array_map(self.call, arg)
	else:
	    return self.call(arg)

    def call(self, x):
	"Evaluate the interpolant, assuming x is a scalar."

	# if out of range, return endpoint
	if x <= self.x_vals[0]:
	    return self.y_vals[0]
	if x >= self.x_vals[-1]:
	    return self.y_vals[-1]

	pos = searchsorted(self.x_vals, x)
      
	h = self.x_vals[pos]-self.x_vals[pos-1]
	if h == 0.0:
	    raise BadInput
      
	a = (self.x_vals[pos] - x) / h
	b = (x - self.x_vals[pos-1]) / h
	return a*self.y_vals[pos-1] + b*self.y_vals[pos]

def spline_interpolate(x1, y1, x2):
    """
    Given a function at a set of points (x1, y1), interpolate to
    evaluate it at points x2.
    """
    sp = Spline(x1, y1)
    return sp(x2)

def logspline_interpolate(x1, y1, x2):
    """
    Given a function at a set of points (x1, y1), interpolate to
    evaluate it at points x2.
    """
    sp = Spline(log(x1), log(y1))
    return exp(sp(log(x2)))


def linear_interpolate(x1, y1, x2):
    """
    Given a function at a set of points (x1, y1), interpolate to
    evaluate it at points x2.
    """
    li = LinInt(x1, y1)
    return li(x2)

def linfit(fit):
  sum=0.0
  sumx=0.0
  sumy=0.0
  sumxy=0.0
  sumx2=0.0
  sumy2=0.0
  n=0
  for tmp in fit:
    n+=1
    sum=sum+(1./tmp[2]**2)
    sumx=sumx+(1./tmp[2]**2)*tmp[0]
    sumy=sumy+(1./tmp[2]**2)*tmp[1]
    sumxy=sumxy+(1./tmp[2]**2)*tmp[0]*tmp[1]
    sumx2=sumx2+(1./tmp[2]**2)*tmp[0]*tmp[0]
    sumy2=sumy2+(1./tmp[2]**2)*tmp[1]*tmp[1]
  dex=sum*sumx2-sumx*sumx
# y intersect -- a
  a=(sumx2*sumy-sumx*sumxy)/dex
# slope -- b
  b=(sum*sumxy-sumx*sumy)/dex
# varience
  var=(sumy2+a*a*sum+b*b*sumx2-2.*(a*sumy+b*sumxy-a*b*sumx))/(n-2)
# correlation coefficient -- r
  r=(sum*sumxy-sumx*sumy)/((dex*(sum*sumy2-sumy*sumy))**0.5)
# sigma b
  sigb=(var*sumx2/dex)**0.5
# sigma m
  sigm=(var*sum/dex)**0.5
  sig=0.
  for tmp in fit:
    z=a+b*tmp[0]
    sig=sig+(z-tmp[1])**2
  sig=(sig/(n-1))**.5
  return a,b,r,sigb,sigm,sig

#main

file=open(sys.argv[-1],'r')
x=[] ; y=[]
while 1:
  line=file.readline()
  if not line: break
  x.append(float(line.split()[0]))
  y.append(float(line.split()[1]))
file.close()

sp=Spline(x,y)

print sp(0.),sp(0.5),sp(1.)
#for r in arange(x[0],x[-1],(x[-1]-x[0])/100.):
#  print r,sp(r)

#print '20.',sp(20.)
#print x[-7],sp(x[-7])
print x[-2],sp(x[-2])
#print x[-1],sp(x[-1])
#print x[-1]*10.,sp(x[-1]*10.)
#print x[-1]*100.,sp(x[-1]*100.)
#print x[-1]*1000.,sp(x[-1]*1000.)

#for u,v in zip(x,y):
#  print u,v
