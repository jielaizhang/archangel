#!/usr/bin/env python

import urllib, sys, re

data=[tmp for tmp in open(sys.argv[-1],'r').readlines()]

isw=0
for n,line in enumerate(data):
  if 'Sample' in line:
    break

print re.sub('<.*?>',' ',data[n+1].replace('\n',' ')).split()

#print data[n+1]
#for z in data[n+1]:
#  print z
#  for t in z.split('FONT'):
#    print t
