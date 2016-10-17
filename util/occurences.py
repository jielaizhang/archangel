#!/usr/bin/env python

import sys

if sys.argv[1] == '-h':
  print 'occurances search_string/file input_file'
  sys.exit()

lines=[tmp for tmp in open(sys.argv[-1],'r').readlines()]

if '-f' in sys.argv:
  strng=[tmp[:-1] for tmp in open(sys.argv[-2],'r').readlines()]
else:
  strng=[sys.argv[-2]]

for match in strng:
  n=0
  for line in lines:
    if match in line: n=n+1
  print match,n
