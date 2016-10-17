#!/usr/bin/env python

import sys, os

if sys.argv[-1] == '-h':
  print '-l = do landolt, -s = do stone'
  sys.exit()

stars=[tmp.split() for tmp in open('out.tmp','r').readlines()]
names={}
for z in stars:
  names[z[0]]=' '.join(z)
if sys.argv[1] == '-l':
  file=open('/Users/js/stds/landolt.std_phot','r')
else:
  file=open('/Users/js/stds/stone.std_phot','r')
while 1:
  line=file.readline()
  if not line: break
  if line.split()[0] in names.keys():
    print names[line.split()[0]]
  else:
    print line,
