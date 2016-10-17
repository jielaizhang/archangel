#!/usr/bin/env python

import sys, math

M_sun=4.83 # for V
if '-B' in sys.argv: M_sun=5.48
if '-I' in sys.argv: M_sun=4.08
if '-K' in sys.argv: M_sun=3.27
if '-3.6' in sys.argv: M_sun=3.24

print (206265**2.)*10.**(0.4*(M_sun-float(sys.argv[-1])-5.))
