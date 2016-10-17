#!/usr/bin/env python

import os, sys


file=open(sys.argv[-1],'r')
lines=file.readlines()
print lines
for line in lines:
  for z in line:
    if z in ['\xe2','\x88','\x92']:
      if z == '\xe2':
        z='-'
      else:
        z=''
    sys.stdout.write(z)
