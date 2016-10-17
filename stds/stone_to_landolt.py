#!/usr/bin/env python

import sys

junk=[tmp.split() for tmp in open(sys.argv[-1],'r').readlines()]
stone={}
for z in junk[:-1]:
  stone[z[0]]=float(z[1])

file=open('/Users/js/stds/landolt.new','r')
while 1:
  line=file.readline()
  if not line: break
  name=line[:12].rstrip().replace(' ','_').replace('RU','Rubin')
  if name in stone.keys():
    print line[13:].split()[4],stone[name],name
