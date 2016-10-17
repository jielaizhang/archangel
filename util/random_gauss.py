#!/usr/bin/env python

from math import *
import random

#for i in range(10000):
#  x=random.random()*2.-1.
#  y=random.random()*2.-1.
#  rds=x*x+y*y
#  c=sqrt(-2.*log(rds)/rds)
#  print x*c

for i in range(10000):
  x=random.random()
  y=random.random()
  c=(sqrt(-2.*log(x)))*(cos(2.*pi*y))
  print i,c
