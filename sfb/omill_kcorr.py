#!/usr/bin/env python

import sys, os
from math import *

# O'Mill etal 2010

# k_filter = [aA*(g-r)+bA]*z + [aB*(g-r)+bB]
#    aA    saA    bA    sbA    aB    saB    bB    sbB
# u 2.956 0.070 -0.100 0.034 -0.299 0.009 -0.095 0.004
# g 3.070 0.165 0.727 0.117 -0.313 0.021 -0.173 0.015
# r 1.771 0.032 -0.529 0.023 -0.179 0.005 -0.048 0.003
# i 0.538 0.085 -0.075 0.079 -0.027 0.013 -0.120 0.012
# z 0.610 0.045 -0.064 0.034 -0.061 0.007 -0.106 0.005


coeff={'u':[2.956,-0.100,-0.299,-0.095], \
       'g':[3.070,+0.727,-0.313,-0.173], \
       'r':[1.771,-0.529,-0.179,-0.048], \
       'i':[0.538,-0.075,-0.027,-0.120], \
       'z':[0.610,-0.064,-0.061,-0.106]}

filter=sys.argv[-3]
color=float(sys.argv[-2])
redshift=float(sys.argv[-1])

k=(coeff[filter][0]*color+coeff[filter][1])*redshift+(coeff[filter][2]*color+coeff[filter][3])
if k < 0.: k=0.

print redshift,k
